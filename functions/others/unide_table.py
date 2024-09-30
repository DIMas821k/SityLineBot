import sqlite3
from config import  database_path
# Соединяемся с базой данных
conn = sqlite3.connect(database_path)
cursor = conn.cursor()


# Функция для получения списка колонок
def get_columns(table_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    return [col[1] for col in cursor.fetchall()]


# Получаем колонки из таблиц inventory и buildings
inventory_columns = get_columns("inventory")
buildings_columns = get_columns("buildings")

# Создаём список объединённых колонок, избегая дублирования 'id'
combined_columns = ["id"] + [col for col in inventory_columns if col != "id"] + [col for col in buildings_columns if
                                                                                 col != "id"]

# Формируем SQL запрос для создания новой таблицы
create_table_sql = f"""
CREATE TABLE "combined_inventory" (
    {', '.join([f'"{col}" TEXT' if col in inventory_columns else
                                       f'"{col}" INTEGER DEFAULT 0' for col in combined_columns])}
)
"""

# Выполняем SQL запрос для создания таблицы
cursor.execute(create_table_sql)
conn.commit()

# Закрываем соединение
conn.close()
