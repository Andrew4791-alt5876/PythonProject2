import json
import os
import random
from datetime import datetime
from typing import Union, Dict

import pandas as pd
import requests
from pandas import DataFrame
from dotenv import load_dotenv
from twelvedata import TDClient

def read_excel_file(file_path_excel: str = "") -> list | DataFrame | list[str]:
    """Функция, которая преобразует excel-файл в python базу данных"""
    if not isinstance(file_path_excel, str):
        return []
    try:
        df_excel_file = pd.read_excel(file_path_excel)
        list_df_excel_file = df_excel_file.to_dict("records")
        if isinstance(list_df_excel_file, list):
            return df_excel_file
        else:
            return []
    except (FileNotFoundError, PermissionError, SyntaxError, TypeError, OSError):
        return []


def hello_by_current_time():
    now_hour = datetime.now().hour
    if 6 <= now_hour < 12:
        hello_message = 'Доброе утро!'
    elif 12 <= now_hour < 18:
        hello_message = 'Добрый день!'
    elif 18 <= now_hour <= 23:
        hello_message = 'Добрый вечер!'
    else:
        hello_message = 'Доброй ночи!'
    return hello_message


def sort_operations_by_date(data_frame):
    data_frame['Дата операции'] = pd.to_datetime(
        data_frame['Дата операции'],
        format='%d.%m.%Y %H:%M:%S',
        errors='coerce'
    )
    now_day = datetime.now().day
    now_month = datetime.now().month
    sort_df_by_dates = data_frame[(data_frame['Дата операции'].dt.day <= now_day)]
    sort_df_by_month = sort_df_by_dates[(sort_df_by_dates['Дата операции'].dt.month == now_month)]
    # randon_year = random.randint(2018, 2021)
    randon_year = 2018
    sort_df_by_year = sort_df_by_month[(sort_df_by_month['Дата операции'].dt.year == randon_year)]
    return sort_df_by_year


def convert_amount_of_transactions(amount: float, currency: str) -> Union[float, str]:
    """Функция конвертирования валюты из долларов или евро в рубли."""
    if currency not in ["USD", "EUR", "RUB"]:
        return "Недопустимый код валюты для конвертации"
    if amount <= 0:
        return "Сумма должна быть положительной"
    load_dotenv()
    API_KEY: str | None = os.getenv("API_KEY")
    if not API_KEY:
        return "API ключ не найден"
    url = "https://api.apilayer.com/currency_data/convert"
    headers = {"apikey": API_KEY}
    params: Dict[str, Union[str, float]] = {"to": "RUB", "from": currency, "amount": amount}
    try:
        response = requests.request("GET", url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        result = json.loads(response.text)
        if "result" in result and isinstance(result["result"], (int, float)):
            return round(float(result["result"]), 2)
        else:
            return "Неверный формат ответа от API"
    except requests.exceptions.RequestException as e:
        return f"Ошибка запроса: {str(e)}"
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        return f"Ошибка обработки данных: {str(e)}"


def price_of_stocks(stocks):
    load_dotenv()
    API_KEY: str = os.getenv("API_KEY_STOCKS")
    td = TDClient(apikey=API_KEY)
    price = td.price(symbol=stocks).as_json()
    return price


# print(price_of_stocks(["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]))
