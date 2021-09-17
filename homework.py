import logging
import os
import time
from logging.handlers import RotatingFileHandler

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
PRAKTIKUM_URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
STATUSES = {'rejected': 'К сожалению, в работе нашлись ошибки.',
            'reviewing': 'Pабота взята в ревью.',
            'approved': 'Ревьюеру всё понравилось, работа зачтена!'}

bot = telegram.Bot(TELEGRAM_TOKEN)


def get_homeworks(current_timestamp):
    try:
        homework_statuses = requests.get(
            PRAKTIKUM_URL,
            headers=HEADERS,
            params={'from_date': current_timestamp})
        return homework_statuses.json()
    except Exception:
        logging.exception('Бот не смог отправить сообщение')
        logging.error('Бот не смог отправить сообщение', exc_info=True)


def parse_homework_status(homework):
    homework_name = homework['homework_name']
    homework = homework['status']
    for status, verdict in STATUSES.items():
        try:
            if homework == status:
                return ('У вас проверили работу '
                        f'"{homework_name}"!\n\n{verdict}')
            raise Exception(f'Cтатуса {homework} домашней работы не найдено.')
        except Exception:
            logging.exception('Бот не смог отправить сообщение')
            logging.error('Бот не смог отправить сообщение', exc_info=True)


def send_message(message):
    try:
        return bot.send_message(CHAT_ID, message)
    except Exception:
        logging.exception('Бот не смог отправить сообщение')
        logging.error('Бот не смог отправить сообщение', exc_info=True)


def main():
    logging.basicConfig(
        level=logging.DEBUG,
        filename=os.path.expanduser(__file__ + '.log'),
        format='%(asctime)s, %(levelname)s, %(message)s, %(name)s',
        filemode='a',)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    file_handler = RotatingFileHandler(os.path.expanduser(__file__ + '.log'),
                                       maxBytes=50000000,
                                       backupCount=5)
    logger.addHandler(file_handler)
    logging.debug('Бот запущен')
    #  для int(time.time()) падает с ошибкой: 86400 == 1 день
    current_timestamp = int(time.time()) - 86400
    while True:
        try:
            homework = get_homeworks(
                current_timestamp=current_timestamp)['homeworks'][0]
            message = parse_homework_status(homework)
            send_message(message)
            logging.info('Сообщение отправлено')
            time.sleep(20 * 60)

        except Exception as e:
            message = f'Бот упал с ошибкой: {e}'
            bot.send_message(CHAT_ID, message)
            logging.exception('Бот не смог отправить сообщение')
            logging.error('Бот не смог отправить сообщение', exc_info=True)


if __name__ == '__main__':
    main()
