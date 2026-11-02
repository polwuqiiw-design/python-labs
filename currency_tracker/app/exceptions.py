
"""Ошибки приложения."""


class AppError(Exception):
    """Общая ошибка приложения."""


class ValidationError(AppError):
    """Ошибка проверки данных."""


class DuplicateError(AppError):
    """Объект уже существует."""


class NotFoundError(AppError):
    """Объект не найден."""


class ProviderError(AppError):
    """Ошибка получения курсов валют."""
