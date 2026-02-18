import json
from datetime import datetime
from unittest.mock import patch, MagicMock, mock_open

import pandas as pd
import pytest
import requests
from requests import RequestException

from src.utils import read_excel_file, hello_by_current_time, sort_operations_by_date, convert_amount_of_transactions, \
    price_of_stocks, read_json_file


# Тесты для read_excel_file
def test_read_excel_file_success(sample_excel_file):
    """Проверяет успешное чтение Excel-файла и возврат DataFrame."""
    result = read_excel_file(sample_excel_file)
    assert isinstance(result, pd.DataFrame)
    assert not result.empty
    assert list(result.columns) == ['Дата операции', 'Категория', 'Сумма']
    assert len(result) == 2


def test_read_excel_file_invalid_path_type():
    """Проверяет, что передача не строки возвращает пустой список."""
    result = read_excel_file(123)  # передаём число вместо строки
    assert result == []


def test_read_excel_file_file_not_found():
    """Проверяет, что для несуществующего файла возвращается пустой список."""
    result = read_excel_file("non_existent_file.xlsx")
    assert result == []


@patch('pandas.read_excel')
def test_read_excel_file_exception_handling(mock_read_excel):
    """Проверяет обработку исключений при чтении файла."""
    # Настраиваем mock, чтобы он выбрасывал исключение
    mock_read_excel.side_effect = PermissionError("Доступ запрещён")
    result = read_excel_file("some_file.xlsx")
    assert result == []


# Тесты для hello_by_current_time
def test_hello_by_current_time_morning():
    """Проверяет приветствие для утреннего времени (6-11 часов)."""
    test_hour = 8
    with patch('src.utils.datetime') as mock_datetime:
        mock_datetime.now.return_value.hour = test_hour
        assert hello_by_current_time() == "Доброе утро!"


def test_hello_by_current_time_day():
    """Проверяет приветствие для дневного времени (12-17 часов)."""
    test_hour = 15
    with patch('src.utils.datetime') as mock_datetime:
        mock_datetime.now.return_value.hour = test_hour
        assert hello_by_current_time() == "Добрый день!"


def test_hello_by_current_time_evening():
    """Проверяет приветствие для вечернего времени (18-23 часов)."""
    test_hour = 20
    with patch('src.utils.datetime') as mock_datetime:
        mock_datetime.now.return_value.hour = test_hour
        assert hello_by_current_time() == "Добрый вечер!"


def test_hello_by_current_time_night():
    """Проверяет приветствие для ночного времени (0-5 часов)."""
    test_hour = 3
    with patch('src.utils.datetime') as mock_datetime:
        mock_datetime.now.return_value.hour = test_hour
        assert hello_by_current_time() == "Доброй ночи!"


def test_hello_by_current_time_edge_cases():
    """Проверяет граничные значения часов."""
    # 6 часов — утро
    with patch('src.utils.datetime') as mock_datetime:
        mock_datetime.now.return_value.hour = 6
        assert hello_by_current_time() == "Доброе утро!"
    # 11 часов — утро
    with patch('src.utils.datetime') as mock_datetime:
        mock_datetime.now.return_value.hour = 11
        assert hello_by_current_time() == "Доброе утро!"
    # 12 часов — день
    with patch('src.utils.datetime') as mock_datetime:
        mock_datetime.now.return_value.hour = 12
        assert hello_by_current_time() == "Добрый день!"
    # 17 часов — день
    with patch('src.utils.datetime') as mock_datetime:
        mock_datetime.now.return_value.hour = 17
        assert hello_by_current_time() == "Добрый день!"
    # 18 часов — вечер
    with patch('src.utils.datetime') as mock_datetime:
        mock_datetime.now.return_value.hour = 18
        assert hello_by_current_time() == "Добрый вечер!"
    # 23 часа — вечер
    with patch('src.utils.datetime') as mock_datetime:
        mock_datetime.now.return_value.hour = 23
        assert hello_by_current_time() == "Добрый вечер!"
    # 0 часов — ночь
    with patch('src.utils.datetime') as mock_datetime:
        mock_datetime.now.return_value.hour = 0
        assert hello_by_current_time() == "Доброй ночи!"
    # 5 часов — ночь
    with patch('src.utils.datetime') as mock_datetime:
        mock_datetime.now.return_value.hour = 5
        assert hello_by_current_time() == "Доброй ночи!"


# Тесты для sort_operations_by_date
def test_sort_operations_by_date_valid():
    """Проверка корректной фильтрации по дню, месяцу и случайному году."""
    data = {
        "Дата операции": [
            "15.01.2023 12:30:00",
            "20.01.2023 14:20:00",
            "05.02.2023 10:00:00",
            "25.01.2024 09:15:00",
            "10.01.2022 18:45:00"
        ]
    }
    df = pd.DataFrame(data)

    with patch('src.utils.datetime') as mock_datetime:
        # Задаём текущую дату: 20 января 2023 года
        mock_datetime.now.return_value = datetime(2023, 1, 20, 15, 0, 0)
        with patch('random.randint', return_value=2023):
            result = sort_operations_by_date(df)

    # Ожидаем только строки с месяцем январь, днём <=20 и годом 2023
    assert len(result) == 2
    assert all(result["Дата операции"].dt.year == 2023)
    assert all(result["Дата операции"].dt.month == 1)
    assert all(result["Дата операции"].dt.day <= 20)


def test_sort_operations_by_date_empty_df():
    """Проверка на пустом DataFrame."""
    df = pd.DataFrame(columns=["Дата операции"])
    with patch('src.utils.datetime') as mock_datetime:
        mock_datetime.now.return_value = datetime(2023, 1, 20, 15, 0, 0)
        with patch('random.randint', return_value=2023):
            result = sort_operations_by_date(df)
    assert result.empty


def test_sort_operations_by_date_invalid_date_format():
    """Проверка, что неверный формат даты приводит к исключению строк."""
    data = {
        "Дата операции": [
            "invalid_date",
            "15.01.2021 12:30:00"
        ]
    }
    df = pd.DataFrame(data)
    with patch('src.utils.datetime') as mock_datetime:
        mock_datetime.now.return_value = datetime(2023, 1, 20, 15, 0, 0)
        with patch('random.randint', return_value=2021):
            result = sort_operations_by_date(df)
    # Должна остаться только одна валидная запись
    assert len(result) == 1
    assert result.iloc[0]["Дата операции"] == pd.Timestamp("2021-01-15 12:30:00")


# Тесты для convert_amount_of_transactions
@patch('src.utils.os.getenv')
@patch('src.utils.requests.request')
def test_convert_amount_of_transactions_success(mock_request, mock_getenv):
    """Успешная конвертация валюты."""
    mock_getenv.return_value = "valid_api_key_123"
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = json.dumps({"result": 7500.50})
    mock_request.return_value = mock_response

    result = convert_amount_of_transactions(100, "USD")

    assert result == 7500.5
    mock_request.assert_called_once_with(
        "GET",
        "https://api.apilayer.com/currency_data/convert",
        headers={"apikey": "valid_api_key_123"},
        params={"to": "RUB", "from": "USD", "amount": 100},
        timeout=10
    )


@patch('src.utils.os.getenv')
@patch('src.utils.requests.request')
def test_convert_amount_of_transactions_euro_success(mock_request, mock_getenv):
    """Успешная конвертация евро."""
    mock_getenv.return_value = "valid_api_key_123"
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = json.dumps({"result": 90.25})
    mock_request.return_value = mock_response

    result = convert_amount_of_transactions(1, "EUR")

    assert result == 90.25


def test_convert_amount_of_transactions_invalid_currency():
    """Неверный код валюты."""
    result = convert_amount_of_transactions(100, "GBP")
    assert result == "Недопустимый код валюты для конвертации"


def test_convert_amount_of_transactions_non_positive_amount():
    """Сумма <= 0."""
    result = convert_amount_of_transactions(-10, "USD")
    assert result == "Сумма должна быть положительной"
    result = convert_amount_of_transactions(0, "EUR")
    assert result == "Сумма должна быть положительной"


@patch('src.utils.os.getenv')
def test_convert_amount_of_transactions_missing_api_key(mock_getenv):
    """API ключ отсутствует."""
    mock_getenv.return_value = None
    result = convert_amount_of_transactions(100, "USD")
    assert result == "API ключ не найден"


@patch('src.utils.os.getenv')
@patch('src.utils.requests.request')
def test_convert_amount_of_transactions_request_exception(mock_request, mock_getenv):
    """Ошибка запроса (сетевая)."""
    mock_getenv.return_value = "valid_api_key_123"
    mock_request.side_effect = RequestException("Connection error")
    result = convert_amount_of_transactions(100, "USD")
    assert result == "Ошибка запроса: Connection error"


@patch('src.utils.os.getenv')
@patch('src.utils.requests.request')
def test_convert_amount_of_transactions_http_error(mock_request, mock_getenv):
    """HTTP ошибка (например, 404)."""
    mock_getenv.return_value = "valid_api_key_123"
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Client Error")
    mock_request.return_value = mock_response
    # raise_for_status() будет вызван и выбросит исключение
    with patch('requests.Response.raise_for_status', side_effect=requests.exceptions.HTTPError("404")):
        result = convert_amount_of_transactions(100, "USD")
    # Проверяем, что функция возвращает сообщение об ошибке
    assert result.startswith("Ошибка запроса:")


@patch('src.utils.os.getenv')
@patch('src.utils.requests.request')
def test_convert_amount_of_transactions_invalid_json(mock_request, mock_getenv):
    """Неверный формат JSON в ответе."""
    mock_getenv.return_value = "valid_api_key_123"
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "not a json"
    mock_request.return_value = mock_response

    result = convert_amount_of_transactions(100, "USD")
    assert result.startswith("Ошибка обработки данных:")


@patch('src.utils.os.getenv')
@patch('src.utils.requests.request')
def test_convert_amount_of_transactions_missing_result_field(mock_request, mock_getenv):
    """В ответе отсутствует поле 'result'."""
    mock_getenv.return_value = "valid_api_key_123"
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = json.dumps({"error": "something"})
    mock_request.return_value = mock_response

    result = convert_amount_of_transactions(100, "USD")
    assert result == "Неверный формат ответа от API"


@patch('src.utils.os.getenv')
@patch('src.utils.requests.request')
def test_convert_amount_of_transactions_result_not_number(mock_request, mock_getenv):
    """Поле 'result' не является числом."""
    mock_getenv.return_value = "valid_api_key_123"
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = json.dumps({"result": "not a number"})
    mock_request.return_value = mock_response

    result = convert_amount_of_transactions(100, "USD")
    assert result == "Неверный формат ответа от API"


@patch('src.utils.os.getenv')
@patch('src.utils.requests.request')
def test_convert_amount_of_transactions_timeout(mock_request, mock_getenv):
    """Таймаут запроса."""
    mock_getenv.return_value = "valid_api_key_123"
    mock_request.side_effect = requests.exceptions.Timeout("Request timed out")
    result = convert_amount_of_transactions(100, "USD")
    assert result == "Ошибка запроса: Request timed out"


# Тесты для price_of_stocks
@patch('src.utils.TDClient')
@patch('src.utils.os.getenv')
@patch('src.utils.load_dotenv')
def test_price_of_stocks_success(mock_load_dotenv, mock_getenv, mock_tdclient):
    """Успешное получение цены акций с корректным API ключом."""
    # Настройка моков
    mock_getenv.return_value = "valid_api_key_123"
    mock_instance = MagicMock()
    mock_tdclient.return_value = mock_instance
    # Настраиваем цепочку вызовов: price(...).as_json() возвращает тестовые данные
    mock_price = MagicMock()
    mock_instance.price.return_value = mock_price
    mock_price.as_json.return_value = {"AAPL": {"price": 150.25}}

    # Вызов функции
    stocks = ["AAPL"]
    result = price_of_stocks(stocks)

    # Проверки
    assert result == {"AAPL": {"price": 150.25}}
    mock_load_dotenv.assert_called_once()
    mock_getenv.assert_called_once_with("API_KEY_STOCKS")
    mock_tdclient.assert_called_once_with(apikey="valid_api_key_123")
    mock_instance.price.assert_called_once_with(symbol=stocks)
    mock_price.as_json.assert_called_once()


@patch('src.utils.TDClient')
@patch('src.utils.os.getenv')
@patch('src.utils.load_dotenv')
def test_price_of_stocks_with_string_symbol(mock_load_dotenv, mock_getenv, mock_tdclient):
    """Проверка, что символ передаётся правильно, если stocks — строка."""
    mock_getenv.return_value = "valid_api_key_123"
    mock_instance = MagicMock()
    mock_tdclient.return_value = mock_instance
    mock_price = MagicMock()
    mock_instance.price.return_value = mock_price
    mock_price.as_json.return_value = {"AAPL": {"price": 150.25}}

    stocks = "AAPL"
    result = price_of_stocks(stocks)

    assert result == {"AAPL": {"price": 150.25}}
    mock_instance.price.assert_called_once_with(symbol="AAPL")


@patch('src.utils.TDClient')
@patch('src.utils.os.getenv')
@patch('src.utils.load_dotenv')
def test_price_of_stocks_missing_api_key(mock_load_dotenv, mock_getenv, mock_tdclient):
    """Отсутствие API ключа должно приводить к исключению (или ошибке)."""
    mock_getenv.return_value = None  # ключ не найден
    # Имитируем, что TDClient выбрасывает исключение при создании с None
    mock_tdclient.side_effect = Exception("API key is required")

    with pytest.raises(Exception, match="API key is required"):
        price_of_stocks(["AAPL"])

    mock_load_dotenv.assert_called_once()
    mock_getenv.assert_called_once_with("API_KEY_STOCKS")
    mock_tdclient.assert_called_once_with(apikey=None)


@patch('src.utils.TDClient')
@patch('src.utils.os.getenv')
@patch('src.utils.load_dotenv')
def test_price_of_stocks_empty_api_key(mock_load_dotenv, mock_getenv, mock_tdclient):
    """Пустой API ключ (строка) также может вызывать ошибку."""
    mock_getenv.return_value = ""  # пустая строка
    mock_tdclient.side_effect = Exception("Invalid API key")

    with pytest.raises(Exception, match="Invalid API key"):
        price_of_stocks(["AAPL"])

    mock_tdclient.assert_called_once_with(apikey="")


@patch('src.utils.TDClient')
@patch('src.utils.os.getenv')
@patch('src.utils.load_dotenv')
def test_price_of_stocks_api_returns_error(mock_load_dotenv, mock_getenv, mock_tdclient):
    """Проверка обработки случая, когда метод price возвращает структуру с ошибкой."""
    mock_getenv.return_value = "valid_key"
    mock_instance = MagicMock()
    mock_tdclient.return_value = mock_instance
    mock_price = MagicMock()
    mock_instance.price.return_value = mock_price
    # Имитируем ответ с ошибкой
    mock_price.as_json.return_value = {"error": "Symbol not found"}

    result = price_of_stocks(["UNKNOWN"])

    assert result == {"error": "Symbol not found"}
    mock_instance.price.assert_called_once_with(symbol=["UNKNOWN"])


# Тесты для read_json_file
@patch("builtins.open", new_callable=mock_open, read_data='[{"key": "value"}, {"key2": "value2"}]')
def test_read_json_file_success(mock_file):
    """Корректный JSON-файл со списком возвращает этот список."""
    result = read_json_file("dummy_path.json")
    assert result == [{"key": "value"}, {"key2": "value2"}]
    mock_file.assert_called_once_with("dummy_path.json", "r", encoding="utf-8")


@patch("builtins.open", new_callable=mock_open, read_data='{"key": "value"}')
def test_read_json_file_not_list(mock_file):
    """Если JSON не список, возвращается пустой список."""
    result = read_json_file("dummy_path.json")
    assert result == []
    mock_file.assert_called_once()


@patch("builtins.open", new_callable=mock_open, read_data='{"key": "value"')  # невалидный JSON
def test_read_json_file_invalid_json(mock_file):
    """При ошибке JSONDecodeError возвращается пустой список."""
    result = read_json_file("dummy_path.json")
    assert result == []
    mock_file.assert_called_once()


@patch("builtins.open", side_effect=FileNotFoundError)
def test_read_json_file_not_found(mock_file):
    """Если файл не найден, возвращается пустой список."""
    result = read_json_file("nonexistent.json")
    assert result == []
    mock_file.assert_called_once_with("nonexistent.json", "r", encoding="utf-8")


@patch("builtins.open", side_effect=PermissionError)
def test_read_json_file_permission_error(mock_file):
    """При ошибке доступа возвращается пустой список."""
    result = read_json_file("protected.json")
    assert result == []
    mock_file.assert_called_once()


@patch("builtins.open", side_effect=OSError)
def test_read_json_file_os_error(mock_file):
    """При OSError возвращается пустой список."""
    result = read_json_file("some_file.json")
    assert result == []
    mock_file.assert_called_once()


def test_read_json_file_non_string_path():
    """Если аргумент path не строка, возвращается пустой список (без попытки открыть файл)."""
    result = read_json_file(123)
    assert result == []


@patch("builtins.open", side_effect=FileNotFoundError)
def test_read_json_file_empty_path(mock_file):
    """Пустая строка пути приводит к FileNotFoundError и возврату []."""
    result = read_json_file("")
    assert result == []
    mock_file.assert_called_once_with("", "r", encoding="utf-8")


@pytest.mark.parametrize("exception", [FileNotFoundError, PermissionError, OSError])
@patch("builtins.open")
def test_read_json_file_multiple_exceptions(mock_open, exception):
    """Параметризованная проверка разных исключений."""
    mock_open.side_effect = exception
    result = read_json_file("some_path.json")
    assert result == []
    mock_open.assert_called_once()
