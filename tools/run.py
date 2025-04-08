from tools.loging import log_error, log_debug
import os
import importlib.util

class RunParser:
    def __init__(self, db):
        self.db = db

    def run_parser(self, module_path):
    # Загружаем модуль
        spec = importlib.util.spec_from_file_location(module_path[:-3], module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Вызываем функцию парсера (предположим, что она называется parse)
        if hasattr(module, 'parse'):
            try:
                module.parse(self.db)
                log_debug(f"Successfully parsed {module_path}")
            except Exception as e:
                log_error(f"Error parsing {module_path}: {e}")

    def run_all_parsers(self, directory):
        for root, dirs, files in os.walk(directory):
            for file_name in files:
                if file_name.endswith('.py'):
                    module_path = os.path.join(root, file_name)
                    self.run_parser(module_path)
            # Ограничиваем вложенность до двух уровней
            if root != directory:
                dirs.clear()

    def run_specific_parsers(self, directory, files_to_run):
        for file_path in files_to_run:
            full_path = os.path.join(directory, file_path)
            if os.path.isfile(full_path):
                self.run_parser(full_path)
            else:
                log_error(f"File {file_path} does not exist in {directory}")

    def run_parsers_by_folder(self, directory, target_folder):
        target_path = os.path.join(directory, target_folder)
        if os.path.isdir(target_path):
            for file_name in os.listdir(target_path):
                if file_name.endswith('.py'):
                    module_path = os.path.join(target_path, file_name)
                    self.run_parser(module_path)
        else:
            log_error(f"Target folder {target_folder} does not exist in {directory}")