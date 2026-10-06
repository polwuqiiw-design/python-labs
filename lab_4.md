# Лабораторная работа №4

## Задание

1. Написать функцию `calculate`, которая принимает два числа и выполняет деление первого числа на второе. Точность `epsilon` по умолчанию равна `0.0001`.
2. Написать функцию `load_params`, которая считывает значение `epsilon` из файла `settings.ini`.
3. Написать тесты с использованием `unittest`.

## Основная программа

Файл `main.py`:

```python
import configparser


def calculate(a, b, epsilon=0.0001):
    """Делит первое число на второе с заданной точностью."""
    if b == 0:
        raise ZeroDivisionError("Деление на ноль невозможно")

    if not 10**-9 <= epsilon <= 10**-1:
        raise ValueError("Некорректное значение epsilon")

    result = a / b
    return round(result, 10)


def load_params(filename="settings.ini"):
    """Считывает значение epsilon из файла настроек."""
    config = configparser.ConfigParser()
    config.read(filename)

    epsilon = float(config["settings"]["epsilon"])

    if not 10**-9 <= epsilon <= 10**-1:
        raise ValueError("Некорректное значение epsilon")

    return epsilon


epsilon = load_params()
print(calculate(1, 2, epsilon=epsilon))
```

## Файл настроек

Файл `settings.ini`:

```ini
[settings]
epsilon = 0.0001
```

## Тестирование

Файл `test_main.py`:

```python
import os
import unittest

from main import calculate, load_params


class TestCalculate(unittest.TestCase):

    def test_half(self):
        self.assertEqual(calculate(1, 2, epsilon=0.1), 0.5)

    def test_small_number(self):
        self.assertEqual(calculate(1, 1000, epsilon=0.001), 0.001)

    def test_zero(self):
        with self.assertRaises(ZeroDivisionError):
            calculate(1, 0)


class TestLoadParams(unittest.TestCase):

    def test_file_reading(self):
        self.assertTrue(os.path.exists("settings.ini"))

    def test_epsilon_range(self):
        epsilon = load_params()
        self.assertTrue(10**-9 <= epsilon <= 10**-1)

    def test_epsilon_format(self):
        epsilon = load_params()
        self.assertIsInstance(epsilon, float)


if __name__ == "__main__":
    unittest.main()
```

## Запуск тестов

```bash
python -m unittest test_main.py
```

Если все тесты выполнены успешно, программа выводит:

```text
......
----------------------------------------------------------------------
Ran 6 tests

OK
```

## Вывод

В ходе работы были созданы функции для деления чисел и чтения параметра `epsilon` из конфигурационного файла. Для проверки работы программы были написаны тесты с использованием `unittest`.
