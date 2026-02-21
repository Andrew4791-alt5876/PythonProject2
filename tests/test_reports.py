from typing import Any
from unittest.mock import MagicMock, mock_open, patch

from src.reports import log_reports


# Тесты для декоратора log_reports
@patch("src.reports.datetime")
@patch("builtins.open", new_callable=mock_open)
@patch("json.dump")
@patch("json.loads")
def test_log_reports_default_filename(
    mock_json_loads: Any, mock_json_dump: Any, mock_file_open: Any, mock_datetime: Any
) -> None:
    """Проверка, что при отсутствии filename генерируется имя и данные записываются."""
    # Фиксируем текущую дату
    mock_now = MagicMock()
    mock_now.strftime.return_value = "20230515"
    mock_datetime.now.return_value = mock_now
    # Моделируем DataFrame с методом to_json
    mock_df = MagicMock()
    mock_df.to_json.return_value = '[{"col": "val"}]'
    mock_json_loads.return_value = [{"col": "val"}]

    @log_reports()
    def test_func() -> MagicMock:
        return mock_df

    result = test_func()
    expected_filename = "log_report/report_test_func_20230515.json"
    mock_file_open.assert_called_once_with(expected_filename, "w", encoding="utf-8")
    mock_json_dump.assert_called_once_with([{"col": "val"}], mock_file_open(), indent=2, ensure_ascii=False)
    mock_df.to_json.assert_called_once_with(orient="records", date_format="iso", force_ascii=False)
    assert result == f"Отчет записан в файл {expected_filename}."


@patch("builtins.open", new_callable=mock_open)
@patch("json.dump")
@patch("json.loads")
def test_log_reports_custom_filename(mock_json_loads: Any, mock_json_dump: Any, mock_file_open: Any) -> None:
    """Проверка, что используется переданное имя файла."""
    mock_df = MagicMock()
    mock_df.to_json.return_value = '[{"key": 1}]'
    mock_json_loads.return_value = [{"key": 1}]

    @log_reports(filename="custom.json")
    def test_func() -> MagicMock:
        return mock_df

    result = test_func()
    mock_file_open.assert_called_once_with("custom.json", "w", encoding="utf-8")
    mock_json_dump.assert_called_once_with([{"key": 1}], mock_file_open(), indent=2, ensure_ascii=False)
    assert result == "Отчет записан в файл custom.json."


@patch("builtins.open", new_callable=mock_open)
@patch("json.dump")
def test_log_reports_write_exception(mock_json_dump: Any, mock_file_open: Any) -> None:
    """Проверка обработки исключения при записи файла."""
    mock_df = MagicMock()
    mock_df.to_json.return_value = "[]"
    # Имитируем ошибку при вызове json.dump
    mock_json_dump.side_effect = PermissionError("Access denied")

    @log_reports(filename="test.json")
    def test_func() -> MagicMock:
        return mock_df

    result = test_func()
    # Должно вернуться имя класса исключения
    assert result == "Ошибка Access denied"


@patch("builtins.open", new_callable=mock_open)
def test_log_reports_no_to_json_method(mock_file_open: Any) -> None:
    """Проверка, что если результат не имеет метода to_json, выбрасывается исключение."""

    @log_reports(filename="test.json")
    def test_func() -> dict[str, str]:
        return {"not": "dataframe"}  # нет метода to_json

    result = test_func()
    # Ожидаем AttributeError или что-то подобное, но т.к. AttributeError будет внутри, вернется его имя
    assert result == "Ошибка 'dict' object has no attribute 'to_json'"


@patch("src.reports.datetime")
@patch("builtins.open", new_callable=mock_open)
def test_log_reports_creates_directory(mock_file_open: Any, mock_datetime: Any) -> None:
    """Проверка формирования пути при генерации имени по умолчанию."""
    mock_now = MagicMock()
    mock_now.strftime.return_value = "20240101"
    mock_datetime.now.return_value = mock_now
    mock_df = MagicMock()
    mock_df.to_json.return_value = "[]"

    @log_reports()
    def test_func() -> MagicMock:
        return mock_df

    test_func()
    expected = "log_report/report_test_func_20240101.json"
    mock_file_open.assert_called_once_with(expected, "w", encoding="utf-8")


def test_log_reports_preserves_arguments() -> None:
    """Проверка, что декоратор передает аргументы в декорируемую функцию."""
    mock_func = MagicMock(return_value=MagicMock())
    mock_func.__name__ = "mock_func"
    # Декорируем mock-функцию
    decorated = log_reports(filename="dummy.json")(mock_func)
    # Вызываем с аргументами
    decorated(1, 2, key="value")
    # Проверяем, что исходная функция была вызвана с теми же аргументами
    mock_func.assert_called_once_with(1, 2, key="value")
