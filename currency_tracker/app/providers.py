
"""Поставщики курсов валют."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from collections.abc import Iterable
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

import requests

from app.exceptions import NotFoundError, ProviderError, ValidationError
from app.models import Rate


class RateProvider(ABC):
    """Общий интерфейс поставщиков курсов."""

    @abstractmethod
    def get_rates(self) -> dict[str, Rate]:
        """Получить все курсы валют."""

    def get_rate(self, code: str) -> Rate:
        rates = self.get_rates()
        code = code.strip().upper()

        if code not in rates:
            raise NotFoundError(f"Курс {code} не найден")

        return rates[code]


class CbrXmlProvider(RateProvider):
    """Получение курсов с сайта ЦБ РФ."""

    URL = "https://www.cbr.ru/scripts/XML_daily.asp"
    TIMEOUT = 10
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (student lab: currency tracker)"
    }

    def __init__(
        self,
        url: str | None = None,
        timeout: float | None = None,
    ) -> None:
        self._url = url or self.URL
        self._timeout = timeout or self.TIMEOUT

    def get_rates(self) -> dict[str, Rate]:
        try:
            response = requests.get(
                self._url,
                headers=self.HEADERS,
                timeout=self._timeout,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise ProviderError(
                f"Не удалось получить данные ЦБ РФ: {exc}"
            ) from exc

        return self.parse(response.content)

    @staticmethod
    def parse(xml_data: bytes) -> dict[str, Rate]:
        """Разобрать XML с курсами валют."""

        try:
            root = ET.fromstring(xml_data)
            on_date = datetime.strptime(
                root.attrib["Date"], "%d.%m.%Y"
            ).date()
        except (ET.ParseError, KeyError, ValueError) as exc:
            raise ProviderError(
                f"Некорректный ответ ЦБ РФ: {exc}"
            ) from exc

        rates: dict[str, Rate] = {}

        for valute in root.findall("Valute"):
            try:
                code = valute.findtext("CharCode", "").strip()
                name = valute.findtext("Name", "").strip()

                num_code = valute.findtext("NumCode")
                if num_code is not None:
                    num_code = num_code.strip() or None

                nominal = int(
                    valute.findtext("Nominal", "0")
                )

                value = Decimal(
                    valute.findtext("Value", "0").replace(",", ".")
                )

                rate = Rate(
                    code,
                    name,
                    nominal,
                    value,
                    on_date,
                    num_code=num_code,
                )

                rates[code] = rate

            except (ValueError, InvalidOperation, ValidationError):
                continue

        return rates


class StaticRateProvider(RateProvider):
    """Поставщик курсов из готового списка."""

    def __init__(self, rates: Iterable[Rate]) -> None:
        self._rates = {
            rate.code: rate for rate in rates
        }

    def get_rates(self) -> dict[str, Rate]:
        return dict(self._rates)

    @classmethod
    def demo(cls) -> StaticRateProvider:
        """Пример курсов для проверки программы."""

        today = date.today()

        return cls([
            Rate("USD", "Доллар США", 1, Decimal("80.0000"),
                 today, num_code="840"),
            Rate("EUR", "Евро", 1, Decimal("93.0000"),
                 today, num_code="978"),
            Rate("CNY", "Китайский юань", 1, Decimal("11.2000"),
                 today, num_code="156"),
            Rate("JPY", "Японских иен", 100, Decimal("53.0000"),
                 today, num_code="392"),
        ])
