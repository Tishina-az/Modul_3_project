from datetime import datetime
from unittest.mock import patch

import pandas as pd
import pytest

from src.utils import (current_exchange_rate, current_values_stocks, get_card_info, get_range_of_date,
                       get_top_transactions, read_xlsx)

# @pytest.mark.parametrize("mocked_time, expected_output", [
#    (6, "Доброе утро!"),
#     (12, "Добрый день!"),
#     (18, "Добрый вечер!"),
#     (21, "Доброй ночи!"),
#     (22, "Доброй ночи!"),
#     (5, "Доброй ночи!"),
# ])
# @patch('datetime.datetime')
# def test_hello_user(mock_datetime, mocked_time, expected_output):
#     """"""
#     mock_datetime.now.return_value.hour.return_value = mocked_time
#     assert hello_user() == expected_output


@patch("pandas.read_excel")
def test_read_xlsx(mock_read_excel, sample_dataframe) -> None:
    """Тестируем успешное чтение файла"""

    mock_read_excel.return_value = sample_dataframe
    result = read_xlsx("example.xlsx")
    assert isinstance(result, pd.DataFrame)


@patch("pandas.read_excel")
def test_read_xlsx_error(mock_read, capsys) -> None:
    """Тестирует поведение функции при возникшей ошибке чтения файла"""
    mock_read.side_effect = Exception
    try:
        read_xlsx("example.xlsx")
    except Exception as e:
        assert f"При чтении файла возникла ошибка - {e}."


def test_get_range_of_date_valid():
    """Тестируем функцию возврата диапазона дат, при корректной дате на входе"""
    date_input = "2023-10-05 14:30:00"
    expected_start = datetime(2023, 10, 1, 0, 0, 0)
    expected_end = datetime(2023, 10, 5, 14, 30, 0)
    assert get_range_of_date(date_input) == (expected_start, expected_end)


def test_get_range_of_date_empty_string():
    """Тестируем функцию возврата диапазона дат, при пустой строке на входе"""
    result = get_range_of_date("")
    assert result == ()


def test_get_card_info_valid(date_start_end, sample_dataframe, list_cards):
    """Тест функции возврата списка словарей с расходами и кэшбеком по каждой карте"""
    date_start, date_end = date_start_end
    expected_output = list_cards
    result = get_card_info(sample_dataframe, date_start, date_end)
    assert result == expected_output


def test_get_card_info_empty_dataframe(date_start_end, sample_empty_dataframe):
    """Тест возврата пустого списка при передаче пустого датафрейма"""
    date_start, date_end = date_start_end
    result = get_card_info(sample_empty_dataframe, date_start, date_end)
    assert result == []


def test_get_top_transactions_valid(date_start_end, sample_dataframe, list_top_transactions):
    """Тест функции возврата списка словарей, содержащих топ-5 расходов"""
    date_start, date_end = date_start_end
    expected_output = list_top_transactions
    result = get_top_transactions(sample_dataframe, date_start, date_end)
    assert result == expected_output


def test_get_top_transactions_empty_dataframe(date_start_end, sample_empty_dataframe):
    """Тест возврата пустого списка при передаче пустого датафрейма"""
    date_start, date_end = date_start_end
    result = get_top_transactions(sample_empty_dataframe, date_start, date_end)
    assert result == []


@patch("requests.get")
def test_current_exchange_rate_success(mock_get, mock_json_file):
    """Тестирование запроса курса валют от API, с положительным статусом"""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"Valute": {"USD": {"Value": 75.00}, "EUR": {"Value": 90.00}}}

    expected_output = [{"currency": "USD", "rate": 75.00}, {"currency": "EUR", "rate": 90.00}]

    result = current_exchange_rate(mock_json_file)
    assert result == expected_output


@patch("requests.get")
def test_current_exchange_rate_api_error(mock_get, mock_json_file):
    """Тестирование, в случае ошибки при запросе от API"""
    mock_get.return_value.status_code = 500  # Ошибка сервера
    with pytest.raises(ValueError) as e:
        current_exchange_rate(mock_json_file)
    assert "Ошибка 500 при получении текущего курса валют!" in str(e.value)


@patch("requests.get")
def test_current_exchange_rate_currency_not_found(mock_get, mock_json_file):
    """Тестирование функции, в случае отсутствия заданной валюты в ответе от API"""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"Valute": {"USD": {"Value": 75.00}}}

    with pytest.raises(ValueError) as e:
        current_exchange_rate(mock_json_file)

    assert "Не найдены данные для валюты: EUR!" in str(e.value)


@patch("requests.get")
def test_current_values_stocks(mock_requests_get, mock_json_file):
    """Тестирование функции получения стоимости акций"""
    mock_requests_get.return_value.status_code = 200
    mock_requests_get.return_value.json.return_value = [{"price": 150.00}]

    result = current_values_stocks(mock_json_file)
    expected_result = [{"stock": "AAPL", "price": 150.00}]

    assert result == expected_result
    assert mock_requests_get.call_count == 1
