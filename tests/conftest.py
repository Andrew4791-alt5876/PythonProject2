from typing import Any, Generator
from unittest.mock import patch

import pandas as pd
import pytest
from pandas import DataFrame


@pytest.fixture
def sample_transactions_df() -> pd.DataFrame:
    """DataFrame с тестовыми транзакциями."""
    data = {
        "Дата операции": ["15.03.2021 12:30:00", "20.03.2021 15:45:00", "25.03.2021 09:10:00"],
        "Номер карты": ["1234567890123456", "9876543210987654", "1234567890123456"],
        "Сумма платежа": [-1500.50, 2000.00, -300.25],
        "Категория": ["Супермаркеты", "Переводы", "Аптеки"],
        "Описание": ["Пятёрочка", "Перевод другу", "Аптека"],
    }
    return pd.DataFrame(data)


@pytest.fixture
def user_settings() -> list[dict]:
    """Пример содержимого user_settings.json."""
    return [{"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "TSLA"]}]


@pytest.fixture
def mock_logger() -> Generator:
    """Мок для глобального логгера, чтобы не портить реальные файлы."""
    with patch("src.utils.logger") as mock:
        yield mock


@pytest.fixture
def sample_df() -> DataFrame:
    """Тестовый DataFrame с необходимыми колонками."""
    data = {
        "Номер карты": ["1234", "5678", "1234"],
        "Сумма платежа": [-100, 200, -50],
        "Дата операции": ["01.01.2021 12:00", "02.01.2021 13:00", "03.01.2021 14:00"],
        "Категория": ["Еда", "Перевод", "Еда"],
        "Описание": ["A", "B", "C"],
    }
    return pd.DataFrame(data)


# Фикстура для мока внешней функции sort_operations_by_user_month_year
@pytest.fixture
def mock_sort_operations(mocker: Any) -> Any:
    # Мокаем функцию, чтобы она возвращала тот же DataFrame, который передали
    return mocker.patch("src.services.sort_operations_by_user_month_year", side_effect=lambda df: df)


@pytest.fixture
def mock_dependencies() -> Generator:
    """
    Фикстура, которая подменяет все внешние функции,
    используемые в main_web_site, на моки.
    Возвращает словарь с моками для проверок.
    """
    with patch("src.views.hello_by_current_time") as mock_hello, patch(
        "src.views.sort_operations_by_date"
    ) as mock_sort, patch("src.views.create_json_info_cards") as mock_cards, patch(
        "src.views.create_json_info_top"
    ) as mock_top, patch(
        "src.views.read_json_file"
    ) as mock_read, patch(
        "src.views.create_info_user_currency"
    ) as mock_currency, patch(
        "src.views.create_info_stocks"
    ) as mock_stocks, patch(
        "src.views.logger"
    ) as mock_logger:

        # Настраиваем возвращаемые значения
        mock_hello.return_value = "Добрый день"
        # Мок для sort_operations_by_date должен вернуть DataFrame
        # Мы вернём тот же sample_df, но можно и другой
        mock_sort.return_value = pd.DataFrame({"Номер карты": ["1234", "5678"], "Сумма платежа": [-150, 200]})
        mock_cards.return_value = [{"last_digits": "1234", "total_spent": -150, "cashback": 1.5}]
        mock_top.return_value = [{"date": "01.01.2021", "amount": 200, "category": "Перевод"}]
        mock_read.return_value = [{"user_currencies": ["USD"], "user_stocks": ["AAPL"]}]
        mock_currency.return_value = [{"currency": "USD", "rate": 75.5}]
        mock_stocks.return_value = [{"stock": "AAPL", "price": 150.0}]

        yield {
            "hello": mock_hello,
            "sort": mock_sort,
            "cards": mock_cards,
            "top": mock_top,
            "read": mock_read,
            "currency": mock_currency,
            "stocks": mock_stocks,
            "logger": mock_logger,
        }
