import json
import os
from datetime import datetime

import pandas as pd
import requests
from dotenv import load_dotenv
from pandas import DataFrame

load_dotenv()
api_stock = os.getenv("API_KEY_STOCK")


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

    df_by_date = df[
        (pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S").between(date_start, date_end))
        & (df["Сумма платежа"] < 0)
    ]
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

    df_by_date = df[
        (pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S").between(date_start, date_end))
        & (df["Сумма платежа"] < 0)
    ]
    df_by_values = df_by_date.sort_values(by="Сумма операции с округлением", ascending=False)

    top_transactions = []
    for index, row in df_by_values.iterrows():
        if len(top_transactions) == 5:
            break
        else:
            transactions_dict = {
                "date": row["Дата операции"][:10],
                "amount": row["Сумма операции с округлением"],
                "category": row["Категория"],
                "description": row["Описание"],
            }
            top_transactions.append(transactions_dict)

    return top_transactions


def current_exchange_rate(path_to_json: str) -> list[dict]:
    """Функция принимает путь до файла со списком валют и возвращает список с текущим курсом"""

    with open(path_to_json) as f:
        data_cur = json.load(f)
    currency_list = data_cur.get("user_currencies")

    currency_rates = []
    response = requests.get("https://www.cbr-xml-daily.ru/daily_json.js")
    if response.status_code != 200:
        raise ValueError("Ошибка при получении текущего курса валют!")
    data = response.json()
    for currency in currency_list:
        currency_data = data["Valute"].get(currency)
        currency_rates.append({"currency": currency, "rate": round(currency_data["Value"], 2)})
        if not currency_data:
            raise ValueError(f"Не найдены данные для валюты: {currency}!")

    return currency_rates


def current_values_stocks(path_to_json: str) -> list[dict]:
    """Функция принимает путь к списку тикеров акция и возвращает списко словарей со стоимостью"""

    with open(path_to_json) as f:
        data_st = json.load(f)
    stocks_list = data_st.get("user_stocks")

    stock_prices = []
    for stock in stocks_list:
        url = f"https://financialmodelingprep.com/api/v3/quote/{stock}?apikey={api_stock}"
        response = requests.get(url)
        data = response.json()
        stock_prices.append({"stock": stock, "price": data[0]["price"]})

    return stock_prices
