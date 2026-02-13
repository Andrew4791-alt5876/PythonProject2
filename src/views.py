from typing import Any

from src.utils import read_excel_file, hello_by_current_time, sort_operations_by_date, convert_amount_of_transactions, \
  read_json_file, price_of_stocks


def main_web_site() -> Any:
    hello_message = hello_by_current_time()
    df_excel = read_excel_file("../data/operations.xlsx")
    sorted_df_by_date = sort_operations_by_date(df_excel)
    list_nunber_card = list(set(list(sorted_df_by_date['Номер карты'])))
    list_of_cards = []
    for card in list_nunber_card:
        if isinstance(card, str):
            dict_sum_prices = {}
            dict_sum_prices["last_digits"] = card[-4:]
            sort_by_card = sorted_df_by_date[(sorted_df_by_date['Номер карты'] == card)]
            sum_of_prices = sum(sort_by_card['Сумма платежа'])
            dict_sum_prices["total_spent"] = sum_of_prices
            dict_sum_prices["cashback"] = round(sum_of_prices / 100, 2)
            list_of_cards.append(dict_sum_prices)
        elif isinstance(card, float):
            dict_sum_prices = {}
            dict_sum_prices["last_digits"] = card
            sort_by_card = sorted_df_by_date[(sorted_df_by_date['Номер карты']).isna()]
            sum_of_prices = sum(sort_by_card['Сумма платежа'])
            dict_sum_prices["total_spent"] = sum_of_prices
            dict_sum_prices["cashback"] = round(sum_of_prices / 100, 2)
            list_of_cards.append(dict_sum_prices)
    # user_setting_file = read_json_file('C:/Users/User/PycharmProjects/PythonProject2/user_settings.json')
    # list_course_currensies =[]
    # for currrency in user_setting_file[0]['user_currencies']:
    #     currrency_dict = {}
    #     currrency_dict["currency"] = currrency
    #     curse_to_rub = convert_amount_of_transactions(1, currrency)
    #     currrency_dict["rate"] = curse_to_rub
    #     list_course_currensies.append(currrency_dict)
    # dict_course_stocks = (price_of_stocks(user_setting_file[0]["user_stocks"]))
    # list_course_stocks = list(dict_course_stocks.items())
    list_course_currensies = []
    list_course_stocks = []
    message_to_frontend = {
  "greeting": hello_message,
  "cards": list_of_cards,
  "top_transactions": [
    {
      "date": "21.12.2021",
      "amount": 1198.23,
      "category": "Переводы",
      "description": "Перевод Кредитная карта. ТП 10.2 RUR"
    },
    {
      "date": "20.12.2021",
      "amount": 829.00,
      "category": "Супермаркеты",
      "description": "Лента"
    },
    {
      "date": "20.12.2021",
      "amount": 421.00,
      "category": "Различные товары",
      "description": "Ozon.ru"
    },
    {
      "date": "16.12.2021",
      "amount": -14216.42,
      "category": "ЖКХ",
      "description": "ЖКУ Квартира"
    },
    {
      "date": "16.12.2021",
      "amount": 453.00,
      "category": "Бонусы",
      "description": "Кешбэк за обычные покупки"
    }
  ],
  "currency_rates": list_course_currensies,
  "stock_prices": list_course_stocks
}
    return message_to_frontend


print(main_web_site())


# columns_of_df = [
#     'Дата операции',
#     'Дата платежа',
#     'Номер карты',
#     'Статус',
#     'Сумма операции',
#     'Валюта операции',
#     'Сумма платежа',
#     'Валюта платежа',
#     'Кэшбэк',
#     'Категория',
#     'MCC',
#     'Описание',
#     'Бонусы (включая кэшбэк)',
#     'Округление на инвесткопилку',
#     'Сумма операции с округлением'
# ]


# {
# 'AAPL': {'price': '261.95000'},
# 'AMZN': {'price': '199.17000'},
# 'GOOGL': {'price': '311.74000'},
# 'MSFT': {'price': '404.15000'},
# 'TSLA': {'price': '415.83500'}
# }