from src.reports import spending_by_category
from src.services import analysis_cashback
from src.utils import read_xlsx
from src.views import main_page


path_to_file = "../data/operations.xlsx"
transactions = read_xlsx(path_to_file)


def main():
    """Главная функция, для проверки всех функциональностей проекта"""
    print(
        """
        Какую страницу открыть:
        1 - Главная;
        2 - Сервис;
        3 - Отчёты.
    """
    )
    try:
        user_choice = int(input("Введите цифру от 1 до 3: "))
        if user_choice == 1:
            print("Запуск страницы 'Главная': ")
            return main_page("2018-12-12 12:00:00")
        elif user_choice == 2:
            print("Запуск страницы 'Сервисы': ")
            return analysis_cashback(transactions, 2018, 6)
        elif user_choice == 3:
            print("Запуск страницы 'Отчёты': ")
            return spending_by_category(transactions, "Супермаркеты", "2021-06-04 13:44:39")
    except ValueError as e:
        return print(
            f"""
        Ошибка ValueError: {e}.
        Введён неверный параметр!
        """
        )


if __name__ == "__main__":
    print(main())
