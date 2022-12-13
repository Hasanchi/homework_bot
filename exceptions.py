class StatusCodeNotOk(Exception):
    """Статус ответа не 200."""


class ListError(Exception):
    """Пришел пустой список."""


class ApiAnswersError(Exception):
    """Глобальные переменные недоступны."""


class NotSendMessage(Exception):
    """Сообщение не отправлено."""


class NotValidJson(Exception):
    """Не валидный json."""
