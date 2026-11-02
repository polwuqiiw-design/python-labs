
"""Модели приложения."""

import re
from datetime import date, datetime
from decimal import Decimal
from functools import total_ordering

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
            "created_at": self.created_at.isoformat(),
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

    def __init__(
        self,
        username: str,
        email: str,
        full_name: str | None = None,
    ) -> None:
        super().__init__()
        self.username = username
        self.email = email
        self.full_name = full_name
        self._is_active = True

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
            raise ValidationError(
                "В имени разрешены латинские буквы, цифры и _"
            )

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

    @property
    def full_name(self) -> str | None:
        return self._full_name

    @full_name.setter
    def full_name(self, value: str | None) -> None:
        if value is None:
            self._full_name = None
            return

        if not isinstance(value, str):
            raise ValidationError("Полное имя должно быть строкой")

        value = value.strip()

        if not 2 <= len(value) <= 100:
            raise ValidationError(
                "Полное имя должно содержать от 2 до 100 символов"
            )

        if not all(char.isalpha() or char in " -" for char in value):
            raise ValidationError(
                "В полном имени разрешены буквы, пробелы и дефис"
            )

        self._full_name = value

    @property
    def is_active(self) -> bool:
        return self._is_active

    def deactivate(self) -> None:
        """Деактивировать пользователя."""
        self._is_active = False

    def activate(self) -> None:
        """Активировать пользователя."""
        self._is_active = True

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update(
            username=self.username,
            email=self.email,
            full_name=self.full_name,
            is_active=self.is_active,
        )
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

    def __init__(
        self,
        code: str,
        name: str,
        num_code: str | None = None,
    ) -> None:
        super().__init__()
        self.code = code
        self.name = name
        self.num_code = num_code

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
            raise ValidationError(
                "Код валюты должен состоять из 3 латинских букв"
            )

        self._code = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValidationError("Название валюты не может быть пустым")

        self._name = value.strip()

    @property
    def num_code(self) -> str | None:
        return self._num_code

    @num_code.setter
    def num_code(self, value: str | None) -> None:
        if value is None:
            self._num_code = None
            return

        if not isinstance(value, str):
            raise ValidationError("Цифровой код должен быть строкой")

        value = value.strip()

        if len(value) != 3 or not value.isascii() or not value.isdecimal():
            raise ValidationError(
                "Цифровой код должен содержать ровно 3 цифры"
            )

        self._num_code = value

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update(
            code=self.code,
            name=self.name,
            num_code=self.num_code,
        )
        return data

    def info(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f"{self.code} — {self.name}"

    def __repr__(self) -> str:
        return f"Currency(id={self.id}, code={self.code!r})"


@total_ordering
class Rate:
    """Курс валюты на определённую дату."""

    def __init__(
        self,
        code: str,
        name: str,
        nominal: int,
        value: Decimal,
        on_date: date,
        num_code: str | None = None,
    ) -> None:
        if nominal <= 0:
            raise ValidationError("Номинал должен быть положительным")

        value = Decimal(value)

        if value <= 0:
            raise ValidationError("Курс должен быть положительным")

        if num_code is not None:
            if not isinstance(num_code, str):
                raise ValidationError("Цифровой код должен быть строкой")

            num_code = num_code.strip()

            if (
                len(num_code) != 3
                or not num_code.isascii()
                or not num_code.isdecimal()
            ):
                raise ValidationError(
                    "Цифровой код должен содержать ровно 3 цифры"
                )

        self.code = code.upper()
        self.name = name
        self.nominal = nominal
        self.value = value
        self.date = on_date
        self.num_code = num_code

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
            self.date,
        ) == (
            other.code,
            other.nominal,
            other.value,
            other.date,
        )

    def __lt__(self, other: object) -> bool:
        """Сравнение по стоимости одной единицы валюты."""
        if not isinstance(other, Rate):
            return NotImplemented

        return self.per_unit < other.per_unit

    def __hash__(self) -> int:
        return hash((
            self.code,
            self.nominal,
            self.value,
            self.date,
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


class Subscription:
    """Подписка пользователя на валюту."""

    def __init__(self, user: User, currency: Currency) -> None:
        if not isinstance(user, User):
            raise TypeError("user должен быть объектом User")

        if not isinstance(currency, Currency):
            raise TypeError("currency должен быть объектом Currency")

        self._user = user
        self._currency = currency
        self._created_at = datetime.now()

    @property
    def user(self) -> User:
        return self._user

    @property
    def currency(self) -> Currency:
        return self._currency

    @property
    def key(self) -> tuple[int, int]:
        return self.user.id, self.currency.id

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Subscription):
            return NotImplemented
        return self.key == other.key

    def __hash__(self) -> int:
        return hash(self.key)

    def __repr__(self) -> str:
        return (
            f"Subscription(user_id={self.user.id}, "
            f"currency_id={self.currency.id})"
        )
