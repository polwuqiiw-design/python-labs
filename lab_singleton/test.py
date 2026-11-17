import unittest

from main import CurrenciesLst


class TestCurrenciesLst(unittest.TestCase):
    """Проверки работы приложения с курсами валют."""

    @classmethod
    def setUpClass(cls):
        # Создаём объект один раз для всех тестов
        cls.tracker = CurrenciesLst(min_interval=0.0)
        cls.tracker.set_min_interval(0.0)

    def test_unknown_currency(self):
        """Проверяем, как программа обрабатывает неверный ID."""

        result = self.tracker.fetch_data(["R9999"])

        self.assertEqual(result, [{"R9999": None}])

    def test_gbp_currency(self):
        """Проверяем название и курс британского фунта."""

        result = self.tracker.fetch_data(["R01035"])

        self.assertTrue(len(result) > 0)

        currency = result[0]
        self.assertIn("GBP", currency)

        name, value, nominal = currency["GBP"]

        self.assertIn("Фунт стерлингов", name)

        whole, fraction = value
        rate = float(f"{whole}.{fraction}")

        self.assertGreaterEqual(rate, 0)
        self.assertLessEqual(rate, 999)

        self.assertGreater(int(nominal), 0)

    def test_kzt_currency(self):
        """Проверяем название и курс казахстанского тенге."""

        result = self.tracker.fetch_data(["R01335"])

        self.assertTrue(len(result) > 0)

        currency = result[0]
        self.assertIn("KZT", currency)

        name, value, nominal = currency["KZT"]

        self.assertIn("Тенге", name)

        whole, fraction = value
        rate = float(f"{whole}.{fraction}")

        self.assertGreaterEqual(rate, 0)
        self.assertLessEqual(rate, 999)

        self.assertGreater(int(nominal), 0)

    def test_singleton(self):
        """Убеждаемся, что повторно возвращается тот же объект."""

        first = CurrenciesLst()
        second = CurrenciesLst()

        self.assertIs(first, second)


if __name__ == "__main__":
    unittest.main()
