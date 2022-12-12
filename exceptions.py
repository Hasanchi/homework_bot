class StatusCodeNotOk(Exception):
    """Статус ответа не 200."""


class ListError(Exception):
    """Пришел пустой список."""


class ApiAnswersError(Exception):
    """Глобальные переменные недоступны."""
