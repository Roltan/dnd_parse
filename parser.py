from tools.output import Output
from tools.run import RunParser
from tools.loging import log_error, log_debug
import os
import argparse
import sys
import traceback

# папка с парсерами
table_directory = "table"
# подключение к целевой бд
DB = Output(host='MySQL-8.2', user='root', password='', database='dnd_hero')
runParser = RunParser(DB)
# Список файлов, которые нужно запустить (если пустой, запустятся все)
files_to_run = [
    "vin/wmi.py",
]

# Перехват исключений
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    log_error(f"Uncaught exception:\n    {exc_type.__name__};\n    {exc_value};\n{''.join(traceback.format_tb(exc_traceback))}\n")

def create_parser_file(parser_path):
    # Путь к папке с базой данных
    full_path = os.path.join(table_directory, parser_path)
    dir_path = os.path.dirname(full_path)
    
    # Создаем папку, если она не существует
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    
    # Путь к файлу парсера
    file_path = full_path + '.py'
    
    # Создаем файл и записываем в него шаблон парсера
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(f"""from tools.read import ReadSQL
from tools.output import Output
from tools.loging import log_error
from collections import OrderedDict
import json

def parse(output = Output(host='MySQL-8.2', user='root', password='', database='example')):
    # название входного файла
    input_file = ''
    # название искомой таблицы
    table_name = ''
    # название создаваемого атрибута
    atrName = ''
                
    # переменные с данными таблиц
    table = ReadSQL(input_file, table_name)
                
    ##""")
    
    print(f"Created parser file: {file_path}")

sys.excepthook = handle_exception
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage parser files.")
    subparsers = parser.add_subparsers(dest='command')

    # Подкоманда для создания нового файла парсера
    create_parser = subparsers.add_parser('create', help='Create a new parser file')
    create_parser.add_argument('parser', type=str, help='Parser name or path')

    # Подкоманда для запуска парсеров
    run_parser = subparsers.add_parser('run', help='Run parsers')
    run_parser.add_argument('--all', action='store_true', help='Run all parsers')
    run_parser.add_argument('--dir', type=str, help='Directory to run parsers from')

    args = parser.parse_args()

    if args.command == 'create':
        create_parser_file(args.parser)
    elif args.command == 'run':
        if args.all:
            runParser.run_all_parsers(table_directory)
        elif args.dir:
            runParser.run_parsers_by_folder(table_directory, args.dir)
        else:
            runParser.run_specific_parsers(table_directory, files_to_run)