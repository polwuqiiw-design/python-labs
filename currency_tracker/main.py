
"""Консольный интерфейс трекера курсов валют."""

import sys

from app.exceptions import AppError, ProviderError
from app.providers import CbrXmlProvider, RateProvider, StaticRateProvider
from app.services import CurrencyTracker


MENU = """
1. Зарегистрироваться
2. Список валют
3. Подписаться на валюту
4. Отписаться от валюты
5. Мои курсы
6. Подписчики валюты
0. Выход
"""


def choose_provider() -> RateProvider:
    """Выбрать источник курсов валют."""
    if "--offline" in sys.argv:
        return StaticRateProvider.demo()

    return CbrXmlProvider()


def ask_user_id() -> int:
    """Запросить номер пользователя."""
    return int(input("Ваш id: "))


def create_tracker() -> CurrencyTracker | None:
    """Создать трекер и загрузить валюты."""
    tracker = CurrencyTracker(choose_provider())

    # try: пробуем получить курсы валют
    try:
        count = tracker.sync_currencies()

    # except: обрабатываем ошибку получения данных
    except ProviderError as exc:
        print(f"Ошибка: {exc}")

        answer = input(
            "Перейти в автономный режим? (y/n): "
        ).strip().lower()

        if answer != "y":
            return None

        tracker = CurrencyTracker(StaticRateProvider.demo())
        count = tracker.sync_currencies()
        print(f"Автономный режим. Загружено валют: {count}")

    # else: выполняется при успешной первоначальной загрузке
    else:
        print(f"Загружено валют: {count}")

    # finally: выполняется независимо от результата
    finally:
        print("Синхронизация завершена")

    return tracker


def main() -> None:
    """Запустить консольную программу."""
    tracker = create_tracker()

    if tracker is None:
        return

    while True:
        print(MENU)
        choice = input("Выберите пункт: ").strip()

        try:
            if choice == "1":
                user = tracker.register_user(
                    input("Имя: "),
                    input("Email: "),
                )
                print(
                    f"Зарегистрирован: {user} (id={user.id})"
                )

            elif choice == "2":
                for currency in tracker.currencies:
                    print(currency)

            elif choice == "3":
                tracker.subscribe(
                    ask_user_id(),
                    input("Код валюты: "),
                )
                print("Подписка оформлена")

            elif choice == "4":
                tracker.unsubscribe(
                    ask_user_id(),
                    input("Код валюты: "),
                )
                print("Подписка отменена")

            elif choice == "5":
                user_id = ask_user_id()

                try:
                    rates = tracker.get_user_rates(user_id)
                except ProviderError as exc:
                    print(f"Ошибка получения курсов: {exc}")
                    continue

                for rate in sorted(rates, reverse=True):
                    print(rate)

            elif choice == "6":
                code = input("Код валюты: ")
                subscribers = tracker.get_subscribers(code)

                if subscribers:
                    for user in subscribers:
                        print(user)
                else:
                    print("На эту валюту пока никто не подписан")

            elif choice == "0":
                break

            else:
                print("Нет такого пункта")

        except AppError as exc:
            print(f"Ошибка: {exc}")

        except ValueError:
            print("Ошибка: id должен быть целым числом")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        print("\nДо свидания")
