from typing import Any

import pandas as pd
from pandas import DataFrame


def read_excel_file(file_path_excel: str = "") -> list[Any] | DataFrame | list[str]:
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
        return ['B']


print(read_excel_file("../data/operations.xlsx"))
