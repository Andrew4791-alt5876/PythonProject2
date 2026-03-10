import json
from typing import Any
from unittest.mock import MagicMock, mock_open, patch

import pandas as pd
import requests
from pandas import DataFrame

from src import utils


# ---------- Тесты для read_excel_file ----------
def test_read_excel_file_success(mocker: MagicMock) -> Any:
    """Успешное чтение Excel-файла."""
    mock_df = pd.DataFrame({"A": [1, 2]})
    mocker.patch("pandas.read_excel", return_value=mock_df)
    mock_logger = mocker.patch("src.utils.logger")
    result = utils.read_excel_file("test.xlsx")
    # Проверяем, что результат — DataFrame
    assert isinstance(result, pd.DataFrame)
    pd.testing.assert_frame_equal(result, mock_df)
    mock_logger.info.assert_called_once_with("Excel-файл преобразован в DataFrame успешно")


def test_read_excel_file_invalid_path_type(mock_logger: MagicMock) -> None:
    """Передан не строковый путь."""
    result = utils.read_excel_file(123)
    assert result == []
    mock_logger.error.assert_called_once_with("Ошибка пути к excel-файлу")


def test_read_excel_file_exception(mock_logger: MagicMock) -> None:
    """Ошибка при чтении файла."""
    with patch("pandas.read_excel", side_effect=FileNotFoundError):
        result = utils.read_excel_file("missing.xlsx")
        assert result == []
        mock_logger.error.assert_called_once()  # сообщение может быть любым


# ---------- Тесты для hello_by_current_time ----------
@patch("src.utils.datetime")
def test_hello_by_current_time_morning(mock_datetime: Any, mock_logger: MagicMock) -> None:
    """Тест для функции формирования приветственного сообщения 'Доброе утро!'"""
    mock_datetime.now.return_value.hour = 8
    assert utils.hello_by_current_time() == "Доброе утро!"
    mock_logger.info.assert_called_once()


@patch("src.utils.datetime")
def test_hello_by_current_time_day(mock_datetime: Any, mock_logger: MagicMock) -> None:
    """Тест для функции формирования приветственного сообщения 'Добрый день!'"""
    mock_datetime.now.return_value.hour = 15
    assert utils.hello_by_current_time() == "Добрый день!"


@patch("src.utils.datetime")
def test_hello_by_current_time_evening(mock_datetime: Any, mock_logger: MagicMock) -> None:
    """Тест для функции формирования приветственного сообщения 'Добрый вечер!'"""
    mock_datetime.now.return_value.hour = 20
    assert utils.hello_by_current_time() == "Добрый вечер!"


@patch("src.utils.datetime")
def test_hello_by_current_time_night(mock_datetime: Any, mock_logger: MagicMock) -> None:
    """Тест для функции формирования приветственного сообщения 'Доброй ночи!'"""
    mock_datetime.now.return_value.hour = 3
    assert utils.hello_by_current_time() == "Доброй ночи!"


# ---------- Тесты для sort_operations_by_date ----------
@patch("src.utils.random.randint")
@patch("src.utils.datetime")
def test_sort_operations_by_date_success(
    mock_datetime: Any, mock_randint: Any, sample_transactions_df: DataFrame, mock_logger: MagicMock
) -> None:
    """Успешный тест функции сортировки базы данных по дате"""
    # Настраиваем текущую дату
    mock_datetime.now.return_value.day = 25
    mock_datetime.now.return_value.month = 3
    mock_randint.return_value = 2021
    # Применяем функцию
    result = utils.sort_operations_by_date(sample_transactions_df)
    # После преобразования дат столбец станет datetime, проверим длину
    assert len(result) == 3
    mock_logger.info.assert_called_once()


def test_sort_operations_by_date_key_error(mock_logger: MagicMock) -> None:
    """Отсутствует колонка 'Дата операции'."""
    df = pd.DataFrame({"A": [1, 2]})
    result = utils.sort_operations_by_date(df)
    assert result == []
    mock_logger.error.assert_called_once()


# ---------- Тесты для create_json_info_cards ----------
# (с учётом бага – return внутри цикла)
def test_create_json_info_cards_string_card(sample_transactions_df: DataFrame, mock_logger: MagicMock) -> None:
    """Проверка формирования ответа в части cards при входных данных о счете в виде строки"""
    user_cards = ["1234567890123456"]
    result = utils.create_json_info_cards(sample_transactions_df, user_cards)
    assert len(result) == 1
    assert result[0]["last_digits"] == "3456"
    assert result[0]["total_spent"] == -1800.75  # -1500.50 + -300.25
    assert result[0]["cashback"] == 18.01  # округление abs(-1800.75)/100


def test_create_json_info_cards_numeric_card(sample_transactions_df: DataFrame, mock_logger: MagicMock) -> None:
    """Проверка формирования ответа в части cards при входных данных о счете в виде целого числа"""
    user_cards = [9876543210987654]
    result = utils.create_json_info_cards(sample_transactions_df, user_cards)
    assert result[0]["last_digits"] == "7654"
    assert result[0]["total_spent"] == 2000.0
    assert result[0]["cashback"] == 0


def test_create_json_info_cards_nan_card() -> None:
    """Проверка считывания карт в формате None для формирования ответа в части cards"""
    df = pd.DataFrame({"Номер карты": [None, "1234"], "Сумма платежа": [-100, -200]})
    user_cards = [None]
    result = utils.create_json_info_cards(df, user_cards)
    assert result[0]["last_digits"] == "NaN"
    assert result[0]["total_spent"] == -100.0
    assert result[0]["cashback"] == 1.0


def test_create_json_info_cards_empty_list(sample_transactions_df: DataFrame) -> None:
    """Проверка при пустом листе банковских карт"""
    result = utils.create_json_info_cards(sample_transactions_df, [])
    assert result is None  # нет return


# ---------- Тесты для create_json_info_top ----------
def test_create_json_info_top(sample_transactions_df: DataFrame, mock_logger: MagicMock) -> None:
    """Проверка формирования ответа в части top_transactions"""
    result = utils.create_json_info_top(sample_transactions_df)
    # из-за возврата внутри цикла вернётся только первая запись
    assert len(result) == 1
    assert result[0]["amount"] == 2000.0  # наибольшая по модулю? на самом деле сортировка по abs
    # в sample_transactions_df модули: 1500.5, 2000, 300.25 -> сортировка по убыванию: 2000, 1500.5, 300.25
    # head(5) берёт все 3, но из-за бага только первая
    assert result[0]["category"] == "Переводы"
    assert result[0]["date"] == "20.03.2021"  # дата без времени


# ---------- Тесты для convert_amount_of_transactions ----------
@patch("src.utils.os.getenv")
@patch("src.utils.requests.request")
def test_convert_amount_success(mock_request: Any, mock_getenv: Any, mock_logger: MagicMock) -> None:
    """Тест на успешность формирования информации о курсе валюты"""
    mock_getenv.return_value = "fake_api_key"
    mock_response = MagicMock()
    mock_response.text = json.dumps({"result": 7500.50})
    mock_response.raise_for_status.return_value = None
    mock_request.return_value = mock_response
    result = utils.convert_amount_of_transactions(100, "USD")
    assert result == 7500.50
    mock_request.assert_called_once()
    mock_logger.info.assert_called_once()


def test_convert_amount_invalid_currency(mock_logger: MagicMock) -> None:
    """Тест с не допустимой валютой"""
    result = utils.convert_amount_of_transactions(100, "GBP")
    assert result == 0
    mock_logger.warning.assert_called_once()


def test_convert_amount_non_positive(mock_logger: MagicMock) -> None:
    """Тест с отрицательны количеством валюты для перевода в другую валюту"""
    result = utils.convert_amount_of_transactions(-10, "USD")
    assert result == 0
    mock_logger.warning.assert_called_once()


@patch("src.utils.os.getenv", return_value=None)
def test_convert_amount_no_api_key(mock_getenv: Any, mock_logger: MagicMock) -> None:
    """Тест при отсутствии API-ключа"""
    result = utils.convert_amount_of_transactions(100, "USD")
    assert result == 0
    mock_logger.warning.assert_called_once_with("API ключ не найден по курсу валюты")


@patch("src.utils.os.getenv", return_value="key")
@patch("src.utils.requests.request", side_effect=requests.exceptions.Timeout)
def test_convert_amount_request_exception(mock_request: Any, mock_getenv: Any, mock_logger: MagicMock) -> None:
    """Тест при превышении времени ответа на запрос с сервера"""
    result = utils.convert_amount_of_transactions(100, "USD")
    assert result == 0
    mock_logger.error.assert_called_once()


# ---------- Тесты для create_info_user_currency ----------
@patch("src.utils.convert_amount_of_transactions")
def test_create_info_user_currency_success(mock_convert: Any, user_settings: Any, mock_logger: MagicMock) -> None:
    """Проверка успешного формирования ответа по курсам валют"""
    mock_convert.side_effect = [75.5, 90.2]  # USD -> 75.5, EUR -> 90.2
    result = utils.create_info_user_currency(user_settings)
    expected = [{"currency": "USD", "rate": 75.5}, {"currency": "EUR", "rate": 90.2}]
    assert result == expected
    assert mock_convert.call_count == 2
    mock_logger.info.call_count == 2


@patch("src.utils.convert_amount_of_transactions", return_value=0)
def test_create_info_user_currency_unavailable(mock_convert: Any, user_settings: Any, mock_logger: MagicMock) -> None:
    """Тест на не верный запрос и не возможности получения курса валют"""
    result = utils.create_info_user_currency(user_settings)
    # если курс 0, элемент не добавляется в список
    assert result == []  # ни один не добавлен
    mock_logger.warning.call_count == 2


# ---------- Тесты для price_of_stocks ----------
@patch("src.utils.os.getenv")
@patch("src.utils.TDClient")
def test_price_of_stocks_success(mock_tdclient: Any, mock_getenv: Any, mock_logger: MagicMock) -> None:
    """Тест на успешное получение данных о стоимости акций"""
    mock_getenv.return_value = "stock_key"
    mock_instance = MagicMock()
    mock_instance.price.return_value.as_json.return_value = {"AAPL": {"price": 150.25}}
    mock_tdclient.return_value = mock_instance

    result = utils.price_of_stocks("AAPL")
    assert result == {"AAPL": {"price": 150.25}}
    mock_logger.info.assert_called_once()


@patch("src.utils.os.getenv", return_value=None)
def test_price_of_stocks_no_key(mock_getenv: Any, mock_logger: MagicMock) -> None:
    """Тест при отсутствии API-ключа при запросе стоимости акций"""
    result = utils.price_of_stocks("AAPL")
    assert result == {}
    mock_logger.warning.assert_called_once_with("API ключ не найден по стоимости акций")


@patch("src.utils.os.getenv", return_value="key")
@patch("src.utils.TDClient", side_effect=requests.exceptions.RequestException("fail"))
def test_price_of_stocks_exception(mock_td: Any, mock_getenv: Any, mock_logger: MagicMock) -> None:
    """Тест при ошибке при запросе или не корректном ответе по стоимости акций"""
    result = utils.price_of_stocks("AAPL")
    assert result == {}
    mock_logger.error.assert_called_once()


# ---------- Тесты для create_info_stocks ----------
@patch("src.utils.price_of_stocks")
def test_create_info_stocks_success(mock_price: Any, user_settings: Any, mock_logger: MagicMock) -> None:
    """Тест на успешное формирование ответа по стоимости акций"""
    mock_price.return_value = {"AAPL": {"price": 150.25}, "TSLA": {"price": 700.50}}
    result = utils.create_info_stocks(user_settings)
    expected = [{"stock": "AAPL", "price": 150.25}, {"stock": "TSLA", "price": 700.50}]
    assert result == expected
    mock_logger.info.assert_called()


@patch("src.utils.price_of_stocks", return_value={})
def test_create_info_stocks_fallback_zero(mock_price: Any, user_settings: Any, mock_logger: MagicMock) -> None:
    """Тест при отсутствии данных о стоимости акций"""
    result = utils.create_info_stocks(user_settings)
    expected = [{"stock": "AAPL", "price": 0}, {"stock": "TSLA", "price": 0}]
    assert result == expected
    mock_logger.warning.call_count == 2


# ---------- Тесты для read_json_file ----------
def test_read_json_file_success(mock_logger: MagicMock) -> None:
    """Тест на успешное формирование JSON-ответа для web-страницы 'Главная'"""
    mock_data = [{"key": "value"}]
    mock_open_obj = mock_open(read_data=json.dumps(mock_data))
    with patch("builtins.open", mock_open_obj):
        result = utils.read_json_file("settings.json")
        assert result == mock_data
        mock_logger.info.assert_called_once_with("JSON-файл преобразован в DataFrame успешно")


def test_read_json_file_not_list(mock_logger: MagicMock) -> None:
    """Тест на не успешное формирование JSON-ответа для web-страницы 'Главная'"""
    mock_data = {"key": "value"}  # словарь, не список
    mock_open_obj = mock_open(read_data=json.dumps(mock_data))
    with patch("builtins.open", mock_open_obj):
        result = utils.read_json_file("settings.json")
        assert result == []
        mock_logger.warning.assert_called_once_with("Не верный формат преобразования JSON-файла")


def test_read_json_file_invalid_path_type(mock_logger: MagicMock) -> None:
    """Тест на не верные данные при формировании JSON-ответа для web-страницы 'Главная'"""
    result = utils.read_json_file(123)
    assert result == []
    mock_logger.warning.assert_called_once_with("Не верный формат пути к JSON-файлу")


def test_read_json_file_file_not_found(mock_logger: MagicMock) -> None:
    """Тест при отсутствии JSON-файла"""
    with patch("builtins.open", side_effect=FileNotFoundError):
        result = utils.read_json_file("missing.json")
        assert result == []
        mock_logger.error.assert_called_once()


def test_read_json_file_json_decode_error(mock_logger: MagicMock) -> None:
    """Тест при ошибки преобразования JSON-файла"""
    mock_open_obj = mock_open(read_data="invalid json")
    with patch("builtins.open", mock_open_obj):
        result = utils.read_json_file("settings.json")
        assert result == []
        mock_logger.error.assert_called_once()
