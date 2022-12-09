class StatusCodeNotOk(Exception):
    """Статус ответа не 200."""


class ConnectionError(Exception):
    """Ошибка соединения."""


class VariablesNotAailable(Exception):
    """Глобальные переменные недоступны."""
