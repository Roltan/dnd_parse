import os
import mysql.connector
from mysql.connector import errorcode
from slugify import slugify
from dotenv import load_dotenv
from tools.loging import log_error

# Загрузка переменных окружения
load_dotenv()

class Output:
    def __init__(self, host=None, user=None, password=None, database=None, table_creation_sql=None):
        # Параметры подключения из .env по умолчанию
        self.host = host or os.getenv('DB_HOST')
        self.user = user or os.getenv('DB_USER')
        self.password = password or os.getenv('DB_PASSWORD')
        self.database = database or os.getenv('DB_NAME')
        self.table_creation_sql = table_creation_sql
        self.connection = None
        self.cursor = None

    def connect(self):
        """Установка соединения с базой данных"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                autocommit=False
            )
            self.cursor = self.connection.cursor(dictionary=True)
        except mysql.connector.Error as err:
            self.handle_database_error(err)

    def disconnect(self):
        """Закрытие соединения с базой данных"""
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection and self.connection.is_connected():
                self.connection.close()
        except mysql.connector.Error as err:
            log_error(f"Ошибка при закрытии соединения: {err}")

    def create_table(self, creation_sql=None):
        """Создание таблицы по указанному SQL-запросу"""
        try:
            sql = creation_sql or self.table_creation_sql
            if not sql:
                raise ValueError("Не указан SQL-запрос для создания таблицы")
            
            self.cursor.execute(sql)
            self.connection.commit()
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                log_error("Таблица уже существует")
            else:
                self.handle_database_error(err)

    def insert(self, data, table_name, columns, batch_size=100):
        """
        Универсальный метод для вставки данных
        :param data: Список словарей или список списков
        :param table_name: Имя таблицы
        :param columns: Список колонок для вставки
        :param batch_size: Размер пачки для вставки
        """
        self.connect()
        try:
            # Валидация данных
            validated_data = self.validate_data(data, columns)
            
            # Формирование SQL-запроса
            placeholders = ', '.join(['%s'] * len(columns))
            query = f"INSERT INTO `{table_name}` ({', '.join(columns)}) VALUES ({placeholders})"
            
            # Пакетная вставка
            for i in range(0, len(validated_data), batch_size):
                batch = validated_data[i:i + batch_size]
                self.cursor.executemany(query, batch)
                self.connection.commit()
                
        except Exception as e:
            self.connection.rollback()
            log_error(f"Ошибка при вставке данных: {str(e)}")
            raise
        finally:
            self.disconnect()

    def validate_data(self, data, expected_columns):
        """Валидация и преобразование данных"""
        validated = []
        
        if isinstance(data, dict):
            data = [data]
            
        for item in data:
            # Преобразование словаря в список значений
            if isinstance(item, dict):
                if not all(key in item for key in expected_columns):
                    missing = set(expected_columns) - set(item.keys())
                    raise ValueError(f"Отсутствуют ключи: {', '.join(missing)}")
                validated.append([item[col] for col in expected_columns])
                
            # Проверка списка значений
            elif isinstance(item, (list, tuple)):
                if len(item) != len(expected_columns):
                    raise ValueError("Несоответствие количества колонок и данных")
                validated.append(item)
                
            else:
                raise TypeError("Неподдерживаемый формат данных")
                
        return validated

    def handle_database_error(self, error):
        """Обработка ошибок базы данных"""
        error_msg = f"Database error [{error.errno}]: {error.msg}"
        log_error(error_msg)
        raise mysql.connector.Error(error_msg)