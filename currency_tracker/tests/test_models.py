
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
