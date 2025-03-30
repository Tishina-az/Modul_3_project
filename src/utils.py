import json
import logging
import os
from datetime import datetime

import pandas as pd
import requests
from dotenv import load_dotenv
from pandas import DataFrame

load_dotenv()
api_stock = os.getenv("API_KEY_STOCK")

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(filename)s:%(funcName)s: %(message)s",
    filename=os.path.join(os.path.dirname(__file__), "../logs/utils.log"),
    filemode="a",
)

utils_logger = logging.getLogger()


def hello_user() -> str:
    """Функция формирует приветствие в зависимости от текущего времени суток"""

    utils_logger.info("Запуск функции...")
    current_time = datetime.now()
    current_hour = current_time.hour
    greeting = ""
    if 6 <= current_hour < 12:
        greeting += "Доброе утро!"
    elif 12 <= current_hour < 18:
        greeting += "Добрый день!"
    elif 18 <= current_hour < 21:
        greeting += "Добрый вечер!"
    else:
        greeting += "Доброй ночи!"

    utils_logger.info("Успешное завершение работы!")
    return greeting


def read_xlsx(path_to_excel: str) -> DataFrame:
    """Функция читает файл excel и возвращает DataFrame"""

    utils_logger.info("Запуск функции...")
    try:
        data = pd.read_excel(path_to_excel)
        utils_logger.info("Файл успешно прочитан!")
        return data
    except Exception as e:
        utils_logger.error(f"При чтении файла возникла ошибка - {e}.")
        raise Exception(f"При чтении файла возникла ошибка - {e}.")


def get_range_of_date(date: str = None) -> tuple:
    """Функция принимает на вход дату и возвращает кортеж из двух дат - начало месяца и текущая дата"""

    try:
        date_end = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        date_start = date_end.replace(day=1, hour=0, minute=0, second=0)
        utils_logger.info("Функция успешно завершилась!")
        return date_start, date_end
    except ValueError as e:
        utils_logger.error(f"Возникла ошибка ValueError - {e}. Проверьте корректность ввода даты!")
        print("Неверный формат даты! Введите дату в формате: YYYY-MM-DD HH:MM:SS")
        return ()


def get_card_info(df: pd.DataFrame, date_start: datetime, date_end: datetime) -> list[dict]:
    """
    Функция принимает DataFrame и две даты (период),
    а возвращает список словарей с данными для каждой карты,
    включающими сумму расходов и кэшбека в указанный период.
    """

    utils_logger.info("Запуск функции...")
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

    utils_logger.info("Успешное завершение функции!")
    return cards


def get_top_transactions(df: pd.DataFrame, date_start: datetime, date_end: datetime) -> list[dict]:
    """Функция, возвращает топ-5 транзакций по сумме платежа"""

    utils_logger.info("Запуск функции...")
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

    utils_logger.info("Успешное завершение функции!")
    return top_transactions


def current_exchange_rate(path_to_json: str) -> list[dict]:
    """Функция принимает путь до файла со списком валют и возвращает список с текущим курсом"""

    utils_logger.info("Запуск функции...")
    utils_logger.warning("Чтение файла json.")
    with open(path_to_json) as f:
        data_cur = json.load(f)
    currency_list = data_cur.get("user_currencies")

    currency_rates = []
    response = requests.get("https://www.cbr-xml-daily.ru/daily_json.js")
    status_code = response.status_code
    if status_code != 200:
        utils_logger.error(f"Ошибка {status_code}, при обращении к API.")
        raise ValueError(f"Ошибка {status_code} при получении текущего курса валют!")
    utils_logger.info("Данные от API получены.")
    data = response.json()
    for currency in currency_list:
        currency_data = data["Valute"].get(currency)
        if not currency_data:
            raise ValueError(f"Не найдены данные для валюты: {currency}!")
        else:
            currency_rates.append({"currency": currency, "rate": round(currency_data["Value"], 2)})

    utils_logger.info("Успешное завершение функции!")
    return currency_rates


def current_values_stocks(path_to_json: str) -> list[dict]:
    """Функция принимает путь к списку тикеров акция и возвращает списко словарей со стоимостью"""

    utils_logger.info("Запуск функции...")
    utils_logger.warning("Чтение файла json.")
    with open(path_to_json) as f:
        data_st = json.load(f)
    stocks_list = data_st.get("user_stocks")

    stock_prices = []
    for stock in stocks_list:
        url = f"https://financialmodelingprep.com/api/v3/quote/{stock}?apikey={api_stock}"
        response = requests.get(url)
        status_code = response.status_code
        if status_code != 200:
            utils_logger.error(f"Ошибка {status_code}, при обращении к API.")
            raise ValueError(f"Ошибка {status_code}, попробуйте ещё раз!")
        else:
            utils_logger.info("Данные от API получены.")
            data = response.json()
            stock_prices.append({"stock": stock, "price": data[0]["price"]})

    utils_logger.info("Успешное завершение функции!")
    return stock_prices
