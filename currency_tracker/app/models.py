
"""Модели приложения."""

import re
from datetime import date, datetime
from decimal import Decimal

from app.exceptions import ValidationError


class BaseEntity:
    """Общий класс для пользователя и валюты."""

    _id_counter = 0

    def __init__(self) -> None:
        self.__id = self._generate_id()
        self._created_at = datetime.now()

    @classmethod
    def _generate_id(cls) -> int:
        cls._id_counter += 1
        return cls._id_counter

    @classmethod
    def reset_ids(cls) -> None:
        cls._id_counter = 0

    @property
    def id(self) -> int:
        return self.__id

    @property
    def created_at(self) -> datetime:
        return self._created_at

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat()
        }

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BaseEntity):
            return NotImplemented
        return type(self) is type(other) and self.id == other.id

    def __hash__(self) -> int:
        return hash((type(self), self.id))

    def __repr__(self) -> str:
        return f"{type(self).__name__}(id={self.id})"


class User(BaseEntity):
    """Пользователь приложения."""

    _id_counter = 0

    USERNAME_MIN_LENGTH = 3
    USERNAME_MAX_LENGTH = 32

    _USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_]+$")
    _EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

    def __init__(self, username: str, email: str) -> None:
        super().__init__()
        self.username = username
        self.email = email

    @property
    def username(self) -> str:
        return self._username

    @username.setter
    def username(self, value: str) -> None:
        if not isinstance(value, str):
            raise ValidationError("Имя должно быть строкой")

        value = value.strip()

        if not self.USERNAME_MIN_LENGTH <= len(value) <= self.USERNAME_MAX_LENGTH:
            raise ValidationError("Имя должно содержать от 3 до 32 символов")

        if not self._USERNAME_PATTERN.fullmatch(value):
            raise ValidationError("В имени разрешены латинские буквы, цифры и _")

        self._username = value

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        if not isinstance(value, str):
            raise ValidationError("Email должен быть строкой")

        value = value.strip().lower()

        if not self._EMAIL_PATTERN.fullmatch(value):
            raise ValidationError("Неправильный email")

        self._email = value

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update(username=self.username, email=self.email)
        return data

    def info(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f"{self.username} <{self.email}>"

    def __repr__(self) -> str:
        return f"User(id={self.id}, username={self.username!r})"


class Currency(BaseEntity):
    """Валюта."""

    _id_counter = 0

    CODE_LENGTH = 3

    def __init__(self, code: str, name: str) -> None:
        super().__init__()
        self.code = code
        self.name = name

    @property
    def code(self) -> str:
        return self._code

    @code.setter
    def code(self, value: str) -> None:
        if not isinstance(value, str):
            raise ValidationError("Код валюты должен быть строкой")

        value = value.strip().upper()

        if len(value) != self.CODE_LENGTH or not (
            value.isascii() and value.isalpha()
        ):
            raise ValidationError("Код валюты должен состоять из 3 латинских букв")

        self._code = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValidationError("Название валюты не может быть пустым")

        self._name = value.strip()

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update(code=self.code, name=self.name)
        return data

    def info(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f"{self.code} — {self.name}"

    def __repr__(self) -> str:
        return f"Currency(id={self.id}, code={self.code!r})"


class Rate:
    """Курс валюты на определённую дату."""

    def __init__(
        self,
        code: str,
        name: str,
        nominal: int,
        value: Decimal,
        on_date: date
    ) -> None:
        if nominal <= 0:
            raise ValidationError("Номинал должен быть положительным")

        value = Decimal(value)

        if value <= 0:
            raise ValidationError("Курс должен быть положительным")

        self.code = code.upper()
        self.name = name
        self.nominal = nominal
        self.value = value
        self.date = on_date

    @property
    def per_unit(self) -> Decimal:
        """Стоимость одной единицы валюты."""
        return self.value / self.nominal

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Rate):
            return NotImplemented

        return (
            self.code,
            self.nominal,
            self.value,
            self.date
        ) == (
            other.code,
            other.nominal,
            other.value,
            other.date
        )

    def __hash__(self) -> int:
        return hash((
            self.code,
            self.nominal,
            self.value,
            self.date
        ))

    def __str__(self) -> str:
        return (
            f"{self.nominal} {self.code} = "
            f"{self.value} RUB на {self.date:%d.%m.%Y}"
        )

    def __repr__(self) -> str:
        return (
            f"Rate({self.code!r}, "
            f"nominal={self.nominal}, value={self.value})"
        )
