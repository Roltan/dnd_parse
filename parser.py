import argparse
import sys
from tools.config import config
from tools.creator import ParserCreator
from tools.output import Output
from tools.run import RunParser

def setup_argparse():
    """Настройка аргументов командной строки"""
    parser = argparse.ArgumentParser(description="Парсер SQL и веб-данных")
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Парсер для create
    create = subparsers.add_parser('create', help='Создать новый парсер')
    create.add_argument('name', help='Имя парсера (без .py)')
    for ptype, desc in config.PARSER_TYPES.items():
        create.add_argument(
            f'--{ptype}',
            action='store_const',
            const=ptype,
            dest='parser_type',
            help=f'Создать {desc.lower()}'
        )
    create.set_defaults(func=handle_create)

    # Парсер для run
    run = subparsers.add_parser('run', help='Запустить парсеры')
    run.add_argument('--all', action='store_true', help='Запустить все парсеры')
    run.add_argument('--file', help='Запустить конкретный файл')
    run.set_defaults(func=handle_run)

    return parser

def handle_create(args):
    """Обработка команды create"""
    creator = ParserCreator()
    try:
        created_file = creator.create(args.name, args.parser_type)
        print(f"✅ Создан парсер: {created_file}")
    except Exception as e:
        print(f"❌ Ошибка: {e}", file=sys.stderr)
        sys.exit(1)

def handle_run(args):
    """Обработка команды run"""
    runner = RunParser(Output(**config.db_config))
    try:
        if args.all:
            runner.run_all_parsers(config.table_directory)
        elif args.file:
            runner.run_specific_parsers(config.table_directory, [args.file])
        else:
            runner.run_specific_parsers(config.table_directory, config.files_to_run)
    except Exception as e:
        print(f"❌ Ошибка при запуске: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    parser = setup_argparse()
    args = parser.parse_args()
    args.func(args)