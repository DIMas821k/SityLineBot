import sqlite3
from config import  database_path
# Подключение к базе данных SQLite
conn = sqlite3.connect(database_path)
cursor = conn.cursor()

# Извлечение всех данных из таблицы "buildings"
cursor.execute('SELECT * FROM buildings')
buildings_data = cursor.fetchall()

# Получение списка названий столбцов, кроме id
columns = [description[0] for description in cursor.description if description[0] != 'id']

# Цикл по каждому пользователю в таблице "buildings"
for row in buildings_data:
    user_id = row[0]  # ID пользователя
    builds = row[1:]  # Данные о постройках

    # Формирование строки в формате "название_здание:кол-во"
    builds_string = ';'.join([f"{columns[i]}:{builds[i]}" for i in range(len(builds)) if builds[i] > 0])

    # Вставка данных в таблицу "OWN_BUILDS"
    cursor.execute(
        'INSERT OR REPLACE INTO OWN_BUILDS (ID, BUILDS) VALUES (?, ?)',
        (user_id, builds_string)
    )

# Сохранение изменений и закрытие соединения
conn.commit()
conn.close()