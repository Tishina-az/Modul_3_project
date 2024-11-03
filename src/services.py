import json

import pandas as pd
from pandas import DataFrame

from src.utils import read_xlsx


def analysis_cashback(data: DataFrame, year: int, month: int) -> str:
    """ """

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

    return json.dumps(category_cashback, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    path_to_file = "../data/operations.xlsx"
    transactions = read_xlsx(path_to_file)
    print(analysis_cashback(transactions, 2021, 4))
