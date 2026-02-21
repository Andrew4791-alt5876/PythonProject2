from typing import Any
from unittest.mock import call, patch

import pandas as pd
import pytest

from src.services import input_user_month, input_user_year, sort_data_by_categories, sort_operations_by_user_month_year


# Тесты для input_user_month
@patch("builtins.input")
def test_input_user_month_correct_first_try(mock_input: Any) -> None:
    """Пользователь сразу вводит корректный месяц."""
    mock_input.return_value = "5"
    result = input_user_month()
    assert result == 5
    mock_input.assert_called_once_with(
        "Введите месяц за который необходим анализ\n" "(от 1 до 12, где 1-январь...12-декабрь): "
    )


@patch("builtins.input")
def test_input_user_month_correct_after_invalid_string(mock_input: Any) -> None:
    """Пользователь вводит буквы, затем корректное число."""
    mock_input.side_effect = ["abc", "7"]
    result = input_user_month()
    assert result == 7
    assert mock_input.call_count == 2
    mock_input.assert_has_calls(
        [
            call("Введите месяц за который необходим анализ\n" "(от 1 до 12, где 1-январь...12-декабрь): "),
            call("Не верные данные ввода месяца, попробуйте еще раз\n" "(от 1 до 12, где 1-январь...12-декабрь): "),
        ]
    )


@patch("builtins.input")
def test_input_user_month_correct_after_out_of_range(mock_input: Any) -> None:
    """Пользователь вводит числа вне допустимого диапазона, затем корректное."""
    mock_input.side_effect = ["0", "13", "3"]
    result = input_user_month()
    assert result == 3
    assert mock_input.call_count == 3
    # Проверяем, что после неверных чисел сообщение об ошибке такое же, как и после букв
    expected_calls = [
        call("Введите месяц за который необходим анализ\n" "(от 1 до 12, где 1-январь...12-декабрь): "),
        call("Не верные данные ввода месяца, попробуйте еще раз\n" "(от 1 до 12, где 1-январь...12-декабрь): "),
        call("Не верные данные ввода месяца, попробуйте еще раз\n" "(от 1 до 12, где 1-январь...12-декабрь): "),
    ]
    mock_input.assert_has_calls(expected_calls)


@patch("builtins.input")
def test_input_user_month_empty_then_correct(mock_input: Any) -> None:
    """Пользователь вводит пустую строку (просто Enter), затем корректный месяц."""
    mock_input.side_effect = ["", "9"]
    result = input_user_month()
    assert result == 9
    assert mock_input.call_count == 2
    # Первый вызов с начальным приглашением, второй с сообщением об ошибке (пустой ввод не считается числом)
    mock_input.assert_has_calls(
        [
            call("Введите месяц за который необходим анализ\n" "(от 1 до 12, где 1-январь...12-декабрь): "),
            call("Не верные данные ввода месяца, попробуйте еще раз\n" "(от 1 до 12, где 1-январь...12-декабрь): "),
        ]
    )


@patch("builtins.input")
def test_input_user_month_multiple_empty_then_correct(mock_input: Any) -> None:
    """Несколько пустых вводов, затем корректный."""
    mock_input.side_effect = ["", "", "", "2"]
    result = input_user_month()
    assert result == 2
    assert mock_input.call_count == 4
    # Проверяем, что первый вызов с основным приглашением, остальные с сообщением об ошибке
    calls = mock_input.call_args_list
    assert calls[0] == call("Введите месяц за который необходим анализ\n" "(от 1 до 12, где 1-январь...12-декабрь): ")
    for i in range(1, 4):
        assert calls[i] == call(
            "Не верные данные ввода месяца, попробуйте еще раз\n" "(от 1 до 12, где 1-январь...12-декабрь): "
        )


@patch("builtins.input")
def test_input_user_month_never_correct(mock_input: Any) -> None:
    """Тест проверяет, что функция не завершается, пока не получит корректный ввод."""
    # Устанавливаем 10 неверных вводов подряд (буквы, числа вне диапазона, пустые)
    mock_input.side_effect = ["abc", "0", "", "13", "xyz"] * 2  # 10 неверных значений
    # Мы не ожидаем, что функция завершится сама, поэтому запускаем её в контексте,
    # где после 10 вызовов input возникнет StopIteration (так как side_effect исчерпан).
    # Функция попытается вызвать input в 11-й раз, и это вызовет StopIteration.
    with pytest.raises(StopIteration):
        input_user_month()
    # Проверяем, что input был вызван ровно 11 раз (до исчерпания side_effect), так как 10 неверных вводов
    assert mock_input.call_count == 11
    # Можно также проверить, что все вызовы были с корректными приглашениями
    for i, call_args in enumerate(mock_input.call_args_list):
        if i == 0:
            expected = call("Введите месяц за который необходим анализ\n" "(от 1 до 12, где 1-январь...12-декабрь): ")
        else:
            expected = call(
                "Не верные данные ввода месяца, попробуйте еще раз\n" "(от 1 до 12, где 1-январь...12-декабрь): "
            )
        assert call_args == expected


# Тесты для input_user_year
@patch("builtins.input")
def test_input_user_year_correct_first_try(mock_input: Any) -> None:
    """Пользователь сразу вводит корректный год."""
    mock_input.return_value = "2020"
    result = input_user_year()
    assert result == 2020
    mock_input.assert_called_once_with("Введите год за который необходим анализ (2018 до 2021): ")


@patch("builtins.input")
def test_input_user_year_correct_after_invalid_string(mock_input: Any) -> None:
    """Пользователь вводит буквы, затем корректный год."""
    mock_input.side_effect = ["abc", "2019"]
    result = input_user_year()
    assert result == 2019
    assert mock_input.call_count == 2
    mock_input.assert_has_calls(
        [
            call("Введите год за который необходим анализ (2018 до 2021): "),
            call("Не верные данные ввода года, попробуйте еще раз\n" "(2018 до 2021): "),
        ]
    )


@patch("builtins.input")
def test_input_user_year_correct_after_out_of_range(mock_input: Any) -> None:
    """Пользователь вводит числа вне допустимого диапазона, затем корректный."""
    mock_input.side_effect = ["2017", "2022", "2021"]
    result = input_user_year()
    assert result == 2021
    assert mock_input.call_count == 3
    expected_calls = [
        call("Введите год за который необходим анализ (2018 до 2021): "),
        call("Не верные данные ввода года, попробуйте еще раз\n" "(2018 до 2021): "),
        call("Не верные данные ввода года, попробуйте еще раз\n" "(2018 до 2021): "),
    ]
    mock_input.assert_has_calls(expected_calls)


@patch("builtins.input")
def test_input_user_year_empty_then_correct(mock_input: Any) -> None:
    """Пользователь вводит пустую строку (Enter), затем корректный год."""
    mock_input.side_effect = ["", "2020"]
    result = input_user_year()
    assert result == 2020
    assert mock_input.call_count == 2
    mock_input.assert_has_calls(
        [
            call("Введите год за который необходим анализ (2018 до 2021): "),
            call("Не верные данные ввода года, попробуйте еще раз\n" "(2018 до 2021): "),
        ]
    )


@patch("builtins.input")
def test_input_user_year_multiple_invalid_then_correct(mock_input: Any) -> None:
    """Несколько неверных вводов (буквы, числа вне диапазона, пустые), затем корректный."""
    mock_input.side_effect = ["abc", "2016", "", "2023", "2018"]
    result = input_user_year()
    assert result == 2018
    assert mock_input.call_count == 5
    calls = mock_input.call_args_list
    assert calls[0] == call("Введите год за который необходим анализ (2018 до 2021): ")
    for i in range(1, 5):
        assert calls[i] == call("Не верные данные ввода года, попробуйте еще раз\n" "(2018 до 2021): ")


@patch("builtins.input")
def test_input_user_year_never_correct(mock_input: Any) -> None:
    """Проверка, что функция продолжает запрашивать ввод при бесконечных неверных данных."""
    # 10 неверных вводов подряд
    mock_input.side_effect = ["abc", "2015", "", "2023", "xyz"] * 2  # 10 элементов
    with pytest.raises(StopIteration):
        input_user_year()
    # Последний (11-й) вызов вызывает StopIteration, поэтому call_count == 11
    assert mock_input.call_count == 11
    # Проверим, что все вызовы, кроме первого, были с сообщением об ошибке
    calls = mock_input.call_args_list
    assert calls[0] == call("Введите год за который необходим анализ (2018 до 2021): ")
    for i in range(1, 11):
        assert calls[i] == call("Не верные данные ввода года, попробуйте еще раз\n" "(2018 до 2021): ")


# Тесты для sort_operations_by_user_month_year
@patch("src.services.input_user_month")
@patch("src.services.input_user_year")
def test_sort_operations_by_user_month_year_valid(mock_year: Any, mock_month: Any) -> None:
    """Проверка корректной фильтрации по введённым месяцу и году."""
    # Задаём возвращаемые значения для моков
    mock_month.return_value = 5
    mock_year.return_value = 2020
    # Создаём тестовый DataFrame с разными датами
    data = {
        "Дата операции": [
            "15.05.2020 12:30:00",  # подходит
            "20.05.2020 14:20:00",  # подходит
            "05.06.2020 10:00:00",  # другой месяц
            "25.05.2021 09:15:00",  # другой год
            "10.05.2020 18:45:00",  # подходит
            "неправильная дата",  # будет NaT
        ]
    }
    df = pd.DataFrame(data)
    # Вызов функции
    result = sort_operations_by_user_month_year(df)
    # Ожидаем, что останутся только строки с маем 2020 года (3 шт.)
    assert len(result) == 3
    # Проверяем, что все даты имеют нужный месяц и год
    assert all(result["Дата операции"].dt.month == 5)
    assert all(result["Дата операции"].dt.year == 2020)
    # Проверяем, что функции ввода были вызваны
    mock_month.assert_called_once()
    mock_year.assert_called_once()


@patch("src.services.input_user_month")
@patch("src.services.input_user_year")
def test_sort_operations_by_user_month_year_no_matches(mock_year: Any, mock_month: Any) -> None:
    """Если нет транзакций за указанный месяц/год, возвращается пустой DataFrame."""
    mock_month.return_value = 12
    mock_year.return_value = 2019
    data = {"Дата операции": ["15.05.2020 12:30:00", "20.05.2020 14:20:00"]}
    df = pd.DataFrame(data)
    result = sort_operations_by_user_month_year(df)
    assert result.empty
    mock_month.assert_called_once()
    mock_year.assert_called_once()


@patch("src.services.input_user_month")
@patch("src.services.input_user_year")
def test_sort_operations_by_user_month_year_invalid_dates(mock_year: Any, mock_month: Any) -> None:
    """Строки с некорректными датами (NaT) должны игнорироваться при фильтрации."""
    mock_month.return_value = 3
    mock_year.return_value = 2021
    data = {
        "Дата операции": [
            "15.03.2021 12:30:00",  # подходит
            "invalid date",  # NaT
            "20.03.2021 14:20:00",  # подходит
            "не дата",  # NaT
        ]
    }
    df = pd.DataFrame(data)
    result = sort_operations_by_user_month_year(df)
    assert len(result) == 2
    assert all(result["Дата операции"].dt.month == 3)
    assert all(result["Дата операции"].dt.year == 2021)


@patch("src.services.input_user_month")
@patch("src.services.input_user_year")
def test_sort_operations_by_user_month_year_empty_df(mock_year: Any, mock_month: Any) -> None:
    """Пустой DataFrame на входе должен вернуть пустой DataFrame."""
    mock_month.return_value = 7
    mock_year.return_value = 2022
    df = pd.DataFrame(columns=["Дата операции"])
    result = sort_operations_by_user_month_year(df)
    assert result.empty
    # Всё равно должны быть вызваны функции ввода
    mock_month.assert_called_once()
    mock_year.assert_called_once()


@patch("src.services.input_user_month")
@patch("src.services.input_user_year")
def test_sort_operations_by_user_month_year_month_year_order(mock_year: Any, mock_month: Any) -> None:
    """Проверка, что фильтрация сначала по месяцу, потом по году (логика не важна, главное результат)."""
    mock_month.return_value = 8
    mock_year.return_value = 2018
    data = {
        "Дата операции": [
            "15.08.2018 12:30:00",  # подходит
            "20.08.2019 14:20:00",  # другой год
            "05.09.2018 10:00:00",  # другой месяц
        ]
    }
    df = pd.DataFrame(data)
    result = sort_operations_by_user_month_year(df)
    assert len(result) == 1
    assert result.iloc[0]["Дата операции"] == pd.Timestamp("2018-08-15 12:30:00")


# Тесты для sort_data_by_categories
@patch("src.services.sort_operations_by_user_month_year")
@patch("src.services.read_excel_file")
def test_sort_data_by_categories_success(mock_read_excel: Any, mock_sort: Any) -> None:
    data = {
        "Категория": ["Супермаркеты", "Аптеки", "Переводы", "Кафе", "Бонусы", "Супермаркеты"],
        "Сумма платежа": [100.50, 250.00, -50.00, 300.75, 200.00, 50.00],
    }
    filtered_df = pd.DataFrame(data)
    mock_read_excel.return_value = pd.DataFrame()  # не важно
    mock_sort.return_value = filtered_df
    result = sort_data_by_categories(filtered_df)
    expected = {"Супермаркеты": 150.5, "Аптеки": 250.0, "Кафе": 300.75}
    assert result == expected
    mock_sort.assert_called_once_with(filtered_df)
    mock_read_excel.assert_not_called()


@patch("src.services.sort_operations_by_user_month_year")
@patch("src.services.read_excel_file")
def test_sort_data_by_categories_no_excluded_categories(mock_read_excel: Any, mock_sort: Any) -> None:
    """Проверка, что если нет категорий из списка исключения, возвращаются все."""
    data = {"Категория": ["Такси", "Интернет", "Телефон"], "Сумма платежа": [500.00, 300.50, 150.25]}
    filtered_df = pd.DataFrame(data)
    mock_read_excel.return_value = pd.DataFrame()
    mock_sort.return_value = filtered_df
    result = sort_data_by_categories('df_excel')
    # После сортировки по возрастанию: Телефон (150.25), Интернет (300.5), Такси (500)
    expected = {"Телефон": 150.25, "Интернет": 300.5, "Такси": 500.0}
    assert result == expected


@patch("src.services.sort_operations_by_user_month_year")
@patch("src.services.read_excel_file")
def test_sort_data_by_categories_empty_after_filter(mock_read_excel: Any, mock_sort: Any) -> None:
    """Если после фильтрации по месяцу/году DataFrame пуст, возвращается пустой словарь."""
    empty_df = pd.DataFrame(columns=["Категория", "Сумма платежа"])
    mock_read_excel.return_value = pd.DataFrame()
    mock_sort.return_value = empty_df
    result = sort_data_by_categories('df_excel')
    assert result == {}


@patch("src.services.sort_operations_by_user_month_year")
@patch("src.services.read_excel_file")
def test_sort_data_by_categories_all_excluded(mock_read_excel: Any, mock_sort: Any) -> None:
    """Если все категории попадают в список исключения, возвращается пустой словарь."""
    data = {
        "Категория": ["Бонусы", "Переводы", "Пополнения", "Наличные", "Зарплата"],
        "Сумма платежа": [100, 200, 300, 400, 500],
    }
    filtered_df = pd.DataFrame(data)
    mock_read_excel.return_value = pd.DataFrame()
    mock_sort.return_value = filtered_df
    result = sort_data_by_categories('df_excel')
    assert result == {}


@patch("src.services.sort_operations_by_user_month_year")
@patch("src.services.read_excel_file")
def test_sort_data_by_categories_rounding(mock_read_excel: Any, mock_sort: Any) -> None:
    """Проверка округления сумм до двух знаков."""
    data = {"Категория": ["Продукты", "Одежда"], "Сумма платежа": [100.555, 200.999]}
    filtered_df = pd.DataFrame(data)
    mock_read_excel.return_value = pd.DataFrame()
    mock_sort.return_value = filtered_df
    result = sort_data_by_categories('df_excel')
    expected = {"Продукты": 100.56, "Одежда": 201.0}
    assert result == expected
