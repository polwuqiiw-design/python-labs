
"""Проверка классов User, Currency и Rate."""

from datetime import date
from decimal import Decimal

import pytest

from app.exceptions import ValidationError
from app.models import Currency, Rate, User


def test_user_creation():
    user = User("anna", "anna@example.com")

    assert user.username == "anna"
    assert user.email == "anna@example.com"
    assert user.id == 1


def test_user_email_lowercase():
    user = User("anna", "ANNA@EXAMPLE.COM")

    assert user.email == "anna@example.com"


def test_short_username():
    with pytest.raises(ValidationError):
        User("an", "anna@example.com")


def test_invalid_email():
    with pytest.raises(ValidationError):
        User("anna", "wrong_email")


def test_currency_creation():
    currency = Currency("usd", "Доллар США")

    assert currency.code == "USD"
    assert currency.name == "Доллар США"


def test_invalid_currency():
    with pytest.raises(ValidationError):
        Currency("US", "Доллар США")


def test_rate_per_unit():
    rate = Rate(
        "JPY",
        "Японская иена",
        100,
        Decimal("53.0"),
        date(2026, 10, 27)
    )

    assert rate.per_unit == Decimal("0.53")


def test_user_ids():
    user1 = User("anna", "anna@example.com")
    user2 = User("boris", "boris@example.com")

    assert user1.id == 1
    assert user2.id == 2


def test_currency_ids():
    currency1 = Currency("USD", "Доллар США")
    currency2 = Currency("EUR", "Евро")

    assert currency1.id == 1
    assert currency2.id == 2


def test_user_username_spaces():
    user = User(" anna ", "anna@example.com")

    assert user.username == "anna"


def test_currency_code_spaces():
    currency = Currency(" usd ", "Доллар США")

    assert currency.code == "USD"


def test_empty_currency_name():
    with pytest.raises(ValidationError):
        Currency("USD", "")


def test_username_invalid_characters():
    with pytest.raises(ValidationError):
        User("anna!", "anna@example.com")


def test_user_inheritance():
    from app.models import BaseEntity

    user = User("anna", "anna@example.com")

    assert isinstance(user, BaseEntity)


def test_currency_inheritance():
    from app.models import BaseEntity

    currency = Currency("USD", "Доллар США")

    assert isinstance(currency, BaseEntity)


def test_user_to_dict():
    user = User("anna", "anna@example.com")

    data = user.to_dict()

    assert data["username"] == "anna"
    assert data["email"] == "anna@example.com"
    assert data["id"] == 1


def test_currency_to_dict():
    currency = Currency("USD", "Доллар США")

    data = currency.to_dict()

    assert data["code"] == "USD"
    assert data["name"] == "Доллар США"


def test_user_str():
    user = User("anna", "anna@example.com")

    assert str(user) == "anna <anna@example.com>"


def test_currency_str():
    currency = Currency("USD", "Доллар США")

    assert str(currency) == "USD — Доллар США"


def test_user_repr():
    user = User("anna", "anna@example.com")

    assert "User" in repr(user)
    assert "anna" in repr(user)


def test_currency_repr():
    currency = Currency("USD", "Доллар США")

    assert "Currency" in repr(currency)
    assert "USD" in repr(currency)
