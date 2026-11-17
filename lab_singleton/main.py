import time
import requests
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from xml.etree import ElementTree as ET


CBR_URL = "https://www.cbr.ru/scripts/XML_daily.asp"


def get_currencies(currencies_ids_lst: list) -> list:
    """Получение выбранных валют с сайта ЦБ РФ."""

    response = requests.get(CBR_URL, timeout=10)
    response.raise_for_status()

    currencies = []
    root = ET.fromstring(response.content)

    for item in root.findall("Valute"):
        currency_id = item.get("ID")

        if currency_id in currencies_ids_lst:
            name = item.findtext("Name")
            code = item.findtext("CharCode")
            value = item.findtext("Value")
            nominal = item.findtext("Nominal")

            # Разделяем курс на целую и дробную части
            parts = value.replace(",", ".").split(".")
            integer_part = parts[0]
            fractional_part = parts[1] if len(parts) > 1 else "0"

            currencies.append({
                code: (
                    name,
                    (integer_part, fractional_part),
                    nominal
                )
            })

    # Если указанного ID нет, возвращаем его со значением None
    for currency_id in currencies_ids_lst:
        if not any(
            currency_id == item.get("ID")
            for item in root.findall("Valute")
        ):
            currencies.append({currency_id: None})

    return currencies


class SingletonMeta(type):
    """Метакласс, который не позволяет создавать несколько объектов."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)

        return cls._instances[cls]


class CurrenciesLst(metaclass=SingletonMeta):
    """Класс для получения и отображения курсов валют."""

    def __init__(self, min_interval=1.0):
        self.__cur_lst = []
        self.__min_interval = min_interval
        self.__last_request_time = 0.0

    def get_cur_lst(self):
        return self.__cur_lst

    def set_cur_lst(self, value):
        self.__cur_lst = value

    def get_min_interval(self):
        return self.__min_interval

    def set_min_interval(self, value):
        if value < 0:
            raise ValueError("Интервал не может быть отрицательным")

        self.__min_interval = value

    def fetch_data(self, ids_list):
        """Запрос курсов с ограничением частоты обращений."""

        current_time = time.monotonic()
        passed_time = current_time - self.__last_request_time

        if passed_time < self.__min_interval:
            time.sleep(self.__min_interval - passed_time)

        self.__last_request_time = time.monotonic()
        self.__cur_lst = get_currencies(ids_list)

        return self.__cur_lst

    def visualize_currencies(self):
        """Создание графика валют и сохранение в файл."""

        codes = []
        rates = []

        for currency in self.__cur_lst:
            for code, data in currency.items():
                if data is None:
                    continue

                codes.append(code)

                whole, fraction = data[1]
                nominal = int(data[2])

                rate = float(f"{whole}.{fraction}") / nominal
                rates.append(rate)

        if not codes:
            print("Нет данных для построения графика")
            return

        fig, ax = plt.subplots(figsize=(8, 5))

        ax.bar(codes, rates, color="steelblue")
        ax.set_title("Курсы валют по данным ЦБ РФ")
        ax.set_xlabel("Валюта")
        ax.set_ylabel("Стоимость одной единицы в рублях")

        for i, value in enumerate(rates):
            ax.text(
                i,
                value,
                f"{value:.2f}",
                ha="center",
                va="bottom"
            )

        fig.tight_layout()
        fig.savefig("currencies.jpg")
        plt.close(fig)

        print("График сохранён в currencies.jpg")


if __name__ == "__main__":
    tracker = CurrenciesLst(min_interval=1.0)

    currency_ids = ["R01035", "R01335", "R01700J"]

    result = tracker.fetch_data(currency_ids)

    print("Полученные курсы валют:")
    for currency in result:
        print(currency)

    tracker.visualize_currencies()