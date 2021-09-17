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

# Логер
logger = logging.getLogger('homework')
logger.setLevel(logging.DEBUG)
log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler("logs.log", encoding='UTF-8')
file_handler.setFormatter(log_format)
logger.addHandler(file_handler)


bot = telegram.Bot(token=TELEGRAM_TOKEN)


def parse_homework_status(homework):
    homework_name = homework['homework_name']
    if homework['status'] == 'rejected':
        verdict = 'К сожалению, в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, работа зачтена!'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    payload = {'from_date': current_timestamp}
    homework_statuses = requests.get(PRAKTIKUM_URL,
                                     headers=headers,
                                     params=payload)
    return homework_statuses.json()


def send_message(message):
    return bot.send_message(CHAT_ID, message)


def main():
    logger.debug('Start monitoring homework')
    current_timestamp = int(time.time())  # Начальное значение timestamp
    while True:
        try:
            homework = get_homeworks(current_timestamp).get('homeworks')
            if homework:
                message = parse_homework_status(homework[0])
                send_message(message)
                current_timestamp = int(time.time())
                logger.info('Bot sent message')
            time.sleep(300)  # Опрашивать раз в пять минут

        except Exception as e:
            error = f'Бот упал с ошибкой: {e}'
            logger.error(error)
            send_message(error)
            time.sleep(30)


if __name__ == '__main__':
    main()

