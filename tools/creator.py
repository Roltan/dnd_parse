import os
from tools.config import config

class ParserCreator:
    def _get_templates(self):
        return {
            'sql': self._sql_template(),
            'www': self._web_template(),
        }
    
    def _sql_template(self):
        return """from tools.read import ReadSQL
from tools.output import Output
from tools.loging import log_error

def parse(output = Output()):
    # Настройки парсера
    input_file = ''
    table_name = ''
    
    # Инициализация
    table = ReadSQL(input_file, table_name)
    
    # Ваш код парсинга:
    # for row in table:
    #     output.write('table_name', row)"""

    def _web_template(self):
        return """from tools.output import Output
import requests
from bs4 import BeautifulSoup
from time import sleep
from tools.loging import log_error

def parse(output = Output()):
    # Настройки парсера
    base_url = ''
    headers = {{
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }}
    
    # Ваш код парсинга:
    # response = requests.get(base_url, headers=headers)
    # if response.status_code == 200:
    #     soup = BeautifulSoup(response.text, 'html.parser')
    #     for item in soup.select('.items'):
    #         data = {{'name': item.text.strip()}}
    #         output.write('items', data)"""

    def create(self, name, parser_type=None):
        templates = self._get_templates()
        ptype = self._resolve_parser_type(parser_type)
        
        if ptype not in templates:
            raise ValueError(
                f"Неподдерживаемый тип парсера. Доступные: {list(templates.keys())}"
            )

        file_path = os.path.join(config.table_directory, f"{name}.py")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(templates[ptype].format(
                db_config=', '.join(f"{k}='{v}'" for k, v in config.db_config.items())
            ))
        
        return file_path
    
    def _resolve_parser_type(self, parser_type):
        """Определение типа парсера с учетом конфига"""
        if parser_type and parser_type in config.PARSER_TYPES:
            return parser_type
        return config.default_type