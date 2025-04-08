import sys
import os

# Добавляем корневую папку проекта в sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import re
from tools.loging import log_error

class ReadSQL:
    def __init__(self, file_path, table_name):
        self.table_name = table_name
        self.columns = self._extract_columns_from_create_table(file_path)
        self.all_values_lines = self._find_replace_into(file_path)

    def _extract_columns_from_create_table(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            sql_content = file.read()

        # Регулярное выражение для поиска запроса CREATE TABLE
        create_table_pattern = re.compile(rf'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?`{self.table_name}`\s*\((.*?)\)\s*[^)]*?;', re.IGNORECASE | re.DOTALL)
        match = create_table_pattern.search(sql_content)

        if match:
            # Регулярное выражение для поиска всех столбцов в запросе CREATE TABLE
            columns_pattern = re.compile(r"(?:,|^)\s*`(\w+)`(?!\))", re.DOTALL)
            columns = columns_pattern.findall(match.group(1))
            return columns
        else:
            error = f"Запрос CREATE TABLE для таблицы `{self.table_name}` не найден."
            log_error(error)

    def _find_replace_into(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            sql_content = file.read()

        # Регулярное выражение для поиска команд INSERT INTO и REPLACE INTO
        insert_pattern = re.compile(rf'INSERT INTO\s+`{self.table_name}`\s*(?:\((.*?)\)\s*)?VALUES\s*(.*?);', re.IGNORECASE | re.DOTALL)
        replace_pattern = re.compile(rf'REPLACE INTO\s+`{self.table_name}`\s*(?:\((.*?)\)\s*)?VALUES\s*(.*?);', re.IGNORECASE | re.DOTALL)

        # Поиск всех команд INSERT INTO и REPLACE INTO
        insert_matches = insert_pattern.findall(sql_content)
        replace_matches = replace_pattern.findall(sql_content)

        # Собираем данные из разных запросов в один массив
        all_values_lines = []
        for match in insert_matches:
            values_lines = re.findall(r'\((.*?)\)', match[1])  # Ищем все строки с данными
            all_values_lines.extend(values_lines)
        for match in replace_matches:
            values_lines = re.findall(r'\((.*?)\)', match[1])  # Ищем все строки с данными
            all_values_lines.extend(values_lines)

        return all_values_lines
    
    def _parse_values_line(self, values_line):
        values = re.split(r',\s*(?![^()]*\))', values_line)  # Разделение с учетом скобок
        return {column: value.strip("'") for column, value in zip(self.columns, values)}
    
    # получение массива данных в строке таблицы из файла
    # row_index - порядковый номер строки в которой ищем
    def extract(self, row_index):
        if len(self.all_values_lines) > row_index:
            values_line = self.all_values_lines[row_index].strip().strip('()')
            return self._parse_values_line(values_line)
        error = f"в таблице {self.table_name} нет строки {row_index}, к которой вы хотите получить доступ"
        log_error(error)

    # получение количества строк в таблице
    def count(self):
        return len(self.all_values_lines)

    # получить массива данных в строке таблицы по id
    # record_id - id по которому ищем
    def find(self, record_id):
        for values_line in self.all_values_lines:
            values_line = values_line.strip().strip('()')
            values = self._parse_values_line(values_line)
            if values[self.columns[0]] == str(record_id):
                return values
        error = f"в таблице {self.table_name} нет строки с id {record_id}, к которой вы хотите получить доступ"
        log_error(error)
    
    # метод для фильтрации строк по значению столбца
    # column_name - название колонки по которой сравниваем
    # value - искомое значение колонки
    def where(self, column_name, value):
        filtered_rows = []
        for values_line in self.all_values_lines:
            values_line = values_line.strip().strip('()')
            values = self._parse_values_line(values_line)
            if values.get(column_name) == str(value):
                filtered_rows.append(values)
        return filtered_rows
    