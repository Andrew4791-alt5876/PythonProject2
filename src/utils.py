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


def configure_logger(logger: Any) -> None:
    """Конфигурация логгера для проекта"""
    module_short = logger.name.split(".")[-1]
    log_file = os.path.join("logs", f"{module_short}.log")
    # Чтобы не дублировать обработчики при повторных вызовах, очищаем старые
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
    handler = logging.FileHandler(log_file, "w", encoding="utf-8")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


logger = logging.getLogger("utils")
configure_logger(logger)


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


def sort_operations_by_date(data_frame: Any) -> Any:
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
        logger.info(
            f"Сортировка DataFrame произведена успешно с 1-го числа по {now_day}, месяц {now_month}, год {randon_year}"
        )
        return sort_df_by_year
    except (TypeError, KeyError) as er:
        logger.error(f"Ошибка в функции sort_operations_by_date {str(er)}")
        return []


def create_json_info_cards(sorted_transactions: DataFrame, list_user_card: list) -> Any:
    """Функция формирования ответа по разделу cards для страницы 'Главная'"""
    list_of_cards = []
    for card in list_user_card:
        # Обработка строки (нормальный номер карты)
        if isinstance(card, str):
            last_digits = card[-4:] if len(card) >= 4 else card
            mask = sorted_transactions["Номер карты"] == card
        # Обработка отсутствующего значения (NaN, None)
        elif pd.isna(card):
            last_digits = "NaN"
            mask = sorted_transactions["Номер карты"].isna()
        # Обработка чисел (int, float, но не NaN)
        else:
            # Числовой номер карты
            str_card = str(card)  # строковое представление для сравнения
            clean_card = str_card.replace(".", "").replace(" ", "")  # очистка для last_digits
            last_digits = clean_card[-4:] if len(clean_card) >= 4 else clean_card
            mask = sorted_transactions["Номер карты"] == str_card  # сравнение со строкой
        # Расчёт суммы и кэшбэка
        sort_by_card = sorted_transactions[mask]
        sum_of_prices = sort_by_card["Сумма платежа"].sum()
        rounded_sum = float(round(sum_of_prices, 2))
        if rounded_sum < 0:
            cashback = float(round(abs(rounded_sum / 100), 2))
        else:
            cashback = 0
        dict_sum_prices = {"last_digits": last_digits, "total_spent": rounded_sum, "cashback": cashback}
        list_of_cards.append(dict_sum_prices)
        return list_of_cards


def create_json_info_top(sorted_transactions_top: DataFrame) -> Any:
    """Функция формирования ответа по разделу top_transactions для страницы 'Главная'"""
    df_sorted_top_transactions = sorted_transactions_top.sort_values(
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
        return list_top_transactions


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
        if isinstance(result["result"], (int, float)):
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


def create_info_user_currency(user_currency: list) -> list:
    """Функция формирования ответа по разделу currency_rates для страницы 'Главная'"""
    list_of_coursies = []
    for currrency in user_currency[0]["user_currencies"]:
        currrency_dict = {}
        currrency_dict["currency"] = currrency
        curse_to_rub = convert_amount_of_transactions(1, currrency)
        if curse_to_rub == 0:
            logger.warning(f"Курс валюты {currrency} не доступен")
        else:
            currrency_dict["rate"] = curse_to_rub
            list_of_coursies.append(currrency_dict)
            logger.info(f"Курс валюты {currrency} доступен")
    return list_of_coursies


def price_of_stocks(stocks: Any) -> Any:
    """Функция для получения стоимости акций."""
    load_dotenv()
    API_KEY_STOCKS: str | None = os.getenv("API_KEY_STOCKS")
    if not API_KEY_STOCKS:
        logger.warning("API ключ не найден по стоимости акций")
        return {}
    try:
        td = TDClient(apikey=API_KEY_STOCKS)
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


def create_info_stocks(user_stocks_file: list) -> list:
    """Функция формирования ответа по разделу currency_rates для страницы 'Главная'"""
    dict_course_stocks = price_of_stocks(user_stocks_file[0]["user_stocks"])
    list_course_stocks = []
    for i in user_stocks_file[0]["user_stocks"]:
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
    return list_course_stocks


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
