from typing import Any

from src.utils import (convert_amount_of_transactions, hello_by_current_time, price_of_stocks, read_excel_file,
                       read_json_file, sort_operations_by_date)


def main_web_site() -> Any:
    """Функция генерации JSON-ответа для страницы «Главная»."""

    # Формирование JSON-ответа в части "greeting".
    hello_message = hello_by_current_time()

    # Преобразование excel-файла в DataFrame.
    df_excel = read_excel_file("../data/operations.xlsx")
    sorted_df_by_date = sort_operations_by_date(df_excel)

    # Формирование JSON-ответа в части "cards".
    list_number_card = list(set(list(sorted_df_by_date["Номер карты"])))
    list_of_cards = []
    for card in list_number_card:
        if isinstance(card, str):
            dict_sum_prices = {}
            dict_sum_prices["last_digits"] = card[-4:]
            sort_by_card = sorted_df_by_date[(sorted_df_by_date["Номер карты"] == card)]
            sum_of_prices = sum(sort_by_card["Сумма платежа"])
            dict_sum_prices["total_spent"] = round(sum_of_prices, 2)
            if round(sum_of_prices, 2) < 0:
                cashback = abs(sum_of_prices / 100)
            else:
                cashback = 0
            dict_sum_prices["cashback"] = round(cashback, 2)
            list_of_cards.append(dict_sum_prices)
        elif isinstance(card, float):
            dict_sum_prices = {}
            dict_sum_prices["last_digits"] = str(card)
            sort_by_card = sorted_df_by_date[(sorted_df_by_date["Номер карты"]).isna()]
            sum_of_prices = sum(sort_by_card["Сумма платежа"])
            dict_sum_prices["total_spent"] = round(sum_of_prices, 2)
            if round(sum_of_prices, 2) < 0:
                cashback = abs(sum_of_prices / 100)
            else:
                cashback = 0
            dict_sum_prices["cashback"] = round(cashback, 2)
            list_of_cards.append(dict_sum_prices)

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

    # Формирование JSON-ответа в части "currency_rates".
    user_setting_file = read_json_file("C:/Users/User/PycharmProjects/PythonProject2/user_settings.json")
    list_course_currensies = []
    for currrency in user_setting_file[0]["user_currencies"]:
        currrency_dict = {}
        currrency_dict["currency"] = currrency
        curse_to_rub = convert_amount_of_transactions(1, currrency)
        currrency_dict["rate"] = curse_to_rub
        list_course_currensies.append(currrency_dict)

    # Формирование JSON-ответа в части "stock_prices".
    dict_course_stocks = price_of_stocks(user_setting_file[0]["user_stocks"])
    list_course_stocks = []
    for i in user_setting_file[0]["user_stocks"]:
        dict_stocks = {}
        dict_stocks["stock"] = i
        dict_stocks["price"] = round(float(dict_course_stocks[i]["price"]), 2)
        list_course_stocks.append(dict_stocks)

    # Вывод JSON-ответа для web-сайта.
    message_to_frontend = {
        "greeting": hello_message,
        "cards": list_of_cards,
        "top_transactions": list_top_transactions,
        "currency_rates": list_course_currensies,
        "stock_prices": list_course_stocks,
    }
    return message_to_frontend
