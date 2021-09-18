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
VERDICTS = {'rejected': 'К сожалению, в работе нашлись ошибки.',
            'reviewing': 'Pабота взята в ревью.',
            'approved': 'Ревьюеру всё понравилось, работа зачтена!'}

bot = telegram.Bot(TELEGRAM_TOKEN)


def get_homeworks(current_timestamp):
    try:
        homework_statuses = requests.get(
            PRAKTIKUM_URL,
            headers=HEADERS,
            params={'from_date': current_timestamp})
        if homework_statuses.json()["homeworks"] is None:
            raise Exception(f'{homework_statuses}')
        return homework_statuses.json()
    except Exception as exception:
        print(f'{exception}')


def parse_homework_status(homework):
    homework_name = homework['homework_name']
    homework = homework['status']

    if homework in VERDICTS.keys():
        verdict = VERDICTS[homework]
        return ('У вас проверили работу '
                f'"{homework_name}"!\n\n{verdict}')
    raise IndexError(f'Статус работы {homework_name} не найден')


def send_message(message):
    try:
        return bot.send_message(CHAT_ID, message)
    except Exception:
        # здесь имя не нужно logging.exception уже выводит всю необходимую информацию с описание ексепшина
        logging.exception(f'Бот не смог отправить сообщение')


def main():
    logging.basicConfig(
        level=logging.DEBUG,
        filename=__file__ + '.log',
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
    current_timestamp = int(time.time()) - 24*60*60
    while True:
        try:
            homework = get_homeworks(
                current_timestamp=current_timestamp)['homeworks'][0]
            message = parse_homework_status(homework)
            send_message(message)
            logging.info('Сообщение отправлено')

        except Exception as exception:
            message = f'Ошибка: {exception}'
            send_message(message)
            logging.exception('Бот не смог отправить сообщение')
            logging.error('Бот не смог отправить сообщение', exc_info=True)
        time.sleep(20*60)


if __name__ == '__main__':
    main()
