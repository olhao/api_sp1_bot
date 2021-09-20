import logging
import os
import time

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

logging.basicConfig(level=logging.DEBUG,
                    filename=__file__ + '.log',
                    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s',
                    filemode='a',)


def get_homeworks(current_timestamp):
    try:
        homework_statuses = requests.get(
            PRAKTIKUM_URL,
            headers=HEADERS,
            params={'from_date': current_timestamp})
        return homework_statuses.json()
    except requests.exceptions.RequestException as RequestException:
        raise SystemExit(RequestException)


def parse_homework_status(homework):
    homework_name = homework['homework_name']
    homework_status = homework['status']

    if homework_status in VERDICTS:
        return ('У вас проверили работу '
                f'"{homework_name}"!\n\n{VERDICTS[homework_status]}')
    #  IndexError - Raised when a sequence subscript is out of range

    '''exception ValueError - Raised when an operation or function receives
        an argument that has the right type but an inappropriate value,
        and the situation is not described by a more
        precise exception such as IndexError'''
    '''Traceback (most recent call last):
        homework = get_homeworks(
        IndexError: list index out of range'''
    raise IndexError(f'Статус работы {homework_status} не найден.')


def send_message(message):
    try:
        return bot.send_message(CHAT_ID, message)
    except Exception:
        #  здесь имя не нужно logging.exception уже
        #  выводит всю необходимую информацию с описание ексепшина
        logging.exception('Бот не смог отправить сообщение')


def main():
    logging.debug('Бот запущен')
    # ["homeworks"][0]["date_updated"] в json ответе,
    # но get_homeworks(current_timestamp) использует current_timestamp
    current_timestamp = int(time.time())

    while True:
        try:
            homework = get_homeworks(
                current_timestamp=current_timestamp)['homeworks'][0]
            message = parse_homework_status(homework)
            send_message(message)
            # этот ивент попадает в лог только если сообщение отправлено,
            # т.к. находит внутри трай.
            # в случае ексепшина он не записывается в лог файл
            logging.info('Сообщение отправлено')

        except Exception as exception:
            message = f'Ошибка: {exception}'
            send_message(message)
            logging.exception('Бот не смог отправить сообщение')
        time.sleep(20 * 60)


if __name__ == '__main__':
    main()
