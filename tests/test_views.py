import math
from typing import Any, Dict
from unittest.mock import MagicMock

import pandas as pd
from pandas import DataFrame

from src.views import main_web_site


def test_main_web_site_returns_correct_structure(
    mock_dependencies: Dict[str, MagicMock], sample_df: DataFrame
) -> None:
    """Проверяет, что функция возвращает словарь с ожидаемыми ключами."""
    result = main_web_site(sample_df)
    assert isinstance(result, dict)
    expected_keys = {"greeting", "cards", "top_transactions", "currency_rates", "stock_prices"}
    assert set(result.keys()) == expected_keys
    # Проверяем, что значения соответствуют мокам
    assert result["greeting"] == "Добрый день"
    assert result["cards"] == [{"last_digits": "1234", "total_spent": -150, "cashback": 1.5}]
    assert result["top_transactions"] == [{"date": "01.01.2021", "amount": 200, "category": "Перевод"}]
    assert result["currency_rates"] == [{"currency": "USD", "rate": 75.5}]
    assert result["stock_prices"] == [{"stock": "AAPL", "price": 150.0}]


def test_main_web_site_calls_dependencies_correctly(
    mock_dependencies: Dict[str, MagicMock], sample_df: DataFrame
) -> Any:
    """Проверяет, что каждая зависимость вызывается с правильными аргументами."""
    result = main_web_site(sample_df)
    # 1. hello_by_current_time вызывается без аргументов
    mock_dependencies["hello"].assert_called_once_with()
    # 2. sort_operations_by_date вызывается с исходным df
    mock_dependencies["sort"].assert_called_once_with(sample_df)
    # Получаем отсортированный DataFrame из мока
    sorted_df = mock_dependencies["sort"].return_value
    # 3. create_json_info_cards вызывается с отсортированным df и списком карт
    # Список карт должен быть уникальными значениями из колонки "Номер карты"
    expected_cards_list = sorted_df["Номер карты"].unique().tolist()
    mock_dependencies["cards"].assert_called_once_with(sorted_df, expected_cards_list)
    # 4. create_json_info_top вызывается с отсортированным df
    mock_dependencies["top"].assert_called_once_with(sorted_df)
    # 5. read_json_file вызывается с именем файла
    mock_dependencies["read"].assert_called_once_with("user_settings.json")
    # 6. create_info_user_currency и create_info_stocks вызываются с результатом read_json_file
    settings = mock_dependencies["read"].return_value
    mock_dependencies["currency"].assert_called_once_with(settings)
    mock_dependencies["stocks"].assert_called_once_with(settings)
    assert len(result) == 5


def test_main_web_site_logging(mock_dependencies: Dict[str, MagicMock], sample_df: DataFrame) -> None:
    """Проверяет, что логгер вызывается нужное количество раз."""
    main_web_site(sample_df)
    # Должно быть 7 вызовов logger.info (по одному после каждого этапа + итоговый)
    assert mock_dependencies["logger"].info.call_count == 7


def test_main_web_site_empty_dataframe(mock_dependencies: Dict[str, MagicMock]) -> None:
    """Проверяет функцию формирования ответа для страницы 'Главная' при пусой базе данных"""
    empty_df = pd.DataFrame(columns=["Номер карты", "Сумма платежа"])  # добавляем нужные колонки
    mock_dependencies["sort"].return_value = empty_df
    result = main_web_site(pd.DataFrame())  # можно передать любой DataFrame
    # Проверяем, что create_json_info_cards получил пустой список карт
    mock_dependencies["cards"].assert_called_once_with(empty_df, [])
    mock_dependencies["top"].assert_called_once_with(empty_df)
    # Остальное должно отработать
    assert result["greeting"] == mock_dependencies["hello"].return_value


def test_main_web_site_with_none_in_card_column(mock_dependencies: Dict[str, MagicMock]) -> None:
    """Проверяет функцию формирования ответа для страницы 'Главная' в части cards"""
    df_with_nan = pd.DataFrame({"Номер карты": ["1234", None, "5678", None], "Сумма платежа": [100, 200, 300, 400]})
    mock_dependencies["sort"].return_value = df_with_nan
    main_web_site(df_with_nan)
    # Проверяем аргументы вручную
    args, kwargs = mock_dependencies["cards"].call_args
    pd.testing.assert_frame_equal(args[0], df_with_nan)
    actual_list = args[1]
    expected_list = ["1234", None, "5678"]
    assert len(actual_list) == len(expected_list)
    for a, e in zip(actual_list, expected_list):
        if isinstance(a, float) and math.isnan(a) and e is None:
            continue
        assert a == e
