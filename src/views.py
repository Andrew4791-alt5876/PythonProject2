import logging
from typing import Any

from src.utils import (configure_logger, create_info_stocks, create_info_user_currency, create_json_info_cards,
                       create_json_info_top, hello_by_current_time, read_json_file, sort_operations_by_date)

logger = logging.getLogger("views")
configure_logger(logger)


def main_web_site(df_transactions: Any) -> Any:
    """Функция генерации JSON-ответа для страницы «Главная»."""

    # Формирование JSON-ответа в части "greeting".
    hello_message = hello_by_current_time()
    logger.info("Приветствие создано")

    # Преобразование excel-файла в DataFrame.
    sorted_df_date = sort_operations_by_date(df_transactions)
    logger.info("База данных преобразована в отсортированный DataFrame по датам")

    # Формирование JSON-ответа в части "cards".
    list_number_card = sorted_df_date["Номер карты"].unique().tolist()
    list_of_cards = create_json_info_cards(sorted_df_date, list_number_card)
    logger.info("Сформирован JSON-ответ в части cards")

    # Формирование JSON-ответа в части "top_transactions".
    list_top_transactions = create_json_info_top(sorted_df_date)
    logger.info("Сформирован JSON-ответ в части top_transactions")

    # Формирование JSON-ответа в части "currency_rates".
    user_setting_file = read_json_file("user_settings.json")
    list_course_currensies = create_info_user_currency(user_setting_file)
    logger.info("Ответ в части 'currency_rates' получен")

    # Формирование JSON-ответа в части "stock_prices".
    list_course_stocks = create_info_stocks(user_setting_file)
    logger.info("Ответ в части 'stock_prices' получен")

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
