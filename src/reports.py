import logging
import os
from datetime import datetime
from functools import wraps
from typing import Callable, Any

import pandas as pd


# path_to_csv = os.path.join(os.path.dirname(__file__), "../data/example.csv")
path_to_json = os.path.join(os.path.dirname(__file__), "../data/example.json")

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(filename)s:%(funcName)s: %(message)s",
    filename=os.path.join(os.path.dirname(__file__), "../logs/reports.log"),
    filemode="a",
)

rep_logger = logging.getLogger()


def writing_report_to_file(file_name: str) -> Callable:
    def wrapper(function: Callable) -> Callable:
        @wraps(function)
        def inner(*args: Any, **kwargs: Any) -> Any:
            result = function(*args, **kwargs)
            # result.to_csv(file_name, index=False)
            result.to_json(file_name, orient='records', force_ascii=False, indent=4)
            rep_logger.debug("Запись результата в файл.")
            return result

        return inner

    return wrapper


@writing_report_to_file(path_to_json)
def spending_by_category(transactions: pd.DataFrame, category: str, date: Any = None) -> pd.DataFrame:
    """Функция возвращает траты по заданной категории за последние три месяца (от переданной даты)."""

    rep_logger.info("Запуск функции...")
    if date is None:
        rep_logger.warning("Получение текущей даты.")
        date = datetime.now()
    else:
        rep_logger.warning("Получение даты пользователя.")
        date = pd.to_datetime(date, format="%Y-%m-%d %H:%M:%S")

    date_start = date - pd.DateOffset(months=3)

    rep_logger.debug("Формирование отчета по транзакциям.")
    df_by_date_category = transactions[
        (pd.to_datetime(transactions["Дата операции"], format="%d.%m.%Y %H:%M:%S").between(date_start, date))
        & (transactions["Категория"] == category)
    ]

    rep_logger.info("Функция успешно завершена.")
    return df_by_date_category
