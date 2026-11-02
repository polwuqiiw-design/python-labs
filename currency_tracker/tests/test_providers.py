
"""Тесты поставщиков курсов валют."""

from decimal import Decimal

import pytest
import requests

from app.exceptions import NotFoundError, ProviderError
from app.providers import CbrXmlProvider, RateProvider, StaticRateProvider


SAMPLE_XML = """<?xml version="1.0" encoding="windows-1251"?>
<ValCurs Date="27.10.2026" name="Foreign Currency Market">
<Valute ID="R01235">
<CharCode>USD</CharCode>
<Nominal>1</Nominal>
<Name>Доллар США</Name>
<Value>80,5000</Value>
</Valute>
<Valute ID="R01820">
<CharCode>JPY</CharCode>
<Nominal>100</Nominal>
<Name>Японских иен</Name>
<Value>53,0000</Value>
</Valute>
</ValCurs>""".encode("windows-1251")


def test_abstract_provider():
    with pytest.raises(TypeError):
        RateProvider()


def test_static_provider(rates):
    provider = StaticRateProvider(rates)

    assert len(provider.get_rates()) == 3
    assert provider.get_rate("USD").code == "USD"


def test_provider_code_normalization(rates):
    provider = StaticRateProvider(rates)

    assert provider.get_rate(" usd ").code == "USD"


def test_missing_rate(rates):
    provider = StaticRateProvider(rates)

    with pytest.raises(NotFoundError):
        provider.get_rate("GBP")


def test_static_provider_returns_copy(rates):
    provider = StaticRateProvider(rates)

    result = provider.get_rates()
    result.clear()

    assert len(provider.get_rates()) == 3


def test_parse_xml():
    result = CbrXmlProvider.parse(SAMPLE_XML)

    assert len(result) == 2
    assert result["USD"].value == Decimal("80.5000")
    assert result["JPY"].nominal == 100


def test_parse_per_unit():
    result = CbrXmlProvider.parse(SAMPLE_XML)

    assert result["JPY"].per_unit == Decimal("0.5300")


def test_invalid_xml():
    with pytest.raises(ProviderError):
        CbrXmlProvider.parse(b"invalid xml")


def test_network_error(monkeypatch):
    def fake_get(*args, **kwargs):
        raise requests.ConnectionError("Нет соединения")

    monkeypatch.setattr(requests, "get", fake_get)

    provider = CbrXmlProvider()

    with pytest.raises(ProviderError):
        provider.get_rates()


def test_parse_num_code():
    """Проверяем чтение цифрового кода из XML."""
    xml_data = """<?xml version="1.0" encoding="utf-8"?>
    <ValCurs Date="27.10.2026">
        <Valute>
            <NumCode>840</NumCode>
            <CharCode>USD</CharCode>
            <Nominal>1</Nominal>
            <Name>Доллар США</Name>
            <Value>80,5000</Value>
        </Valute>
    </ValCurs>""".encode("utf-8")

    result = CbrXmlProvider.parse(xml_data)

    assert result["USD"].num_code == "840"


def test_timeout(monkeypatch):
    """Проверяем ошибку при долгом ожидании сервера."""
    def fake_get(*args, **kwargs):
        raise requests.Timeout("Время ожидания истекло")

    monkeypatch.setattr(requests, "get", fake_get)

    with pytest.raises(ProviderError, match="не ответил"):
        CbrXmlProvider().get_rates()


def test_skipped_count():
    """Проверяем подсчёт повреждённых записей."""
    xml_data = """<?xml version="1.0" encoding="utf-8"?>
    <ValCurs Date="27.10.2026">
        <Valute>
            <CharCode>USD</CharCode>
            <Nominal>1</Nominal>
            <Name>Доллар США</Name>
            <Value>80,5000</Value>
        </Valute>
        <Valute>
            <CharCode>EUR</CharCode>
            <Nominal>abc</Nominal>
            <Name>Евро</Name>
            <Value>93,0000</Value>
        </Valute>
    </ValCurs>""".encode("utf-8")

    provider = CbrXmlProvider()
    rates = provider._parse_xml(xml_data)

    assert len(rates) == 1
    assert provider.skipped_count == 1
