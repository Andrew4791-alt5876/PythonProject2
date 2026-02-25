# Курсовая работа по Python

# 📋 Содержание

1. Название проекта и описание
2. Требования
3. Установка (клонирование, виртуальное окружение, зависимости)
4. Настройка (файлы данных, переменные окружения для API ключей)
5. Запуск (основные функции)
6. Тестирование
7. Линтеры и форматирование
8. Структура проекта
9. Примеры использования
10. Лицензия
11. Контакты

## 📖 Описание
### Финансовый аналитический сервис

Проект представляет собой набор инструментов для анализа банковских транзакций, конвертации валют, получения стоимости акций и формирования отчётов. 
Основные функции:
- Формирование информации в виде JSON-файла дла web-страниц (пока реализован ответ страницы "Главная")
- Формирование информации по сервисам в виде словаря (пока реализован сервис для анализа максимального кэшбэка)
- Формирование и запись отчета либо в файл, который вводит пользователь, либо в файл, который создается автоматически.

## Требования

- Python 3.9 или выше
- Установленный Git
- (Опционально) [uv](https://docs.astral.sh/uv/) для быстрой работы с зависимостями

## Установка (клонирование, виртуальное окружение, зависимости)

1. **Клонируйте репозиторий:**

   git clone <ссылка-на-репозиторий>
   cd <имя-папки-проекта>

2. **Создайте виртуальное окружение и активируйте его:**

   python -m venv venv 
   source venv/bin/activate      # для Linux/macOS
   или venv\Scripts\activate     # для Windows

3. **Установите зависимости:**

   pip install -e .

   **Или, если используете uv:**

   uv venv
   source .venv/bin/activate
   uv pip install -e .

   **Для разработки также рекомендуется установить группы зависимостей (линтеры, тесты):**

   pip install -e . --group dev --group lint

## Настройка (файлы данных, переменные окружения для API ключей)

Файлы данных
user_settings.json – файл с настройками пользователя (пример):
[
  {
    "user_currencies": ["USD", "EUR"],
    "user_stocks": ["AAPL", "GOOGL"]
  }
]
Рекомендуется разместить его в корне проекта или указать абсолютный путь в коде.

API ключи
Для работы конвертации валют и получения цен акций необходимы ключи:

Currency API (apilayer) – ключ в переменной окружения API_KEY.

Twelve Data API – ключ в переменной окружения API_KEY_STOCKS.

Создайте файл .env в корне проекта и укажите:
API_KEY=your_currency_api_key
API_KEY_STOCKS=your_twelvedata_api_key

Логи
Логи сохраняются в папку logs/ (создаётся автоматически):

utils.log – общие утилиты

views.log – веб-страница

services.log – сервисы анализа

reports.log – отчёты

Запуск
Основная функция для получения JSON-ответа веб-страницы:
from src.views import main_web_site

result = main_web_site()
print(result)

Пример вызова из командной строки:

python -c "from src.views import main_web_site; print(main_web_site())"

Для анализа по категориям за выбранный месяц/год:
from src.services import sort_data_by_categories

print(sort_data_by_categories())

Для отчёта по категории за последние 3 месяца (с сохранением в JSON):

from src.reports import spending_by_category
import pandas as pd

df = pd.read_excel("../data/operations.xlsx")
result = spending_by_category(df, "Супермаркеты")
print(result)

естирование
Проект покрыт тестами pytest. Запустите все тесты:

pytest

С отчётом о покрытии:

pytest --cov=src --cov-report=term-missing

Линтеры и форматирование
Для поддержания качества кода используются:

black – форматирование

isort – сортировка импортов (совместим с black)

flake8 – линтинг

mypy – статическая типизация

Запустить форматирование:

bash
black src/ tests/
isort src/ tests/
Проверить стиль и типы:

bash
flake8 src/ tests/
mypy src/ tests/
Pre-commit (рекомендуется)
Установите pre-commit и активируйте хуки:

bash
pip install pre-commit
pre-commit install
После этого перед каждым коммитом будет автоматически запускаться проверка кода.

Структура проекта
text
.
├── src/
│   ├── __init__.py
│   ├── views.py          # Формирование JSON-файла для главной страницы
│   ├── utils.py          # Утилиты: чтение файлов, конвертация, приветствие, сортировка
│   ├── services.py       # Анализ по категориям с вводом месяца/года
│   └── reports.py        # Декоратор логирования и отчёты по категориям
├── tests/
│   ├── __init__.py
│   ├── test_views.py     # Тесты для модуля формирования JSON-файла для главной страницы
│   ├── test_utils.py     # Тесты для модуля utils
│   ├── test_services.py  # Тесты для модуля services
│   ├── test_reports.py   # Тесты для модуля reports
│   └── conftest.py       # Фикстуры pytest
├── logs/                 # Папка для логов (создаётся автоматически)
├── data/                 # Рекомендуемое место для Excel-файлов
├── .env                  # Переменные окружения (не в репозитории)
├── .gitignore            # Git игнор
├── pyproject.toml        # Конфигурация проекта и зависимостей
├── README.md             # Этот файл
└── ...
Пример использования класса Number (из дополнительных заданий)
python
class Number:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value

    def add(self, val):
        self.value += val

    def subtract(self, val):
        self.value -= val

x = Number(7)
print(x.get())      # 7
x.add(3)
print(x.get())      # 10
x.subtract(5)
print(x.get())      # 5
Лицензия
Этот проект распространяется под лицензией MIT. Подробнее см. файл LICENSE (если есть).

Контакты
Автор: Ваше Имя
GitHub: ваш-профиль
Email: ваш@email.com

text

Этот README охватывает все основные аспекты проекта, инструкции по установке, настройке и использованию. Пользователь сможет легко разобраться в коде и запустить его.
markdown
# Финансовый аналитический сервис

Проект представляет собой набор инструментов для анализа банковских транзакций, конвертации валют, получения стоимости акций и формирования отчётов. Основные функции:
- Приветствие в зависимости от времени суток
- Чтение данных из Excel и JSON
- Фильтрация операций по дате
- Конвертация валют (USD, EUR → RUB) через внешний API
- Получение цен акций через Twelve Data API
- Формирование отчётов с декоратором логирования
- Веб-страница с JSON-ответом (greeting, cards, top_transactions, currency_rates, stock_prices)

## Требования

- Python 3.9 или выше
- Установленный Git
- (Опционально) [uv](https://docs.astral.sh/uv/) для быстрой работы с зависимостями

## Установка

1. **Клонируйте репозиторий:**
   ```bash
   git clone <ссылка-на-репозиторий>
   cd <имя-папки-проекта>
Создайте виртуальное окружение и активируйте его:

bash
python -m venv venv
source venv/bin/activate      # для Linux/macOS
# или venv\Scripts\activate   # для Windows
Установите зависимости:

bash
pip install -e .
Или, если используете uv:

bash
uv venv
source .venv/bin/activate
uv pip install -e .
Для разработки также рекомендуется установить группы зависимостей (линтеры, тесты):

bash
pip install -e . --group dev --group lint
Настройка
Файлы данных
Проект ожидает наличие следующих файлов (пути можно изменить в коде):

../data/operations.xlsx – Excel-файл с историей операций (обязательные колонки: "Номер карты", "Дата операции", "Сумма платежа", "Категория", "Описание").

user_settings.json – файл с настройками пользователя (пример):

json
[
  {
    "user_currencies": ["USD", "EUR"],
    "user_stocks": ["AAPL", "GOOGL"]
  }
]
Рекомендуется разместить его в корне проекта или указать абсолютный путь в коде.

API ключи
Для работы конвертации валют и получения цен акций необходимы ключи:

Currency API (apilayer) – ключ в переменной окружения API_KEY.

Twelve Data API – ключ в переменной окружения API_KEY_STOCKS.

Создайте файл .env в корне проекта и укажите:

text
API_KEY=your_currency_api_key
API_KEY_STOCKS=your_twelvedata_api_key
Логи
Логи сохраняются в папку logs/ (создаётся автоматически):

utils.log – общие утилиты

views.log – веб-страница

services.log – сервисы анализа

reports.log – отчёты

Запуск
Основная функция для получения JSON-ответа веб-страницы:

python
from src.views import main_web_site

result = main_web_site()
print(result)
Пример вызова из командной строки:

bash
python -c "from src.views import main_web_site; print(main_web_site())"
Для анализа по категориям за выбранный месяц/год:

python
from src.services import sort_data_by_categories

print(sort_data_by_categories())
Для отчёта по категории за последние 3 месяца (с сохранением в JSON):

python
from src.reports import spending_by_category
import pandas as pd

df = pd.read_excel("../data/operations.xlsx")
result = spending_by_category(df, "Супермаркеты")
print(result)
Тестирование
Проект покрыт тестами pytest. Запустите все тесты:

bash
pytest
С отчётом о покрытии:

bash
pytest --cov=src --cov-report=term-missing
Линтеры и форматирование
Для поддержания качества кода используются:

black – форматирование

isort – сортировка импортов (совместим с black)

flake8 – линтинг

mypy – статическая типизация

Запустить форматирование:

bash
black src/ tests/
isort src/ tests/
Проверить стиль и типы:

bash
flake8 src/ tests/
mypy src/ tests/
Pre-commit (рекомендуется)
Установите pre-commit и активируйте хуки:

bash
pip install pre-commit
pre-commit install
После этого перед каждым коммитом будет автоматически запускаться проверка кода.

Структура проекта
text
.
├── src/
│   ├── __init__.py
│   ├── views.py          # Формирование JSON для главной страницы
│   ├── utils.py          # Утилиты: чтение файлов, конвертация, приветствие, сортировка
│   ├── services.py       # Анализ по категориям с вводом месяца/года
│   └── reports.py        # Декоратор логирования и отчёты по категориям
├── tests/
│   ├── __init__.py
│   ├── test_views.py
│   ├── test_utils.py
│   ├── test_services.py
│   ├── test_reports.py
│   └── conftest.py       # Фикстуры pytest
├── logs/                 # Папка для логов (создаётся автоматически)
├── data/                 # Рекомендуемое место для Excel-файлов
├── .env                  # Переменные окружения (не в репозитории)
├── .gitignore
├── pyproject.toml        # Конфигурация проекта и зависимостей
├── README.md
└── ...

Лицензия
Этот проект распространяется под лицензией MIT. Подробнее см. файл LICENSE (если есть).

Контакты
Автор: Ваше Имя
GitHub: ваш-профиль
Email: ваш@email.com