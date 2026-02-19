import os
import tempfile
from typing import Generator, Any

import pandas as pd
import pytest
from pandas import DataFrame


# Фикстура для создания тестового DataFrame операций
@pytest.fixture
def sample_transactions_df() -> DataFrame:
    data = {
        "Номер карты": ["*3456", "*3456", "*7654", None],
        "Дата операции": ["01.01.2023", "02.01.2023", "03.01.2023", "04.01.2023"],
        "Сумма платежа": [-1500.50, 200.75, 3200.00, 50.00],
        "Категория": ["Супермаркеты", "Рестораны", "Переводы", "Аптеки"],
        "Описание": ["Покупка продуктов", "Обед", "Перевод другу", "Лекарства"],
    }
    return pd.DataFrame(data)


# Фикстура для тестовых настроек пользователя
@pytest.fixture
def user_settings() -> list:
    return [{"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "GOOGL"]}]


@pytest.fixture
def sample_excel_file() -> Generator[str, Any, None]:
    """Создаёт временный Excel-файл с данными и возвращает его путь."""
    data = {
        "Дата операции": ["01.01.2023", "02.01.2023"],
        "Категория": ["Супермаркеты", "Фастфуд"],
        "Сумма": [100, 250],
    }
    df = pd.DataFrame(data)
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        file_path = tmp.name
    df.to_excel(file_path, index=False)
    yield file_path
    # Удаляем файл после завершения теста
    os.unlink(file_path)
