from datetime import datetime

import pandas as pd
from pandas import DataFrame


def hello_user() -> str:
    """Функция формирует приветствие в зависимости от текущего времени суток"""
    current_time = datetime.now().strftime("%H:%M:%S")

    if "06:00:00" <= current_time <= "11:59:59":
        return "Доброе утро!"
    elif "12:00:00" <= current_time <= "17:59:59":
        return "Добрый день!"
    elif "18:00:00" <= current_time <= "20:59:59":
        return "Добрый вечер!"
    else:
        return "Доброй ночи!"


def read_xlsx(path_to_excel: str) -> DataFrame:
    """Функция читает файл excel и возвращает DataFrame"""

    data = pd.read_excel(path_to_excel)

    return data


def get_range_of_date(date: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")) -> tuple:
    """Функция принимает на вход дату и возвращает кортеж из двух дат - начало месяца и текущая дата"""

    date_end = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    date_start = date_end.replace(day=1, hour=0, minute=0, second=0)

    return date_start, date_end


def get_card_info(df: DataFrame, date_start: datetime, date_end: datetime) -> list[dict]:
    """
    Функция принимает DataFrame и две даты (период),
    а возвращает список словарей с данными для каждой карты,
    включающими сумму расходов и кэшбека в указанный период.
    """

    df_by_date = df[(pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S")
                     .between(date_start, date_end)) & (df["Сумма платежа"] < 0)]
    df_by_card = (
        df_by_date[df_by_date["Номер карты"].notna()]
        .groupby("Номер карты")
        .agg({"Сумма операции с округлением": "sum"})
        .reset_index()
    )

    cards = []
    for index, row in df_by_card.iterrows():
        cashback = round(row["Сумма операции с округлением"] // 100)
        card_dict = {
            "last_digits": row["Номер карты"].replace("*", ""),
            "total_spent": round(row["Сумма операции с округлением"], 2),
            "cashback": cashback,
        }
        cards.append(card_dict)

    return cards


def get_top_transactions(df: DataFrame, date_start: datetime, date_end: datetime) -> list[dict]:
    """ """

    df_by_date = df[(pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S")
                     .between(date_start, date_end)) & (df["Сумма платежа"] < 0)]
    df_by_values = df_by_date.sort_values(by='Сумма операции с округлением', ascending=False)

    top_transactions = []
    for index, row in df_by_values.iterrows():
        if len(top_transactions) == 5:
            break
        else:
            transactions_dict = {
                "date": row["Дата платежа"],
                "amount": row["Сумма операции с округлением"],
                "category": row["Категория"],
                "description": row["Описание"]
            }
            top_transactions.append(transactions_dict)

    return top_transactions, df_by_values


if __name__ == "__main__":
    path = "../data/operations.xlsx"
    transactions = read_xlsx(path)
    date_1, date_2 = get_range_of_date("2020-03-2 12:00:00")
    print(date_1, date_2)
    print((hello_user()))
    print(get_card_info(transactions, date_1, date_2))
    print(get_top_transactions(transactions, date_1, date_2))
