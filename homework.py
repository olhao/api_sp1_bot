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


def get_homeworks(current_timestamp):
    try:
        homework_statuses = requests.get(
            PRAKTIKUM_URL,
            headers=HEADERS,
            params={'from_date': current_timestamp})
        if homework_statuses.json()["homeworks"]:
            homework = homework_statuses.json()["homeworks"][0]
            if "code" in homework or "error" in homework:
                raise Exception('Произошла ошибка при выполнении запроса -'
                                f' {homework["code"]}, {homework["error"]}')
            raise ValueError('Статус работы не найден.')
    except requests.exceptions.RequestException as request_exception:
        raise ConnectionError('Произошла ошибка соединения при запросе -'
                              f' {request_exception}'
                              'Проверьте параметры: '
                              f'PRAKTIKUM_URL: {PRAKTIKUM_URL} '
                              f'HEADERS: {HEADERS} '
                              f'current_timestamp: {current_timestamp}')
    return homework_statuses.json()


def parse_homework_status(homework):
    homework_name = homework['homework_name']
    homework_status = homework['status']

    if homework_status in VERDICTS:
        return ('У вас проверили работу '
                f'"{homework_name}"!\n\n{VERDICTS[homework_status]}')
    raise ValueError(f'Статус работы {homework_status} не найден.')


def send_message(message):
    try:
        bot.send_message(CHAT_ID, message)
        logging.info('Сообщение отправлено')
    except Exception:
        logging.exception('Бот не смог отправить сообщение')


def get_homework_date():
    current_timestamp = int(time.time())
    homework_statuses = requests.get(
        PRAKTIKUM_URL,
        headers=HEADERS,
        params={'from_date': current_timestamp})
    homework_date = homework_statuses.json()["current_date"]
    return homework_date


def main():
    logging.debug('Бот запущен')
    current_timestamp = get_homework_date()

    while True:
        try:
            homework = get_homeworks(
                current_timestamp)['homeworks'][0]
            message = parse_homework_status(homework)
            send_message(message)

        except Exception as exception:
            message = f'Ошибка: {exception}'
            send_message(message)
            logging.info('Сообщение об ошибке отправлено в telegram -'
                         f' {message}')
            logging.exception(f'Произошла ошибка {exception}')
        time.sleep(20 * 60)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        filename=__file__ + '.log',
                        format=('%(asctime)s, %(levelname)s, '
                                '%(message)s, %(name)s'),
                        filemode='a', )
    main()
