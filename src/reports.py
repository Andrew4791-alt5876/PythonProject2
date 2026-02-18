import json
from datetime import datetime
from typing import Any, Callable, Optional

import pandas as pd
from dateutil.relativedelta import relativedelta

from src.utils import read_excel_file



def log_reports(filename: Any | None = None) -> Any:
    """Внешняя функция, которая принимает аргумент для декоратора и возвращает внутренний декоратор."""

    def decorator(func: Callable) -> Callable:
        """Декоратор, который автоматически регистрирует детали выполнения функций."""

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            """Функция-обертка, которая записывает детали выполнения функции."""
            result = func(*args, **kwargs)
            if filename:
                file_path = filename
            else:
                # Генерируем имя файла по умолчанию
                timestamp = datetime.now().strftime("%Y%m%d")
                func_name = func.__name__
                file_path = f"../log_report/report_{func_name}_{timestamp}.json"
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(
                        json.loads(
                            result.to_json(
                                orient='records',
                                date_format='iso',
                                force_ascii=False
                            )
                        ), f, indent=2, ensure_ascii=False)
                    return f'Отчет записан в файл {file_path}.'
            except Exception as e:
                return type(e).__name__
        return wrapper
    return decorator


@log_reports()  # логи в консоль
def spending_by_category(transactions: pd.DataFrame,
                         category: str,
                         date: Optional[str] = None) -> pd.DataFrame:
    """Функция возвращает траты по заданной категории за последние три месяца """
    if date is None:
        finish_date = datetime.now()
    else:
        finish_date = pd.Timestamp(date)
    start_date = finish_date - relativedelta(months=3)
    sort_finish_data = finish_date + relativedelta(days=1)
    transactions['Дата операции'] = pd.to_datetime(transactions['Дата операции'], dayfirst=True)
    filtered_transactions = transactions.loc[
        (transactions['Дата операции'] >= start_date) &
        (transactions['Дата операции'] < sort_finish_data) &
        (transactions['Категория'] == category)
    ]
    return filtered_transactions

# '2026-02-17 18:07:32.015166'
# transactions = read_excel_file("../data/operations.xlsx")
# print(spending_by_category(transactions,'Рестораны', '2019-02-17'))
# ['Категория']
# {'Авиабилеты',
#  'Связь',
#  'Сервис',
#  'Услуги банка',
#  'Зарплата',
#  'Пополнения',
#  'ЖКХ',
#  'Медицина',
#  'Отели',
#  'НКО',
#  'Фастфуд',
#  'Развлечения',
#  'Рестораны',
#  'Такси',
#  'Книги',
#  'Ж/д билеты',
#  'Мобильная связь',
#  'Каршеринг',
#  'Транспорт',
#  'Детские товары',
#  'Наличные',
#  'Красота',
#  nan,
#  'Аптеки',
#  'Фото и видео',
#  'Онлайн-кинотеатры',
#  'Турагентства',
#  'Спорттовары',
#  'Другое',
#  'Местный транспорт',
#  'Переводы',
#  'Сувениры',
#  'Цветы',
#  'Различные товары',
#  'Супермаркеты',
#  'Дом и ремонт',
#  'Образование',
#  'Топливо',
#  'Автоуслуги',
#  'Кино',
#  'Частные услуги',
#  'Косметика',
#  'Электроника и техника',
#  'Финансы',
#  'Канцтовары',
#  'Duty Free',
#  'Госуслуги',
#  'Искусство',
#  'Бонусы',
#  'Одежда и обувь'}