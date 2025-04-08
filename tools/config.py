import os
import json
from configparser import ConfigParser
from dotenv import load_dotenv

class AppConfig:
    PARSER_TYPES = {
        'sql': 'SQL-парсер',
        'www': 'Веб-парсер',
    }

    def __init__(self, config_path='config.ini'):
        load_dotenv()
        self.config = ConfigParser()
        self.config.read(config_path)
        
        # Настройки путей
        self.table_directory = self._get_path('paths', 'table_directory', 'parsers')
        self.files_to_run = self._get_json('paths', 'files_to_run', [])
        
        # Настройки парсеров
        self.default_type = self._validate_parser_type(
            self.config.get('parser', 'default_type', fallback='sql')
        )
        
        # Настройки БД
        self.db_config = {
            'host': self._get_env_var('database', 'host'),
            'user': self._get_env_var('database', 'user'),
            'password': self._get_env_var('database', 'password'),
            'database': self._get_env_var('database', 'database')
        }

    def _get_path(self, section, option, default):
        """Получение пути с созданием директории при необходимости"""
        path = self.config.get(section, option, fallback=default)
        os.makedirs(path, exist_ok=True)
        return path

    def _get_json(self, section, option, default):
        """Безопасное чтение JSON-строки"""
        try:
            return json.loads(self.config.get(section, option, fallback=json.dumps(default)))
        except json.JSONDecodeError:
            return default

    def _validate_parser_type(self, ptype):
        """Проверка что тип парсера поддерживается"""
        return ptype if ptype in self.PARSER_TYPES else 'sql'

    def _get_env_var(self, section, option):
        """Получение значения с подстановкой переменных окружения"""
        value = self.config.get(section, option, fallback='')
        return os.path.expandvars(value)

# Глобальный экземпляр конфига
config = AppConfig()

   