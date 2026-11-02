
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
    """Общий интерфейс для всех поставщиков."""

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
    """Получение курсов из XML ЦБ РФ."""

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
        self._timeout = self.TIMEOUT if timeout is None else timeout
        self._skipped_count = 0

    @property
    def skipped_count(self) -> int:
        return self._skipped_count

    def get_rates(self) -> dict[str, Rate]:
        try:
            response = requests.get(
                self._url,
                headers=self.HEADERS,
                timeout=self._timeout,
            )
            response.raise_for_status()

        except requests.Timeout as exc:
            raise ProviderError(
                f"Сервер ЦБ РФ не ответил за {self._timeout} секунд"
            ) from exc

        except requests.RequestException as exc:
            raise ProviderError(
                f"Не удалось получить данные ЦБ РФ: {exc}"
            ) from exc

        return self._parse_xml(response.content)

    def _parse_xml(self, xml_data: bytes) -> dict[str, Rate]:
        rates, skipped = self._parse_with_count(xml_data)
        self._skipped_count = skipped
        return rates

    @staticmethod
    def _parse_with_count(
        xml_data: bytes,
    ) -> tuple[dict[str, Rate], int]:
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
        skipped = 0

        for valute in root.findall("Valute"):
            try:
                code = valute.findtext("CharCode", "").strip()
                name = valute.findtext("Name", "").strip()

                num_code = valute.findtext("NumCode")
                if num_code is not None:
                    num_code = num_code.strip() or None

                nominal = int(valute.findtext("Nominal", "0"))

                value = Decimal(
                    valute.findtext("Value", "0").replace(",", ".")
                )

                if not code or not name:
                    raise ValueError("Нет кода или названия")

                rates[code] = Rate(
                    code,
                    name,
                    nominal,
                    value,
                    on_date,
                    num_code=num_code,
                )

            except (ValueError, InvalidOperation, ValidationError):
                skipped += 1

        return rates, skipped

    @staticmethod
    def parse(xml_data: bytes) -> dict[str, Rate]:
        rates, _ = CbrXmlProvider._parse_with_count(xml_data)
        return rates


class StaticRateProvider(RateProvider):
    """Готовые курсы для работы без интернета."""

    def __init__(self, rates: Iterable[Rate]) -> None:
        self._rates = {rate.code: rate for rate in rates}

    def get_rates(self) -> dict[str, Rate]:
        return dict(self._rates)

    @classmethod
    def demo(cls) -> StaticRateProvider:
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


class CbrJsonProvider(RateProvider):
    """Получение курсов валют из JSON."""

    URL = "https://www.cbr-xml-daily.ru/daily_json.js"
    TIMEOUT = 10

    def __init__(
        self,
        url: str | None = None,
        timeout: float | None = None,
    ) -> None:
        self._url = url or self.URL
        self._timeout = self.TIMEOUT if timeout is None else timeout

    def get_rates(self) -> dict[str, Rate]:
        """Загрузить курсы в формате JSON."""
        try:
            response = requests.get(
                self._url,
                timeout=self._timeout,
            )
            response.raise_for_status()
            data = response.json()

        except requests.Timeout as exc:
            raise ProviderError(
                f"Сервер JSON не ответил за {self._timeout} секунд"
            ) from exc

        except requests.RequestException as exc:
            raise ProviderError(
                f"Не удалось получить JSON: {exc}"
            ) from exc

        except ValueError as exc:
            raise ProviderError(
                "Сервер вернул некорректный JSON"
            ) from exc

        return self.parse(data)

    @staticmethod
    def parse(data: dict) -> dict[str, Rate]:
        """Преобразовать JSON в словарь курсов."""

        try:
            on_date = datetime.fromisoformat(
                data["Date"].replace("Z", "+00:00")
            ).date()

            currencies = data["Valute"]

            if not isinstance(currencies, dict):
                raise ValueError("Valute должен быть словарём")

        except (KeyError, TypeError, ValueError) as exc:
            raise ProviderError(
                f"Некорректные данные JSON: {exc}"
            ) from exc

        rates: dict[str, Rate] = {}

        for code, item in currencies.items():
            try:
                rate = Rate(
                    code=item["CharCode"],
                    name=item["Name"],
                    nominal=int(item["Nominal"]),
                    value=Decimal(str(item["Value"])),
                    on_date=on_date,
                    num_code=item.get("NumCode"),
                )

                rates[rate.code] = rate

            except (
                KeyError,
                TypeError,
                ValueError,
                InvalidOperation,
                ValidationError,
            ):
                continue

        return rates
