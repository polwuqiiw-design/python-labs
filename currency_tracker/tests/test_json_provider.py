
"""Тесты JSON-поставщика курсов валют."""

from decimal import Decimal

import pytest

from app.exceptions import NotFoundError, ProviderError
from app.providers import CbrJsonProvider


SAMPLE_JSON = {
    "Date": "2026-10-27T11:30:00+03:00",
    "Valute": {
        "USD": {
            "NumCode": "840",
            "CharCode": "USD",
            "Nominal": 1,
            "Name": "Доллар США",
            "Value": 80.5,
        },
        "JPY": {
            "NumCode": "392",
            "CharCode": "JPY",
            "Nominal": 100,
            "Name": "Японских иен",
            "Value": 53.0,
        },
    },
}


def test_json_parse():
    rates = CbrJsonProvider.parse(SAMPLE_JSON)

    assert len(rates) == 2
    assert rates["USD"].num_code == "840"
    assert rates["USD"].value == Decimal("80.5")


def test_json_nominal():
    rates = CbrJsonProvider.parse(SAMPLE_JSON)

    assert rates["JPY"].per_unit == Decimal("0.53")


def test_invalid_json():
    with pytest.raises(ProviderError):
        CbrJsonProvider.parse({"Date": "invalid"})


def test_json_missing_currency():
    provider = CbrJsonProvider()

    # Подменяем загрузку, чтобы тест не использовал интернет
    provider.get_rates = lambda: CbrJsonProvider.parse(SAMPLE_JSON)

    with pytest.raises(NotFoundError):
        provider.get_rate("XXX")
