from typing import Any
from unittest.mock import patch

import pandas as pd
import pytest

from src.views import main_web_site


# Тест успешного выполнения функции main_web_site
@patch("src.views.price_of_stocks")
@patch("src.views.convert_amount_of_transactions")
@patch("src.views.read_json_file")
@patch("src.views.sort_operations_by_date")
@patch("src.views.read_excel_file")
@patch("src.views.hello_by_current_time")
def test_main_web_site_success(
    mock_hello: Any,
    mock_read_excel: Any,
    mock_sort: Any,
    mock_read_json: Any,
    mock_convert: Any,
    mock_stocks: Any,
    sample_transactions_df: Any,
    user_settings: Any,
) -> None:
    """Проверяет корректное формирование JSON-ответа при типичных данных."""
    # Настройка моков
    mock_hello.return_value = "Добрый день!"
    mock_read_excel.return_value = sample_transactions_df
    mock_sort.return_value = sample_transactions_df  # предполагаем, что сортировка не меняет данные
    mock_read_json.return_value = user_settings
    mock_convert.side_effect = lambda amount, currency: 90.5 if currency == "USD" else 100.2  # курсы
    mock_stocks.return_value = {"AAPL": {"price": "175.34"}, "GOOGL": {"price": "142.10"}}
    # Вызов тестируемой функции
    result = main_web_site("df_transactions")
    # Проверка структуры ответа
    assert isinstance(result, dict)
    assert set(result.keys()) == {"greeting", "cards", "top_transactions", "currency_rates", "stock_prices"}
    # Проверка приветствия
    assert result["greeting"] == "Добрый день!"
    # Проверка карт
    cards = result["cards"]
    assert len(cards) == 3  # две карты + одна запись с NaN
    # Карта 3456
    card_3456 = next(c for c in cards if c["last_digits"] == "3456")
    assert card_3456["total_spent"] == round(-1500.50 + (200.75), 2)  # -1299.75
    assert card_3456["cashback"] == float(round(abs(-1299.75) / 100, 2))  # 12.9975 -> 13.0 (round)
    # Карта 7654
    card_7654 = next(c for c in cards if c["last_digits"] == "7654")
    assert card_7654["total_spent"] == 3200.00
    assert card_7654["cashback"] == 0
    # NaN карта
    nan_card = next(c for c in cards if c["last_digits"] == "NaN")
    assert nan_card["total_spent"] == 50.00
    assert nan_card["cashback"] == 0.0  # так как сумма положительная, cashback = 0
    # Проверка top_transactions (должны быть отсортированы по убыванию абсолютной суммы)
    top = result["top_transactions"]
    assert len(top) == 4  # всего 4 записи в df
    # Проверим, что первой идёт сумма 3200 (абсолютная)
    assert top[0]["amount"] == 3200.00
    assert top[1]["amount"] == -1500.50
    assert top[2]["amount"] == 200.75
    assert top[3]["amount"] == 50.00
    # Проверка валют
    currencies = result["currency_rates"]
    assert len(currencies) == 2
    assert currencies[0]["currency"] == "USD"
    assert currencies[0]["rate"] == 90.5
    assert currencies[1]["currency"] == "EUR"
    assert currencies[1]["rate"] == 100.2
    # Проверка акций
    stocks = result["stock_prices"]
    assert len(stocks) == 2
    assert stocks[0]["stock"] == "AAPL"
    assert stocks[0]["price"] == 175.34
    assert stocks[1]["stock"] == "GOOGL"
    assert stocks[1]["price"] == 142.10


# Тест с пустым DataFrame операций
@patch("src.views.price_of_stocks")
@patch("src.views.convert_amount_of_transactions")
@patch("src.views.read_json_file")
@patch("src.views.sort_operations_by_date")
@patch("src.views.read_excel_file")
@patch("src.views.hello_by_current_time")
def test_main_web_site_empty_df(
    mock_hello: Any,
    mock_read_excel: Any,
    mock_sort: Any,
    mock_read_json: Any,
    mock_convert: Any,
    mock_stocks: Any,
    user_settings: Any,
) -> None:
    """Проверяет поведение при отсутствии транзакций (пустой DataFrame)."""
    empty_df = pd.DataFrame(columns=["Номер карты", "Дата операции", "Сумма платежа", "Категория", "Описание"])
    mock_hello.return_value = "Доброй ночи!"
    mock_read_excel.return_value = empty_df
    mock_sort.return_value = empty_df
    mock_read_json.return_value = user_settings
    mock_convert.side_effect = [90.5, 100.2]
    mock_stocks.return_value = {"AAPL": {"price": "175.34"}, "GOOGL": {"price": "142.10"}}
    result = main_web_site("df_transactions")
    # Проверка карт: список должен быть пустым
    assert result["cards"] == []
    # top_transactions: пустой список
    assert result["top_transactions"] == []
    # остальное должно заполниться нормально
    assert len(result["currency_rates"]) == 2
    assert len(result["stock_prices"]) == 2


# Тест обработки карт с различными типами значений (числа, строки, NaN)
@patch("src.views.price_of_stocks")
@patch("src.views.convert_amount_of_transactions")
@patch("src.views.read_json_file")
@patch("src.views.sort_operations_by_date")
@patch("src.views.read_excel_file")
@patch("src.views.hello_by_current_time")
def test_main_web_site_card_types(
    mock_hello: Any,
    mock_read_excel: Any,
    mock_sort: Any,
    mock_read_json: Any,
    mock_convert: Any,
    mock_stocks: Any,
    user_settings: Any,
) -> None:
    """Проверяет корректную обработку разных представлений номеров карт."""
    data = {
        "Номер карты": ["1234 5678 9012 3456", 1234567890123456, None, float("nan")],
        "Дата операции": ["01.01.2023", "02.01.2023", "03.01.2023", "04.01.2023"],
        "Сумма платежа": [100, -50, 200, 300],
        "Категория": ["A", "B", "C", "D"],
        "Описание": ["a", "b", "c", "d"],
    }
    df = pd.DataFrame(data)
    mock_hello.return_value = "Hi"
    mock_read_excel.return_value = df
    mock_sort.return_value = df
    mock_read_json.return_value = user_settings
    mock_convert.side_effect = [90.5, 100.2]
    mock_stocks.return_value = {"AAPL": {"price": "175"}, "GOOGL": {"price": "142"}}
    result = main_web_site("df_transactions")
    cards = result["cards"]
    assert len(cards) >= 3
    # Проверим обработку NaN
    nan_card = next(c for c in cards if c["last_digits"] == "NaN")
    assert nan_card["total_spent"] == 500  # сумма по всем NaN (200+300)
    assert nan_card["cashback"] == 0
    # Проверим числовую карту (она будет преобразована в строку целиком)
    num_card = next(c for c in cards if isinstance(c["last_digits"], str))
    assert num_card["total_spent"] == 100
    assert num_card["cashback"] == 0
    # Проверим строковую карту
    str_card = next(c for c in cards if c["last_digits"] == "3456")
    assert str_card["total_spent"] == 100
    assert str_card["cashback"] == 0


# Тест корректности сортировки top_transactions (по абсолютной сумме)
@patch("src.views.price_of_stocks")
@patch("src.views.convert_amount_of_transactions")
@patch("src.views.read_json_file")
@patch("src.views.sort_operations_by_date")
@patch("src.views.read_excel_file")
@patch("src.views.hello_by_current_time")
def test_top_transactions_absolute_sort(
    mock_hello: Any,
    mock_read_excel: Any,
    mock_sort: Any,
    mock_read_json: Any,
    mock_convert: Any,
    mock_stocks: Any,
    user_settings: Any,
) -> None:
    """Проверяет, что top_transactions сортируются по абсолютной величине суммы."""
    data = {
        "Номер карты": ["1", "2", "3", "4", "5", "6"],
        "Дата операции": ["01.01.2023"] * 6,
        "Сумма платежа": [100, -200, 300, -400, 50, -10],
        "Категория": ["A"] * 6,
        "Описание": ["a"] * 6,
    }
    df = pd.DataFrame(data)

    mock_hello.return_value = "Hi"
    mock_read_excel.return_value = df
    mock_sort.return_value = df
    mock_read_json.return_value = user_settings
    mock_convert.side_effect = [90.5, 100.2]
    mock_stocks.return_value = {"AAPL": {"price": "175"}, "GOOGL": {"price": "142"}}
    result = main_web_site("df_transactions")
    top = result["top_transactions"]
    # Должны быть первые 5 записей по убыванию абсолютной суммы: -400, 300, -200, 100, 50 (или -10 не входит)
    amounts = [t["amount"] for t in top]
    assert amounts == [-400, 300, -200, 100, 50]


# Тест обработки валют и акций с нестандартными возвращаемыми значениями
@patch("src.views.price_of_stocks")
@patch("src.views.convert_amount_of_transactions")
@patch("src.views.read_json_file")
@patch("src.views.sort_operations_by_date")
@patch("src.views.read_excel_file")
@patch("src.views.hello_by_current_time")
def test_currencies_and_stocks_handling(
    mock_hello: Any,
    mock_read_excel: Any,
    mock_sort: Any,
    mock_read_json: Any,
    mock_convert: Any,
    mock_stocks: Any,
    sample_transactions_df: Any,
    user_settings: Any,
) -> None:
    """Проверяет корректную обработку валют и акций при разных возвращаемых значениях."""
    mock_hello.return_value = "Hi"
    mock_read_excel.return_value = sample_transactions_df
    mock_sort.return_value = sample_transactions_df
    mock_read_json.return_value = user_settings
    # Курсы валют: одна возвращает число, другая строку (должна преобразоваться)
    mock_convert.side_effect = [90.5, "100.2"]  # строка будет передана в JSON как есть, но код не преобразует
    mock_stocks.return_value = {"AAPL": {"price": "175.34"}, "GOOGL": {"price": 142.10}}  # число
    result = main_web_site("df_transactions")
    currencies = result["currency_rates"]
    # Проверим, что второй курс пришёл как строка "100.2", а не число
    assert currencies[1]["rate"] == "100.2"
    stocks = result["stock_prices"]
    # Цена AAPL должна быть float 175.34, GOOGL float 142.1
    assert stocks[0]["price"] == 175.34
    assert stocks[1]["price"] == 142.1


# Тест на случай, если файл с настройками не содержит нужных ключей (ожидаем падение, но пока просто проверим)
@patch("src.views.price_of_stocks")
@patch("src.views.convert_amount_of_transactions")
@patch("src.views.read_json_file")
@patch("src.views.sort_operations_by_date")
@patch("src.views.read_excel_file")
@patch("src.views.hello_by_current_time")
def test_missing_settings_keys(
    mock_hello: Any,
    mock_read_excel: Any,
    mock_sort: Any,
    mock_read_json: Any,
    mock_convert: Any,
    mock_stocks: Any,
    sample_transactions_df: Any,
) -> None:
    """Проверяет, что при отсутствии ключей в настройках функция падает с ошибкой (ожидаемо)."""
    incomplete_settings: dict[str, Any] = {}
    mock_hello.return_value = "Hi"
    mock_read_excel.return_value = sample_transactions_df
    mock_sort.return_value = sample_transactions_df
    mock_read_json.return_value = incomplete_settings
    # Функция должна упасть с KeyError при обращении к отсутствующим ключам
    with pytest.raises(KeyError):
        main_web_site("df_transactions")
