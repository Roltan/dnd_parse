import logging
import datetime
import sys

# Настройка логгера
logging.basicConfig(
    level=logging.DEBUG,  # Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Формат сообщений
    handlers=[
        logging.FileHandler('log.txt', encoding='utf-8'),  # Запись в файл
    ]
)

logger = logging.getLogger(__name__)

def log_error(message):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(message)
    logger.error(f"{current_time} - {message}")
    sys.exit()

def log_debug(message):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.debug(f"Debug: {current_time} - {message}")

def log_debug(message):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"Info: {current_time} - {message}")