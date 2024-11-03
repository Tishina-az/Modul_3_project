import json
from datetime import datetime

from src.utils import (current_exchange_rate, current_values_stocks, get_card_info, get_range_of_date,
                       get_top_transactions, hello_user, read_xlsx)

path_to_file = "../data/operations.xlsx"
path_to_json = "../user_settings.json"


def main_page(date: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")) -> str:
    """
    Функция 'Главной страницы', принимающая на вход дату и выдающая json-ответ,
    с выборкой транзакций, курсов валют и стоимости акций.
    """

    transactions = read_xlsx(path_to_file)
    date_1, date_2 = get_range_of_date(date)
    data = {
        "greeting": hello_user(),
        "cards": get_card_info(transactions, date_1, date_2),
        "top_transactions": get_top_transactions(transactions, date_1, date_2),
        "currency_rates": current_exchange_rate(path_to_json),
        "stock_prices": current_values_stocks(path_to_json)
    }

    return json.dumps(data, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    print(main_page("2020-03-14 12:00:00"))
