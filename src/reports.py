import json
import logging
from datetime import datetime
from typing import Any, Callable, Optional

import pandas as pd
from dateutil.relativedelta import relativedelta

from src.utils import configure_logger

logger = logging.getLogger("reports")
configure_logger(logger)


def log_reports(filename: Any | None = None) -> Any:
    """Внешняя функция, которая принимает аргумент для декоратора и возвращает внутренний декоратор."""

    def decorator(func: Callable) -> Callable:
        """Декоратор, который автоматически регистрирует детали выполнения функций."""

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            """Функция-обертка, которая записывает детали выполнения функции."""
            result = func(*args, **kwargs)
            if filename:
                logger.info(f"Путь для сохранения отчета {filename} указан пользователем")
                file_path = filename
            else:
                # Генерируем имя файла по умолчанию
                timestamp = datetime.now().strftime("%Y%m%d")
                func_name = func.__name__
                file_path = f"log_report/report_{func_name}_{timestamp}.json"
                logger.info(f"Путь для сохранения отчета {filename} сгенерирован автоматически")
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(
                        json.loads(result.to_json(orient="records", date_format="iso", force_ascii=False)),
                        f,
                        indent=2,
                        ensure_ascii=False,
                    )
                    logger.info(f"Отчет записан в файл {file_path}.")
                    return f"Отчет записан в файл {file_path}."
            except Exception as e:
                logger.error(f"Ошибка {str(e)}")
                return f"Ошибка {str(e)}"

        return wrapper

    return decorator


@log_reports()  # логи в консоль
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame | str:
    """Функция возвращает траты по заданной категории за последние три месяца"""
    if date is None:
        finish_date = datetime.now()
    else:
        finish_date = pd.Timestamp(date)
    start_date = finish_date - relativedelta(months=3)
    sort_finish_data = finish_date + relativedelta(days=1)
    try:
        transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], dayfirst=True)
        filtered_transactions = transactions.loc[
            (transactions["Дата операции"] >= start_date)
            & (transactions["Дата операции"] < sort_finish_data)
            & (transactions["Категория"] == category)
        ]
        return filtered_transactions
    except Exception as exc:
        return f"Ошибка {str(exc)}"
