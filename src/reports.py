import os
from datetime import datetime
from functools import wraps
from typing import Optional

import pandas as pd

from src.utils import read_xlsx

path_to_csv = os.path.join(os.path.dirname(__file__), "../data/example.csv")


def writing_report_to_file(file_name):
    def wrapper(function):
        @wraps(function)
        def inner(*args, **kwargs):
            result = function(*args, **kwargs)
            result.to_csv(file_name, index=False)
            return result

        return inner

    return wrapper


@writing_report_to_file(path_to_csv)
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """Функция возвращает траты по заданной категории за последние три месяца (от переданной даты)."""

    if date is None:
        date = datetime.now("%Y-%m-%d %H:%M:%S")
    else:
        date = pd.to_datetime(date, format="%Y-%m-%d %H:%M:%S")

    date_start = date - pd.DateOffset(months=3)

    df_by_date_category = transactions[
        (pd.to_datetime(transactions["Дата операции"], format="%d.%m.%Y %H:%M:%S").between(date_start, date))
        & (transactions["Категория"] == category)
    ]

    return df_by_date_category


if __name__ == "__main__":
    data = read_xlsx("../data/operations.xlsx")
    spending_by_category(data, "Супермаркеты", "2021-12-04 13:44:39")
