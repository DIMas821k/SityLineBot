from ..imports import *
import pandas as pd
import sqlite3
from config import database_path


def my_lower(s):
    return s.lower()  # Встроенная функция Python для работы с Unicode


@dp.message(F.text.lower().split()[0] == "помощь")
async def Help(message: types.Message):
    conn = sqlite3.connect(database_path)
    conn.create_function("my_lower", 1, my_lower)

    query = f"SELECT ПОМОЩЬ FROM actions WHERE my_lower(name) LIKE my_lower(\"%{message.text[7:]}%\")"
    df = pd.read_sql_query(query, conn)
    if len(df.values) == 0:
        answer = "Команда не найдена"
    else:
        answer = str(df.values[0][0])
    await message.reply(answer)
