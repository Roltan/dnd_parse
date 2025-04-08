import mysql.connector
from slugify import slugify
from tools.loging import log_error

# для записи данных в бд вызываем метод insert
# передаём двумерный массив, где каждый вложенный массив это одна запись в бд
# 0 - sub_category_id
# 1 - name
# 2 - options
# 3 - input
# 4 - isFilter

class Output:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None

    def connect(self):
        self.connection = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
        self.cursor = self.connection.cursor()

    def disconnect(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def create_table(self, table_name, columns):
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS `{table_name}` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `sub_category_id` bigint UNSIGNED NOT NULL,
            `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
            `options` text COLLATE utf8mb4_unicode_ci,
            `paragraph` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'Параметры',
            `alias` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
            `input` json NOT NULL,
            `isFilter` tinyint(1) NOT NULL DEFAULT '1',
            `filter` json DEFAULT NULL,
            `vis` tinyint(1) NOT NULL DEFAULT '1'
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        self.cursor.execute(create_table_query)

    def get_max_id(self, table_name):
        self.cursor.execute(f"SELECT MAX(id) FROM `{table_name}`")
        max_id = self.cursor.fetchone()[0]
        return max_id if max_id is not None else 0

    def prepare_data(self, row):
        name = row[1]
        alias = 'atr_'+slugify(name)
        paragraph = 'Параметры'
        # filter = row[3] if row[4] == 1 else None
        vis = 1
        return row + [alias, paragraph, vis]

    def insert_data(self, table_name, columns, data, max_id):
        insert_query = f"INSERT INTO `{table_name}` (`id`, {', '.join(columns)}) VALUES (%s, {', '.join(['%s'] * len(columns))});"
        for row in data:
            max_id += 1
            prepared_row = self.prepare_data(row)
            self.cursor.execute(insert_query, [max_id] + prepared_row)

    def validate_data(self, data, columns):
        if isinstance(data[0], dict):
            # Если данные переданы в виде массива ключ-значение
            required_keys = set(columns)
            for row in data:
                if not required_keys.issubset(row.keys()):
                    missing_keys = required_keys - set(row.keys())
                    error = f"В строке {row} отсутствуют ключи: {', '.join(missing_keys)}"
                    log_error(error)
                    raise ValueError(error)
            # Преобразуем массив ключ-значение в обычный массив
            data = [[row[col] for col in columns] for row in data]
        else:
            # Если данные переданы в виде обычного массива
            expected_length = len(columns)
            for row in data:
                if len(row) != expected_length:
                    error = f"Длина вложенного массива {row} не соответствует количеству полей {expected_length}"
                    log_error(error)
        return data

    def insert(self, data, table_name='attributes', columns=['sub_category_id', 'name', 'options', 'input', 'isFilter', 'filter']):
        # Создаем копию списка columns, чтобы изменения не влияли на оригинальный список
        columns_copy = columns[:]

        # Проверка данных
        data = self.validate_data(data, columns_copy)
            
        # Добавляем фиксированные поля в список столбцов
        columns_copy.extend(['alias', 'paragraph', 'vis'])

        # Подключение к базе данных
        self.connect()

        try:
            # Создание таблицы
            self.create_table(table_name, columns_copy)

            # Получение максимального значения id
            max_id = self.get_max_id(table_name)

            # Вставка данных
            self.insert_data(table_name, columns_copy, data, max_id)

            # Фиксация изменений
            self.connection.commit()
        except mysql.connector.Error as err:
            error = f"Ошибка при записи данных в базу данных: {err}"
            log_error(error)
        finally:
            # Закрытие соединения
            self.disconnect()
