
"""Модели приложения."""


class User:
    """Пользователь приложения."""

    def __init__(self, username: str, email: str) -> None:
        self.username = username
        self.email = email

    def info(self) -> str:
        return f"{self.username} <{self.email}>"


class Currency:
    """Валюта."""

    def __init__(self, code: str, name: str) -> None:
        self.code = code
        self.name = name

    def info(self) -> str:
        return f"{self.code} — {self.name}"
