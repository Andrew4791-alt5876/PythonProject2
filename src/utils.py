import json
import logging
import os
import random
from datetime import datetime
from typing import Any, Dict, Union

import pandas as pd
import requests
from dotenv import load_dotenv
from pandas import DataFrame
from twelvedata import TDClient


logger = logging.getLogger("utils")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(
    "C:/Users/User/PycharmProjects/PythonProject2/logs/utils.log", "w", encoding="utf-8"
)
file_formater = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formater)
logger.addHandler(file_handler)


def read_excel_file(file_path_excel: Any = "") -> list | DataFrame | list[str]:
    """Функция, которая преобразует excel-файл в python базу данных"""
    if not isinstance(file_path_excel, str):
        logger.error("Ошибка пути к excel-файлу")
        return []
    try:
        df_excel_file = pd.read_excel(file_path_excel)
        list_df_excel_file = df_excel_file.to_dict("records")
        if isinstance(list_df_excel_file, list):
            logger.info("Excel-файл преобразован в DataFrame успешно")
            return df_excel_file
        else:
            logger.error("Файл не является списком, нет преобразования в DataFrame")
            return []
    except (FileNotFoundError, PermissionError, SyntaxError, TypeError, OSError) as ex:
        logger.error(f"Ошибка {str(ex)}")
        return []


def hello_by_current_time() -> str:
    """Функция, которая формирует приветственное сообщение в зависимости от фактического времени суток."""
    now_hour = datetime.now().hour
    if 6 <= now_hour < 12:
        hello_message = "Доброе утро!"
    elif 12 <= now_hour < 18:
        hello_message = "Добрый день!"
    elif 18 <= now_hour <= 23:
        hello_message = "Добрый вечер!"
    else:
        hello_message = "Доброй ночи!"
    logger.info(f"Приветственное сообщение в {now_hour} сформировано успешно как: {hello_message}")
    return hello_message


def sort_operations_by_date(data_frame: Any=[]) -> Any:
    """Функция, которая выполняет выборку с 1-го по текущую дату текущего месяца,
    год выбирается случайно в рамках базы данных."""
    try:
        now_day = datetime.now().day
        now_month = datetime.now().month
        data_frame["Дата операции"] = pd.to_datetime(
            data_frame["Дата операции"], format="%d.%m.%Y %H:%M:%S", errors="coerce"
        )
        sort_df_by_dates = data_frame[(data_frame["Дата операции"].dt.day <= now_day)]
        sort_df_by_month = sort_df_by_dates[(sort_df_by_dates["Дата операции"].dt.month == now_month)]
        randon_year = random.randint(2018, 2021)
        sort_df_by_year = sort_df_by_month[(sort_df_by_month["Дата операции"].dt.year == randon_year)]
        logger.info(f"Сортировка DataFrame произведена успешно с 1-го числа по {now_day}, месяц {now_month}, год {randon_year}")
        return sort_df_by_year
    except (TypeError, KeyError) as er:
        logger.error(f"Ошибка в функции sort_operations_by_date {str(er)}")
        return []


def convert_amount_of_transactions(amount: float, currency: str) -> Union[float, str]:
    """Функция конвертирования валюты из долларов или евро в рубли."""
    if currency not in ["USD", "EUR"]:
        logger.warning("Недопустимый код валюты для конвертации(допустимые: 'USD', 'EUR')")
        return 0
    if amount <= 0:
        logger.warning("Сумма должна быть положительной")
        return 0
    load_dotenv()
    API_KEY: str | None = os.getenv("API_KEY")
    if not API_KEY:
        logger.warning("API ключ не найден по курсу валюты")
        return 0
    url = "https://api.apilayer.com/currency_data/convert"
    headers = {"apikey": API_KEY}
    params: Dict[str, Union[str, float]] = {"to": "RUB", "from": currency, "amount": amount}
    try:
        response = requests.request("GET", url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        result = json.loads(response.text)
        if "result" in result and isinstance(result["result"], (int, float)):
            logger.info(f"Курс валюты {currency} получен успешно")
            return round(float(result["result"]), 2)
        else:
            logger.warning("Неверный формат ответа от API по курсу валюты")
            return 0
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка запроса: {str(e)}")
        return 0
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        logger.error(f"Ошибка обработки данных: {str(e)}")
        return 0


def price_of_stocks(stocks: Any) -> Any:
    """Функция для получения стоимости акций."""
    load_dotenv()
    API_KEY: str | None = os.getenv("API_KEY_STOCKS")
    if not API_KEY:
        logger.warning("API ключ не найден по стоимости акций")
        return {}
    try:
        td = TDClient(apikey=API_KEY)
        price = td.price(symbol=stocks).as_json()
        if isinstance(price, dict):
            logger.info(f"Стоимость акций {stocks} получена успешно")
            return price
        else:
            logger.warning("Неверный формат ответа от API по стоимости акций")
            return {}
    except requests.exceptions.RequestException as es:
        logger.error(f"Ошибка запроса: {str(es)}")
        return {}
    except KeyError as err:
        logger.error(f"Ошибка обработки данных: {str(err)}")
        return {}


def read_json_file(path: Any = "") -> list[dict]:
    """Функция, которая считывает и преобразует JSON-файл в Python-список"""
    if not isinstance(path, str):
        logger.warning("Не верный формат пути к JSON-файлу")
        return []
    try:
        with open(path, "r", encoding="utf-8") as file:
            try:
                data_operations = json.load(file)
                if isinstance(data_operations, list):
                    logger.info("JSON-файл преобразован в DataFrame успешно")
                    return data_operations
                else:
                    logger.warning("Не верный формат преобразования JSON-файла")
                    return []
            except json.JSONDecodeError as js:
                logger.error(f"Ошибка {str(js)}")
                return []
    except (FileNotFoundError, PermissionError, SyntaxError, TypeError, OSError) as er:
        logger.error(f"Ошибка {str(er)}")
        return []
