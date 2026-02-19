import logging
from typing import Any

import pandas as pd

from src.utils import (convert_amount_of_transactions, hello_by_current_time, price_of_stocks, read_excel_file,
                       read_json_file, sort_operations_by_date)

logger = logging.getLogger("views")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(
    "C:/Users/User/PycharmProjects/PythonProject2/logs/views.log", "w", encoding="utf-8"
)
file_formater = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formater)
logger.addHandler(file_handler)


def main_web_site() -> Any:
    """Функция генерации JSON-ответа для страницы «Главная»."""

    # Формирование JSON-ответа в части "greeting".
    hello_message = hello_by_current_time()
    logger.info("Приветствие создано")

    # Преобразование excel-файла в DataFrame.
    df_excel = read_excel_file("../data/operations.xlsx")
    sorted_df_by_date = sort_operations_by_date(df_excel)
    logger.info("База данных преобразована в DataFrame")

    # Формирование JSON-ответа в части "cards".
    list_number_card = list(set(list(sorted_df_by_date["Номер карты"])))
    list_of_cards = []
    for card in list_number_card:
        # Обработка строки (нормальный номер карты)
        if isinstance(card, str):
            last_digits = card[-4:] if len(card) >= 4 else card
            mask = sorted_df_by_date["Номер карты"] == card

        # Обработка отсутствующего значения (NaN, None)
        elif pd.isna(card):
            last_digits = "NaN"
            mask = sorted_df_by_date["Номер карты"].isna()

        # Обработка чисел (int, float, но не NaN)
        else:
            # Преобразуем в строку, удаляем возможные разделители
            str_card = str(card).replace(".", "").replace(" ", "")
            last_digits = str_card[-4:] if len(str_card) >= 4 else str_card
            mask = sorted_df_by_date["Номер карты"] == card

        # Расчёт суммы и кэшбэка
        sort_by_card = sorted_df_by_date[mask]
        sum_of_prices = sort_by_card["Сумма платежа"].sum()
        rounded_sum = float(round(sum_of_prices, 2))
        if rounded_sum < 0:
            cashback = float(round(abs(rounded_sum / 100), 2))
        else:
            cashback = 0

        dict_sum_prices = {"last_digits": last_digits, "total_spent": rounded_sum, "cashback": cashback}
        list_of_cards.append(dict_sum_prices)
    logger.info("Сформирован JSON-ответ в части cards")

    # Формирование JSON-ответа в части "top_transactions".
    df_sorted_top_transactions = sorted_df_by_date.sort_values(
        by="Сумма платежа", key=lambda col: col.abs(), ascending=False
    )
    list_info_top = df_sorted_top_transactions.head(5).to_dict("records")
    list_top_transactions = []
    for transactions in list_info_top:
        dict_top_transaction = {}
        date_str = (str(transactions["Дата операции"]))[:10]
        dict_top_transaction["date"] = date_str
        dict_top_transaction["amount"] = transactions["Сумма платежа"]
        dict_top_transaction["category"] = transactions["Категория"]
        dict_top_transaction["description"] = transactions["Описание"]
        list_top_transactions.append(dict_top_transaction)
    logger.info("Сформирован JSON-ответ в части top_transactions")

    # Формирование JSON-ответа в части "currency_rates".
    user_setting_file = read_json_file("C:/Users/User/PycharmProjects/PythonProject2/user_settings.json")
    list_course_currensies = []
    for currrency in user_setting_file[0]["user_currencies"]:
        currrency_dict = {}
        currrency_dict["currency"] = currrency
        curse_to_rub = convert_amount_of_transactions(1, currrency)
        if curse_to_rub == 0:
            logger.warning(f"Курс валюты {currrency} не доступен")
        else:
            currrency_dict["rate"] = curse_to_rub
            list_course_currensies.append(currrency_dict)
            logger.info("Сформирован JSON-ответ в части currency_rates")

    # Формирование JSON-ответа в части "stock_prices".
    dict_course_stocks = price_of_stocks(user_setting_file[0]["user_stocks"])
    list_course_stocks = []
    for i in user_setting_file[0]["user_stocks"]:
        dict_stocks = {}
        dict_stocks["stock"] = i
        if dict_course_stocks != {}:
            dict_stocks["price"] = round(float(dict_course_stocks[i]["price"]), 2)
            list_course_stocks.append(dict_stocks)
            logger.info("Сформирован JSON-ответ в части stock_prices")
        else:
            dict_stocks["price"] = 0
            list_course_stocks.append(dict_stocks)
            logger.warning(f"Стоимость акции {i} не доступна")

    # Вывод JSON-ответа для web-сайта.
    message_to_frontend = {
        "greeting": hello_message,
        "cards": list_of_cards,
        "top_transactions": list_top_transactions,
        "currency_rates": list_course_currensies,
        "stock_prices": list_course_stocks,
    }
    logger.info("Вывод JSON-ответа для web-сайта выполнен успешно")
    return message_to_frontend
