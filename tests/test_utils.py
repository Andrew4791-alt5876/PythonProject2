import json
import logging
from typing import Any
from unittest.mock import MagicMock, mock_open, patch

import pandas as pd
import pytest
import requests

from src.utils import (convert_amount_of_transactions, hello_by_current_time, price_of_stocks, read_excel_file,
                       read_json_file, sort_operations_by_date)


# Тесты для read_excel_file
class TestReadExcelFile:
    """Тесты для функции чтения Excel-файла."""

    # Успешное чтение
    @patch("src.utils.pd.read_excel")
    def test_success(self, mock_read_excel: MagicMock, caplog: Any) -> None:
        """Корректный Excel-файл."""
        # Создаём тестовый DataFrame
        test_df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
        mock_read_excel.return_value = test_df
        with caplog.at_level(logging.INFO):
            result = read_excel_file("valid_file.xlsx")
        # Проверяем, что возвращён именно DataFrame (оригинальный, не список)
        assert result is test_df
        assert isinstance(result, pd.DataFrame)
        assert "Excel-файл преобразован в DataFrame успешно" in caplog.text
        mock_read_excel.assert_called_once_with("valid_file.xlsx")

    # Путь не строка
    @pytest.mark.parametrize("invalid_path", [123, None, ["path"], {"path": "value"}])
    def test_path_not_string(self, invalid_path: Any, caplog: Any) -> None:
        """Путь передан не строкой."""
        with caplog.at_level(logging.ERROR):
            result = read_excel_file(invalid_path)
        assert result == []
        assert "Ошибка пути к excel-файлу" in caplog.text

    # Файл не найден
    @patch("src.utils.pd.read_excel", side_effect=FileNotFoundError("No such file"))
    def test_file_not_found(self, mock_read_excel: MagicMock, caplog: Any) -> None:
        """Файл не существует."""
        with caplog.at_level(logging.ERROR):
            result = read_excel_file("missing.xlsx")
        assert result == []
        assert "Ошибка No such file" in caplog.text

    # Недостаточно прав
    @patch("src.utils.pd.read_excel", side_effect=PermissionError("Permission denied"))
    def test_permission_error(self, mock_read_excel: MagicMock, caplog: Any) -> None:
        """Нет прав на чтение файла."""
        with caplog.at_level(logging.ERROR):
            result = read_excel_file("no_permission.xlsx")
        assert result == []
        assert "Ошибка Permission denied" in caplog.text

    # Другие OSError
    @patch("src.utils.pd.read_excel", side_effect=OSError("Some OS error"))
    def test_os_error(self, mock_read_excel: MagicMock, caplog: Any) -> None:
        """Общая ошибка ввода-вывода."""
        with caplog.at_level(logging.ERROR):
            result = read_excel_file("problematic.xlsx")
        assert result == []
        assert "Ошибка Some OS error" in caplog.text

    # Другие исключения, не входящие в перехватываемые (например, ValueError)
    # В текущей реализации они не обрабатываются и приведут к падению теста.
    # Это можно использовать для проверки, что функция не перехватывает лишнего.
    @patch("src.utils.pd.read_excel", side_effect=ValueError("Invalid file format"))
    def test_unhandled_exception(self, mock_read_excel: MagicMock) -> None:
        """Исключение, не входящее в список обрабатываемых, должно проброситься."""
        with pytest.raises(ValueError, match="Invalid file format"):
            read_excel_file("bad_format.xlsx")


# Тесты для hello_by_current_time
class TestHelloByCurrentTime:
    """Тесты для функции приветствия по времени суток."""

    @patch("src.utils.datetime")
    def test_morning(self, mock_datetime: Any, caplog: Any) -> None:
        """Тест на выдачу сообщения 'Доброе утро!'"""
        mock_now = mock_datetime.now.return_value
        mock_now.hour = 6
        with caplog.at_level(logging.INFO):
            result = hello_by_current_time()
        assert result == "Доброе утро!"
        assert "Приветственное сообщение в 6 сформировано успешно как: Доброе утро!" in caplog.text

    @patch("src.utils.datetime")
    def test_morning_lower_bound(self, mock_datetime: Any) -> None:
        """Тест на выдачу сообщения 'Доброе утро!' при нижней границе времени."""
        mock_now = mock_datetime.now.return_value
        mock_now.hour = 6
        assert hello_by_current_time() == "Доброе утро!"

    @patch("src.utils.datetime")
    def test_morning_upper_bound(self, mock_datetime: Any) -> None:
        """Тест на выдачу сообщения 'Доброе утро!' при верхней границе времени."""
        mock_now = mock_datetime.now.return_value
        mock_now.hour = 11
        assert hello_by_current_time() == "Доброе утро!"

    @patch("src.utils.datetime")
    def test_afternoon_lower_bound(self, mock_datetime: Any) -> None:
        """Тест на выдачу сообщения 'Добрый день!' при нижней границе времени."""
        mock_now = mock_datetime.now.return_value
        mock_now.hour = 12
        assert hello_by_current_time() == "Добрый день!"

    @patch("src.utils.datetime")
    def test_afternoon_upper_bound(self, mock_datetime: Any) -> None:
        """Тест на выдачу сообщения 'Добрый день!' при верхней границе времени."""
        mock_now = mock_datetime.now.return_value
        mock_now.hour = 17
        assert hello_by_current_time() == "Добрый день!"

    @patch("src.utils.datetime")
    def test_evening_lower_bound(self, mock_datetime: Any) -> None:
        """Тест на выдачу сообщения 'Добрый вечер!' при нижней границе времени."""
        mock_now = mock_datetime.now.return_value
        mock_now.hour = 18
        assert hello_by_current_time() == "Добрый вечер!"

    @patch("src.utils.datetime")
    def test_evening_upper_bound(self, mock_datetime: Any) -> None:
        """Тест на выдачу сообщения 'Добрый вечер!' при верхней границе времени."""
        mock_now = mock_datetime.now.return_value
        mock_now.hour = 23
        assert hello_by_current_time() == "Добрый вечер!"

    @patch("src.utils.datetime")
    def test_night_lower_bound(self, mock_datetime: Any) -> None:
        """Тест на выдачу сообщения 'Доброй ночи!' при нижней границе времени."""
        mock_now = mock_datetime.now.return_value
        mock_now.hour = 0
        assert hello_by_current_time() == "Доброй ночи!"

    @patch("src.utils.datetime")
    def test_night_upper_bound(self, mock_datetime: Any) -> None:
        """Тест на выдачу сообщения 'Доброй ночи!' при верхней границе времени."""
        mock_now = mock_datetime.now.return_value
        mock_now.hour = 5
        assert hello_by_current_time() == "Доброй ночи!"


# Тесты для sort_operations_by_date
class TestSortOperationsByDate:
    """Тесты для функции сортировки операций по дате."""

    @pytest.fixture
    def sample_dataframe(self) -> pd.DataFrame:
        """Создаёт тестовый DataFrame с разными датами."""
        data = {
            "Дата операции": [
                "01.01.2021 12:00:00",
                "15.03.2022 10:30:00",
                "20.05.2020 09:15:00",
                "10.11.2019 18:45:00",
                "25.12.2023 22:10:00",
                "05.07.2021 08:20:00",
            ],
            "Сумма": [100, 200, 300, 400, 500, 600],
        }
        return pd.DataFrame(data)

    @patch("src.utils.datetime")
    @patch("src.utils.random.randint")
    def test_success_filtering(
        self,
        mock_randint: MagicMock,
        mock_datetime: MagicMock,
        caplog: Any,
    ) -> None:
        # Настраиваем моки
        mock_now = mock_datetime.now.return_value
        mock_now.day = 10
        mock_now.month = 3
        mock_randint.return_value = 2021
        # Создаём DataFrame с одной подходящей строкой
        df = pd.DataFrame({"Дата операции": ["05.03.2021 14:00:00"], "Сумма": [700]})
        with caplog.at_level(logging.INFO):
            result = sort_operations_by_date(df)
        # Ожидаемый результат: та же строка, но с преобразованной датой
        expected = df.copy()
        expected["Дата операции"] = pd.to_datetime(expected["Дата операции"], format="%d.%m.%Y %H:%M:%S")
        pd.testing.assert_frame_equal(result.reset_index(drop=True), expected.reset_index(drop=True))
        assert "Сортировка DataFrame произведена успешно" in caplog.text
        # Проверяем, что лог содержит правильные параметры
        assert (
            f"с 1-го числа по {mock_now.day}, месяц {mock_now.month}, год {mock_randint.return_value}" in caplog.text
        )

    @patch("src.utils.datetime")
    @patch("src.utils.random.randint")
    def test_no_matching_records(
        self,
        mock_randint: MagicMock,
        mock_datetime: MagicMock,
        sample_dataframe: pd.DataFrame,
        caplog: Any,
    ) -> None:
        """
        Если нет записей, удовлетворяющих условиям, возвращается пустой DataFrame.
        """
        mock_now = mock_datetime.now.return_value
        mock_now.day = 10
        mock_now.month = 3
        mock_randint.return_value = 2021
        with caplog.at_level(logging.INFO):
            result = sort_operations_by_date(sample_dataframe)
        assert isinstance(result, pd.DataFrame)
        assert result.empty
        assert "Сортировка DataFrame произведена успешно" in caplog.text

    @patch("src.utils.datetime")
    @patch("src.utils.random.randint")
    def test_missing_column(
        self,
        mock_randint: MagicMock,
        mock_datetime: MagicMock,
        caplog: Any,
    ) -> None:
        """Отсутствует столбец 'Дата операции' -> KeyError -> возвращаем []."""
        df = pd.DataFrame({"Сумма": [100, 200]})
        mock_now = mock_datetime.now.return_value
        mock_now.day = 10
        mock_now.month = 3
        mock_randint.return_value = 2021
        with caplog.at_level(logging.ERROR):
            result = sort_operations_by_date(df)
        assert result == []
        assert "Ошибка в функции sort_operations_by_date" in caplog.text
        assert "KeyError" in caplog.text or "Дата операции" in caplog.text

    def test_input_not_dataframe(self, caplog: Any) -> None:
        """Если на вход подан не DataFrame (например, список) -> TypeError -> возвращаем []."""
        not_df = [{"a": 1}]  # список словарей
        with caplog.at_level(logging.ERROR):
            result = sort_operations_by_date(not_df)
        assert result == []
        assert "Ошибка в функции sort_operations_by_date" in caplog.text
        # Конкретное сообщение может быть разным, но важно, что логируется ошибка

    @patch("src.utils.datetime")
    @patch("src.utils.random.randint")
    def test_invalid_date_format(
        self,
        mock_randint: MagicMock,
        mock_datetime: MagicMock,
        caplog: Any,
    ) -> None:
        """
        Неправильный формат даты: pd.to_datetime с errors='coerce' не вызывает исключение,
        но если все даты стали NaT, то .dt.day может вызвать AttributeError? Нет, .dt работает,
        но для NaT возвращается NaT, и фильтрация просто не сработает. Однако ошибки не будет,
        просто не будет совпадений. Но если столбец существует, TypeError/KeyError не возникает.
        Поэтому этот тест проверяет, что функция не падает и логирует успех, но результат пуст.
        """
        df = pd.DataFrame({"Дата операции": ["не дата", "тоже не дата"], "Сумма": [1, 2]})
        mock_now = mock_datetime.now.return_value
        mock_now.day = 10
        mock_now.month = 3
        mock_randint.return_value = 2021
        with caplog.at_level(logging.INFO):
            result = sort_operations_by_date(df)
        assert isinstance(result, pd.DataFrame)
        assert result.empty
        assert "Сортировка DataFrame произведена успешно" in caplog.text


# Тесты для convert_amount_of_transactions
class TestConvertAmountOfTransactions:
    """Тесты для функции конвертации валют."""

    # Успешные сценарии
    @patch("src.utils.requests.request")
    @patch("src.utils.os.getenv")
    def test_success_usd(self, mock_getenv: MagicMock, mock_request: MagicMock, caplog: Any) -> None:
        """Успешная конвертация USD -> RUB."""
        mock_getenv.return_value = "valid_api_key"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = json.dumps({"result": 7500.50})
        mock_request.return_value = mock_response
        with caplog.at_level(logging.INFO):
            result = convert_amount_of_transactions(100.0, "USD")
        assert result == 7500.50
        assert "Курс валюты USD получен успешно" in caplog.text

    @patch("src.utils.requests.request")
    @patch("src.utils.os.getenv")
    def test_success_eur(self, mock_getenv: MagicMock, mock_request: MagicMock, caplog: Any) -> None:
        """Успешная конвертация EUR -> RUB."""
        mock_getenv.return_value = "valid_api_key"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = json.dumps({"result": 9000.75})
        mock_request.return_value = mock_response
        with caplog.at_level(logging.INFO):
            result = convert_amount_of_transactions(100.0, "EUR")
        assert result == 9000.75
        assert "Курс валюты EUR получен успешно" in caplog.text

    @patch("src.utils.requests.request")
    @patch("src.utils.os.getenv")
    def test_rounding(self, mock_getenv: MagicMock, mock_request: MagicMock) -> None:
        """Проверка округления до двух знаков."""
        mock_getenv.return_value = "valid_api_key"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = json.dumps({"result": 75.6789})
        mock_request.return_value = mock_response
        result = convert_amount_of_transactions(1.0, "USD")
        assert result == 75.68  # округление до двух знаков

    # Ошибочные сценарии
    @pytest.mark.parametrize(
        "currency, expected_log",
        [
            ("GBP", "Недопустимый код валюты"),
            ("RUB", "Недопустимый код валюты"),  # RUB тоже не разрешён?
        ],
    )
    def test_invalid_currency(self, currency: str, expected_log: str, caplog: Any) -> None:
        """Недопустимая валюта (не USD/EUR)."""
        with caplog.at_level(logging.WARNING):
            result = convert_amount_of_transactions(100.0, currency)
        assert result == 0
        assert "Недопустимый код валюты для конвертации(допустимые: 'USD', 'EUR')" in caplog.text

    @pytest.mark.parametrize("amount", [0, -10, -0.01])
    def test_non_positive_amount(self, amount: float, caplog: Any) -> None:
        """Сумма <= 0."""
        with caplog.at_level(logging.WARNING):
            result = convert_amount_of_transactions(amount, "USD")
        assert result == 0
        assert "Сумма должна быть положительной" in caplog.text

    @patch("src.utils.os.getenv")
    def test_missing_api_key(self, mock_getenv: MagicMock, caplog: Any) -> None:
        """Отсутствие API ключа."""
        mock_getenv.return_value = None
        with caplog.at_level(logging.WARNING):
            result = convert_amount_of_transactions(100.0, "USD")
        assert result == 0
        assert "API ключ не найден по курсу валюты" in caplog.text

    @patch("src.utils.os.getenv")
    def test_empty_api_key(self, mock_getenv: MagicMock, caplog: Any) -> None:
        """Пустой API ключ."""
        mock_getenv.return_value = ""
        with caplog.at_level(logging.WARNING):
            result = convert_amount_of_transactions(100.0, "USD")
        assert result == 0
        assert "API ключ не найден по курсу валюты" in caplog.text

    @patch("src.utils.requests.request")
    @patch("src.utils.os.getenv")
    def test_request_exception(self, mock_getenv: MagicMock, mock_request: MagicMock, caplog: Any) -> None:
        """Ошибка запроса (например, соединение)."""
        mock_getenv.return_value = "valid_api_key"
        mock_request.side_effect = requests.exceptions.ConnectionError("Connection failed")
        with caplog.at_level(logging.ERROR):
            result = convert_amount_of_transactions(100.0, "USD")
        assert result == 0
        assert "Ошибка запроса: Connection failed" in caplog.text

    @patch("src.utils.requests.request")
    @patch("src.utils.os.getenv")
    def test_http_error(self, mock_getenv: MagicMock, mock_request: MagicMock, caplog: Any) -> None:
        """HTTP ошибка (например, 404)."""
        mock_getenv.return_value = "valid_api_key"
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Client Error")
        mock_request.return_value = mock_response
        with caplog.at_level(logging.ERROR):
            result = convert_amount_of_transactions(100.0, "USD")
        assert result == 0
        assert "Ошибка запроса: 404 Client Error" in caplog.text

    @patch("src.utils.requests.request")
    @patch("src.utils.os.getenv")
    def test_timeout(self, mock_getenv: MagicMock, mock_request: MagicMock, caplog: Any) -> None:
        """Таймаут запроса."""
        mock_getenv.return_value = "valid_api_key"
        mock_request.side_effect = requests.exceptions.Timeout("Request timed out")
        with caplog.at_level(logging.ERROR):
            result = convert_amount_of_transactions(100.0, "USD")
        assert result == 0
        assert "Ошибка запроса: Request timed out" in caplog.text

    @patch("src.utils.requests.request")
    @patch("src.utils.os.getenv")
    def test_invalid_json(self, mock_getenv: MagicMock, mock_request: MagicMock, caplog: Any) -> None:
        """Ответ не в формате JSON."""
        mock_getenv.return_value = "valid_api_key"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "not a json"
        mock_request.return_value = mock_response
        with caplog.at_level(logging.ERROR):
            result = convert_amount_of_transactions(100.0, "USD")
        assert result == 0
        assert "Ошибка обработки данных: Expecting value" in caplog.text

    @patch("src.utils.requests.request")
    @patch("src.utils.os.getenv")
    def test_no_result_field(self, mock_getenv: MagicMock, mock_request: MagicMock, caplog: Any) -> None:
        """Ответ не содержит поле 'result'."""
        mock_getenv.return_value = "valid_api_key"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = json.dumps({"error": "something"})
        mock_request.return_value = mock_response
        with caplog.at_level(logging.WARNING):
            result = convert_amount_of_transactions(100.0, "USD")
        assert result == 0
        assert "Неверный формат ответа от API по курсу валюты" in caplog.text

    @patch("src.utils.requests.request")
    @patch("src.utils.os.getenv")
    def test_result_not_number(self, mock_getenv: MagicMock, mock_request: MagicMock, caplog: Any) -> None:
        """Поле 'result' не является числом."""
        mock_getenv.return_value = "valid_api_key"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = json.dumps({"result": "abc"})
        mock_request.return_value = mock_response
        with caplog.at_level(logging.WARNING):
            result = convert_amount_of_transactions(100.0, "USD")
        assert result == 0
        assert "Неверный формат ответа от API по курсу валюты" in caplog.text


# Тесты для price_of_stocks
class TestPriceOfStocks:
    """Тесты для функции получения стоимости акций."""

    @patch("src.utils.TDClient")
    @patch("src.utils.os.getenv")
    def test_success(self, mock_getenv: MagicMock, mock_tdclient: MagicMock, caplog: Any) -> None:
        """Успешное получение цены акций."""
        # Настройка мока для API ключа
        mock_getenv.return_value = "valid_api_key"
        # Настройка мока для TDClient
        mock_td_instance = MagicMock()
        mock_tdclient.return_value = mock_td_instance
        # Мокаем цепочку вызовов: td.price(symbol=...).as_json()
        mock_price = MagicMock()
        mock_td_instance.price.return_value = mock_price
        expected_price = {"symbol": "AAPL", "price": 150.25}
        mock_price.as_json.return_value = expected_price
        with caplog.at_level(logging.INFO):
            result = price_of_stocks("AAPL")
        assert result == expected_price
        assert "Стоимость акций AAPL получена успешно" in caplog.text
        mock_td_instance.price.assert_called_once_with(symbol="AAPL")

    @patch("src.utils.os.getenv")
    def test_missing_api_key(self, mock_getenv: MagicMock, caplog: Any) -> None:
        """Отсутствие API ключа (None)."""
        mock_getenv.return_value = None
        with caplog.at_level(logging.WARNING):
            result = price_of_stocks("AAPL")
        assert result == {}
        assert "API ключ не найден по стоимости акций" in caplog.text

    @patch("src.utils.os.getenv")
    def test_empty_api_key(self, mock_getenv: MagicMock, caplog: Any) -> None:
        """Пустой API ключ."""
        mock_getenv.return_value = ""
        with caplog.at_level(logging.WARNING):
            result = price_of_stocks("AAPL")
        assert result == {}
        assert "API ключ не найден по стоимости акций" in caplog.text

    @patch("src.utils.TDClient")
    @patch("src.utils.os.getenv")
    def test_request_exception(self, mock_getenv: MagicMock, mock_tdclient: MagicMock, caplog: Any) -> None:
        """Ошибка запроса к API."""
        mock_getenv.return_value = "valid_api_key"
        mock_td_instance = MagicMock()
        mock_tdclient.return_value = mock_td_instance
        # Имитируем исключение при вызове price
        mock_td_instance.price.side_effect = requests.exceptions.RequestException("Connection error")
        with caplog.at_level(logging.ERROR):
            result = price_of_stocks("AAPL")
        assert result == {}
        assert "Ошибка запроса: Connection error" in caplog.text

    @patch("src.utils.TDClient")
    @patch("src.utils.os.getenv")
    def test_key_error(self, mock_getenv: MagicMock, mock_tdclient: MagicMock, caplog: Any) -> None:
        """Ошибка KeyError при обработке ответа."""
        mock_getenv.return_value = "valid_api_key"
        mock_td_instance = MagicMock()
        mock_tdclient.return_value = mock_td_instance
        # Имитируем KeyError внутри цепочки вызовов (например, в as_json)
        mock_price = MagicMock()
        mock_td_instance.price.return_value = mock_price
        mock_price.as_json.side_effect = KeyError("missing_field")
        with caplog.at_level(logging.ERROR):
            result = price_of_stocks("AAPL")
        assert result == {}
        assert "Ошибка обработки данных: 'missing_field'" in caplog.text

    @patch("src.utils.TDClient")
    @patch("src.utils.os.getenv")
    def test_invalid_response_format(self, mock_getenv: MagicMock, mock_tdclient: MagicMock, caplog: Any) -> None:
        """Ответ от API не является словарём."""
        mock_getenv.return_value = "valid_api_key"
        mock_td_instance = MagicMock()
        mock_tdclient.return_value = mock_td_instance
        mock_price = MagicMock()
        mock_td_instance.price.return_value = mock_price
        mock_price.as_json.return_value = ["not", "a", "dict"]  # список вместо словаря
        with caplog.at_level(logging.WARNING):
            result = price_of_stocks("AAPL")
        assert result == {}
        assert "Неверный формат ответа от API по стоимости акций" in caplog.text


# Тесты для read_json_file
class TestReadJsonFile:
    """Тесты для функции чтения JSON-файла."""

    # Успешное чтение
    @patch("builtins.open", new_callable=mock_open, read_data='[{"key": "value"}]')
    def test_success(self, mock_file: MagicMock, caplog: Any) -> None:
        """Корректный JSON-файл со списком."""
        with caplog.at_level(logging.INFO):
            result = read_json_file("valid_path.json")
        assert result == [{"key": "value"}]
        assert "JSON-файл преобразован в DataFrame успешно" in caplog.text
        mock_file.assert_called_once_with("valid_path.json", "r", encoding="utf-8")

    # Путь не строка
    @pytest.mark.parametrize("invalid_path", [123, None, ["path"], {"path": "value"}])
    def test_path_not_string(self, invalid_path: Any, caplog: Any) -> None:
        """Путь передан не строкой."""
        with caplog.at_level(logging.WARNING):
            result = read_json_file(invalid_path)
        assert result == []
        assert "Не верный формат пути к JSON-файлу" in caplog.text

    # Файл не найден
    @patch("builtins.open", side_effect=FileNotFoundError("No such file"))
    def test_file_not_found(self, mock_open: MagicMock, caplog: Any) -> None:
        """Файл не существует."""
        with caplog.at_level(logging.ERROR):
            result = read_json_file("missing.json")
        assert result == []
        assert "Ошибка No such file" in caplog.text

    # Недостаточно прав
    @patch("builtins.open", side_effect=PermissionError("Permission denied"))
    def test_permission_error(self, mock_open: MagicMock, caplog: Any) -> None:
        """Нет прав на чтение файла."""
        with caplog.at_level(logging.ERROR):
            result = read_json_file("no_permission.json")
        assert result == []
        assert "Ошибка Permission denied" in caplog.text

    # Другие OSError
    @patch("builtins.open", side_effect=OSError("Some OS error"))
    def test_os_error(self, mock_open: MagicMock, caplog: Any) -> None:
        """Общая ошибка ввода-вывода."""
        with caplog.at_level(logging.ERROR):
            result = read_json_file("problematic.json")
        assert result == []
        assert "Ошибка Some OS error" in caplog.text

    # Содержимое не список (например, словарь)
    @patch("builtins.open", new_callable=mock_open, read_data='{"key": "value"}')
    def test_content_not_list(self, mock_file: MagicMock, caplog: Any) -> None:
        """JSON содержит объект, а не список."""
        with caplog.at_level(logging.WARNING):
            result = read_json_file("dict.json")
        assert result == []
        assert "Не верный формат преобразования JSON-файла" in caplog.text

    # Некорректный JSON (ошибка парсинга)
    @patch("builtins.open", new_callable=mock_open, read_data='{"key": value"}')  # невалидный JSON
    def test_json_decode_error(self, mock_file: MagicMock, caplog: Any) -> None:
        """Файл содержит некорректный JSON."""
        with caplog.at_level(logging.ERROR):
            result = read_json_file("invalid.json")
        assert result == []
        assert "Ошибка" in caplog.text
