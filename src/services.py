import json
import logging
import os

import pandas as pd


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(filename)s:%(funcName)s: %(message)s",
    filename=os.path.join(os.path.dirname(__file__), "../logs/utils.log"),
    filemode="a",
)

serv_logger = logging.getLogger()


def analysis_cashback(data: pd.DataFrame, year: int, month: int) -> str:
    """Функция принимает файл, год и месяц, и выдает анализ кэшбека по категориям в виде json-ответа"""

    serv_logger.info("Запуск функции...")
    serv_logger.warning("Формирование DataFrame.")
    df_by_date = data[
        (pd.to_datetime(data["Дата операции"], format="%d.%m.%Y %H:%M:%S").dt.year == year)
        & (pd.to_datetime(data["Дата операции"], format="%d.%m.%Y %H:%M:%S").dt.month == month)
    ]

    data_exc = df_by_date[~df_by_date["Категория"].isin(["Переводы", "Пополнения"])]
    df_cashback = data_exc.groupby("Категория").agg({"Сумма операции с округлением": "sum"}).reset_index()

    category_cashback = {}
    for index, row in df_cashback.iterrows():
        cashback = round(row["Сумма операции с округлением"] // 100)
        category_cashback[row["Категория"]] = cashback

    serv_logger.info("Успешное завершение выполнения функции.")
    return json.dumps(category_cashback, ensure_ascii=False, indent=4)
