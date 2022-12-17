import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

import exceptions

load_dotenv()

logging.basicConfig(
    format='%(asctime)s,%(message)s, %(levelname)s, %(name)s',
    level=logging.INFO,
    filemode='w',
    filename='main.log',
)


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Проверка доступности переменных."""
    for token in (PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID):
        if not token:
            return False
    return True


def send_message(bot, message):
    """Отправка сообщения."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except telegram.TelegramError as error:
        logging.error(f'message={message}')
        raise exceptions.NotSendMessage() from error()
    logging.debug(f'Сообщение "{message}" отправлено')


def get_api_answer(timestamp):
    """Получает информации через API."""
    params = {'from_date': timestamp}
    try:
        homework_statuses = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=params
        )
        if homework_statuses.status_code != HTTPStatus.OK:
            raise exceptions.StatusCodeNotOk()
        return homework_statuses.json()
    except requests.exceptions.InvalidJSONError as error:
        raise exceptions.NotValidJson(f'error = {error}')
    except requests.exceptions.RequestException as error:
        raise exceptions.ApiAnswersError(f'error = {error}')


def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    if not isinstance(response, dict):
        raise TypeError('Тип данных ответа не соотвествует ожиданию')
    if not isinstance(response.get('homeworks'), list):
        raise TypeError('Данные приходят не в виде списка')
    try:
        return response['homeworks'][0]
    except KeyError as error:
        logging.error(error)
        raise exceptions.ListError()


def parse_status(homework):
    """Извлекает статус из домашней работы."""
    if 'homework_name' not in homework:
        raise KeyError('нет ключа homework_name')
    homework_name = homework.get('homework_name')
    homework_verdict = homework.get('status')
    if homework_verdict not in HOMEWORK_VERDICTS:
        raise KeyError(f'Такого статуса нет: {homework_verdict}')
    verdict = HOMEWORK_VERDICTS[homework_verdict]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    logging.critical('Отсутствует глобальная переменная')
    if not check_tokens():
        sys.exit()

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(timestamp)
            homework = check_response(response)
            message = parse_status(homework)
            send_message(bot, message)
            logging.debug(
                'Получили ответ от API в'
                f'соответсвии с документацией: "{homework}"'
            )
            logging.debug('Отсутствие в ответе новых статусов')
        except exceptions.NotSendMessage as error:
            message = f'Сообщение не может быть отправлено {error}'
            logging.critical(message)
            raise error()
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.critical(message)
            send_message(bot, message)
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
