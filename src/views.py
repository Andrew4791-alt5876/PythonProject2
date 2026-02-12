from typing import Any

from src.utils import read_excel_file, hello_by_current_time, sort_operations_by_date, convert_amount_of_transactions


def main_web_site() -> Any:
    hello_message = hello_by_current_time()
    df_excel = read_excel_file("../data/operations.xlsx")
    sorted_df_by_date = sort_operations_by_date(df_excel)
    curse_usd_rub = convert_amount_of_transactions(1, 'USD')
    curse_eur_rub = convert_amount_of_transactions(1, 'EUR')
    message_to_frontend = {
  "greeting": hello_message,
  "cards": [
    {
      "last_digits": "5814",
      "total_spent": 1262.00,
      "cashback": 12.62
    },
    {
      "last_digits": "7512",
      "total_spent": 7.94,
      "cashback": 0.08
    }
  ],
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
  "currency_rates": [
    {
      "currency": "USD",
      "rate": curse_usd_rub
    },
    {
      "currency": "EUR",
      "rate": curse_eur_rub
    }
  ],
  "stock_prices": [
    {
      "stock": "AAPL",
      "price": 150.12
    },
    {
      "stock": "AMZN",
      "price": 3173.18
    },
    {
      "stock": "GOOGL",
      "price": 2742.39
    },
    {
      "stock": "MSFT",
      "price": 296.71
    },
    {
      "stock": "TSLA",
      "price": 1007.08
    }
  ]
}
    return sorted_df_by_date['Номер карты']


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