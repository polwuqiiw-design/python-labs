
"""Общие данные для тестирования."""

from datetime import date
from decimal import Decimal

import pytest

from app.models import BaseEntity, Currency, Rate, User
from app.providers import StaticRateProvider
from app.services import CurrencyTracker


@pytest.fixture(autouse=True)
def reset_ids():
    """Обнуляем номера перед каждым тестом."""
    for cls in (BaseEntity, User, Currency):
        cls.reset_ids()


@pytest.fixture
def rates():
    """Пример курсов валют."""
    day = date(2026, 10, 27)

    return [
        Rate("USD", "Доллар США", 1, Decimal("80.5"), day),
        Rate("EUR", "Евро", 1, Decimal("93.1"), day),
        Rate("JPY", "Японских иен", 100, Decimal("53.0"), day),
    ]


@pytest.fixture
def tracker(rates):
    """Готовый трекер для тестов."""
    provider = StaticRateProvider(rates)
    tracker = CurrencyTracker(provider)
    tracker.sync_currencies()
    return tracker
