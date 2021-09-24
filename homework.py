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
PRAKTIKUM_URL = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
VERDICTS = {'rejected': 'К сожалению, в работе нашлись ошибки.',
            'reviewing': 'Pабота взята в ревью.',
            'approved': 'Ревьюеру всё понравилось, работа зачтена!'}

bot = telegram.Bot(TELEGRAM_TOKEN)


class ExceptionErrorStatuses(Exception):
    pass


def get_homeworks(current_timestamp):
    params = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(
            PRAKTIKUM_URL,
            headers=HEADERS,
            params=params)
    except requests.exceptions.RequestException as request_exception:
        raise ConnectionError('Произошла ошибка соединения при запросе -'
                              f' {request_exception}'
                              'Проверьте параметры: '
                              f'PRAKTIKUM_URL: {PRAKTIKUM_URL}, '
                              f'HEADERS: {HEADERS}, '
                              f'{params}')

    response = homework_statuses.json()
    errors = ["code", "error"]
    for error in errors:
        if error in response:
            raise ExceptionErrorStatuses('Произошла ошибка '
                                         'при выполнении запроса.'
                                         f'Значение ошибки: {response[error]}.'
                                         'Отправленные параметры: '
                                         f'PRAKTIKUM_URL: {PRAKTIKUM_URL}, '
                                         f'HEADERS: {HEADERS}, '
                                         f'{params}')
    return response


def parse_homework_status(homework):
    status = homework['status']

    if status in VERDICTS:
        return ('У вас проверили работу '
                f'"{homework["homework_name"]}"!\n\n{VERDICTS[status]}')
    raise ValueError(f'Статус работы {status} не найден.')


def send_message(message):
    try:
        bot.send_message(CHAT_ID, message)
        logging.info(f'Сообщение отправлено. Текст сообщения: {message}')
    except Exception:
        logging.exception('Бот не смог отправить сообщение')


def main():
    logging.debug('Бот запущен')
    current_timestamp = int(time.time())
    homeworks = get_homeworks(current_timestamp)

    while True:
        try:
            homework = homeworks['homeworks'][0]
            message = parse_homework_status(homework)
            send_message(message)

        except Exception as exception:
            message = f'Ошибка: {exception}'
            logging.exception(f'Произошла ошибка {exception}')
            send_message(message)
            logging.info('Сообщение об ошибке отправлено в telegram -'
                         f' {message}')
        time.sleep(20 * 60)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        filename=__file__ + '.log',
                        format=('%(asctime)s, %(levelname)s, '
                                '%(message)s, %(name)s'),
                        filemode='a', )
    main()
