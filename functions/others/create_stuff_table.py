import sqlite3
from config import  database_path
# Подключение к базе данных
conn = sqlite3.connect(database_path)
cursor = conn.cursor()

# Функция для вставки данных из другой таблицы в STUFF
def insert_data_into_stuff(table_name, from_table_name):
    # Извлекаем данные из указанной таблицы
    cursor.execute(f"SELECT from_id,название,  стоимость,TYPE FROM {table_name}")
    rows = cursor.fetchall()

    # Подготавливаем данные для вставки в таблицу STUFF
    for row in rows:
        from_id, name_, cost_value,type_ = row
        cursor.execute("""
            INSERT INTO STUFF (from_id, FROM_TABLE,название, COST, TYPE)
            VALUES (?,  ?,?, ?, ?)
        """, (from_id, from_table_name,name_,  cost_value, type_))

    # Сохраняем изменения
    conn.commit()
    print(f"Данные из таблицы {table_name} успешно добавлены в STUFF.")

# Вставляем данные из таблицы Постройки
insert_data_into_stuff('Постройки', 'Постройки')

# Вставляем данные из таблицы STORE
insert_data_into_stuff('STORE', 'STORE')

# Закрываем соединение с базой данных
conn.close()