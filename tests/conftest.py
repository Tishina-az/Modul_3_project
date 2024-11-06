import json
from datetime import datetime
from unittest.mock import mock_open, patch

import pandas as pd
import pytest


@pytest.fixture
def sample_dataframe():
    data = {
        "Дата операции": [
            "05.10.2023 14:30:00",
            "10.10.2023 08:15:00",
            "12.10.2023 09:45:00",
            "15.10.2023 10:10:00",
            "20.10.2023 11:00:00",
            "25.10.2023 12:00:00",
        ],
        "Номер карты": ["*5678", "*5678", "*5432", "*5678", "*5432", "*5678"],
        "Сумма платежа": [-150.00, -200.00, -50.00, -100.00, -300.00, -50.00],
        "Сумма операции с округлением": [150.00, 200.00, 50.00, 100.00, 300.00, 50.00],
        "Категория": ["Еда", "Транспорт", "Развлечения", "Еда", "Транспорт", "Развлечения"],
        "Описание": [
            "Обед в кафе",
            "Поездка на такси",
            "Билеты в кино",
            "Ужин в ресторане",
            "Поездка на автобусе",
            "Посещение музея",
        ],
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_empty_dataframe():
    empty_data = pd.DataFrame(
        columns=["Дата операции", "Номер карты", "Сумма платежа", "Сумма операции с округлением"]
    )
    return empty_data


@pytest.fixture
def list_cards():
    return [
        {"last_digits": "5432", "total_spent": 350.0, "cashback": 3},
        {"last_digits": "5678", "total_spent": 450.0, "cashback": 4},
    ]


@pytest.fixture
def list_top_transactions():
    return [
        {'date': '20.10.2023', 'amount': 300.0, 'category': 'Транспорт', 'description': 'Поездка на автобусе'},
        {'date': '10.10.2023', 'amount': 200.0, 'category': 'Транспорт', 'description': 'Поездка на такси'},
        {'date': '05.10.2023', 'amount': 150.0, 'category': 'Еда', 'description': 'Обед в кафе'},
        {'date': '15.10.2023', 'amount': 100.0, 'category': 'Еда', 'description': 'Ужин в ресторане'},
        {'date': '12.10.2023', 'amount': 50.0, 'category': 'Развлечения', 'description': 'Билеты в кино'}
    ]


@pytest.fixture
def date_start_end():
    date_start = datetime(2023, 10, 1, 0, 0)
    date_end = datetime(2023, 10, 20, 12, 0)
    return date_start, date_end


@pytest.fixture
def mock_json_file():
    data = {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL"]}
    json_data = json.dumps(data)
    with patch("builtins.open", mock_open(read_data=json_data)):
        yield "fake_path.json"
