import logging
import os
import time
from logging import FileHandler, StreamHandler

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
PRAKTIKUM_URL = os.getenv('PRAKTIKUM_URL')
current_timestamp = int(time.time())  # 1629105077


bot = telegram.Bot(TELEGRAM_TOKEN)


def file_logger():
    logging.basicConfig(
        level=logging.DEBUG,
        filename='main.log',
        format='%(asctime)s, %(levelname)s, %(message)s, %(name)s',
        filemode='a',)

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    file_handler = FileHandler('main.log')
    logger.addHandler(file_handler)


def file_debug_logger():
    file_logger()
    logging.debug('Бот запущен')


def file_info_logger():
    file_logger()
    logging.info('Сообщение отправлено')


def file_error_logger():
    file_logger()
    logging.error('Бот не смог отправить сообщение')


def stream_error_logger():
    logging.basicConfig(
        level=logging.ERROR,
        filename='main.log',
        format='%(asctime)s, %(levelname)s, %(name)s, %(message)s',
        filemode='a',)

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.ERROR)
    stream_handler = StreamHandler()
    logger.addHandler(stream_handler)

    logging.error('Бот не смог отправить сообщение')


def get_homeworks(current_timestamp):
    homework_statuses = requests.get(
        PRAKTIKUM_URL,
        headers={'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'},
        params={'from_date': current_timestamp})
    return homework_statuses.json()


def parse_homework_status(homework):
    homework_name = homework['homework_name']
    homework = homework['status']
    if homework == 'rejected':
        verdict = 'К сожалению, в работе нашлись ошибки.'
    elif homework == 'reviewing':
        verdict = 'Pабота взята в ревью.'
    else:
        verdict = 'Ревьюеру всё понравилось, работа зачтена!'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def send_message(message):
    return bot.send_message(CHAT_ID, message)


def main():
    current_timestamp = int(time.time())
    file_debug_logger()
    homework = get_homeworks(current_timestamp=current_timestamp)
    message = parse_homework_status(homework)
    while True:
        try:
            send_message(message)
            file_info_logger()
            time.sleep(20 * 60)  # Опрашивать раз в 20 минут

        except Exception as e:
            message = f'Бот упал с ошибкой: {e}'
            bot.send_message(CHAT_ID, message)
            stream_error_logger()
            file_error_logger()
            time.sleep(5)


if __name__ == '__main__':
    main()
