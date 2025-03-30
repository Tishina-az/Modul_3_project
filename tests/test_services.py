import json

import pytest

from src.services import analysis_cashback


@pytest.mark.parametrize("year, month, expected_output", [
    (2023, 10, {"Еда": 2, "Транспорт": 5, "Развлечения": 1}),
    (2022, 1, {})
])
def test_analysis_cashback(sample_dataframe, year, month, expected_output):
    """ """
    result = analysis_cashback(sample_dataframe, year, month)
    assert json.loads(result) == expected_output
