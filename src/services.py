from typing import Any

import pandas as pd

from src.utils import read_excel_file


def input_user_month() -> int | None:
    """Функция для получения месяца от пользователя."""
    user_month = input("Введите месяц за который необходим анализ\n"
                       "(от 1 до 12, где 1-январь...12-декабрь): ")
    while user_month or user_month == "":
        if user_month.isdigit():
            if 1 <= int(user_month) <= 12:
                return int(user_month)
            else:
                user_month = input("Не верные данные ввода месяца, попробуйте еще раз\n"
                                   "(от 1 до 12, где 1-январь...12-декабрь): ")
        else:
            user_month = input("Не верные данные ввода месяца, попробуйте еще раз\n"
                               "(от 1 до 12, где 1-январь...12-декабрь): ")
    return None


def input_user_year() -> int | None:
    """Функция для получения года от пользователя."""
    user_year = input("Введите год за который необходим анализ (2018 до 2021): ")
    while user_year or user_year == "":
        if user_year.isdigit():
            if 2018 <= int(user_year) <= 2021:
                return int(user_year)
            else:
                user_year = input("Не верные данные ввода года, попробуйте еще раз\n"
                                  "(2018 до 2021): ")
        else:
            user_year = input("Не верные данные ввода года, попробуйте еще раз\n"
                              "(2018 до 2021): ")
    return None


def sort_operations_by_user_month_year(data_frame: Any) -> Any:
    """Функция, которая выполняет выборку базы данных по месяцу и году от пользователя."""
    data_frame["Дата операции"] = pd.to_datetime(
        data_frame["Дата операции"], format="%d.%m.%Y %H:%M:%S", errors="coerce"
    )
    input_month = input_user_month()
    input_year = input_user_year()
    sort_df_by_month = data_frame[(data_frame["Дата операции"].dt.month == input_month)]
    sort_df_by_user = sort_df_by_month[(sort_df_by_month["Дата операции"].dt.year == input_year)]
    return sort_df_by_user


def sort_data_by_categories() -> dict:
    """Функция, которая преобразовывает базу данных в словарь {категория: сумма платежа}."""
    df_excel = read_excel_file("../data/operations.xlsx")
    df_choose_user = sort_operations_by_user_month_year(df_excel)
    df_grouped = df_choose_user.groupby("Категория")["Сумма платежа"].sum().to_dict()
    sorted_items = dict(sorted(df_grouped.items(), key=lambda item: item[1], reverse=False))
    list_of_categories = ["Бонусы", "Переводы", "Пополнения", "Наличные", "Зарплата"]
    for category in list_of_categories:
        sorted_items.pop(category, None)
    sorted_items_rounded = {k: round(v, 2) for k, v in sorted_items.items()}
    return sorted_items_rounded
