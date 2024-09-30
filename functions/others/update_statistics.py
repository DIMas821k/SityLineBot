import sqlite3
from config import  database_path

# Подключение к базе данных SQLite
conn = sqlite3.connect(database_path)  # Замените 'database.db' на имя вашей базы данных
cursor = conn.cursor()

# Функция для пересчета статистики
def recalculate_statistics(user_id):
    # Инициализация статистики
    total_statistics = {
        "работяги": 0,
        "энергия": 0,
        "жители": 0,
        "вода": 0,
        "дороги": 0,
        "Прибыль": 0,
        "Производимый_мусор": 0,
        "exp": 0
    }

    # Получаем все постройки с их характеристиками
    cursor.execute("SELECT название, работяги, энергия, жители, вода, дороги, Прибыль, Производимый_мусор, exp FROM Постройки")
    buildings_stats = cursor.fetchall()

    # Получаем названия колонок таблицы buildings
    cursor.execute("PRAGMA table_info(buildings)")
    buildings_columns = [column[1] for column in cursor.fetchall()]

    # Получаем количество зданий у пользователя
    cursor.execute(f"SELECT * FROM buildings WHERE id = ?", (user_id,))
    user_buildings = cursor.fetchone()

    if user_buildings is None:
        print(f"Для пользователя с id {user_id} нет данных по зданиям.")
        return

    # Соответствие названий зданий из таблицы Постройки и полей таблицы buildings
    building_name_to_column = {
        "Простой дом🏠": "Простой_дом🏠",
        "Кирпичный дом🏡": "Кирпичный_дом🏡",
        "Малый завод🏭": "Малый_завод🏭",
        "Магазин🏪": "Магазин🏪",
        "Космодром": "Космодром",
        "Электростанция": "Электростанция",
        "Водозабор": "Водозабор",
        "Водоочистная станция": "Водоочистная_станция",
        "Гидрологическая станция": "Гидрологическая_станция",
        "Мега водозабор": "Мега_водозабор",
        # Добавьте другие названия зданий, как необходимо
    }

    # Пробегаем по всем зданиям и пересчитываем статистику
    for building in buildings_stats:
        name, работяги, энергия, жители, вода, дороги, Прибыль, Производимый_мусор, exp = building
        building_column = building_name_to_column.get(name)

        if building_column and building_column in buildings_columns:
            # Получаем индекс соответствующего здания в результатах SELECT
            count_index = buildings_columns.index(building_column)
            count = user_buildings[count_index]

            # Обновляем общую статистику, учитывая количество зданий
            total_statistics["работяги"] += работяги * count
            total_statistics["энергия"] += энергия * count
            total_statistics["жители"] += жители * count
            total_statistics["вода"] += вода * count
            total_statistics["дороги"] += дороги * count
            total_statistics["Прибыль"] += Прибыль * count
            total_statistics["Производимый_мусор"] += Производимый_мусор * count
            total_statistics["exp"] += exp * count

    # Обновляем таблицу statistic
    cursor.execute("""
        UPDATE statistic 
        SET работяги = ?, энергия = ?, жители = ?, вода = ?, дороги = ?, Прибыль = ?, Производимый_мусор = ?, exp = ?
        WHERE id = ?
    """, (
        total_statistics["работяги"],
        total_statistics["энергия"],
        total_statistics["жители"],
        total_statistics["вода"],
        total_statistics["дороги"],
        total_statistics["Прибыль"],
        total_statistics["Производимый_мусор"],
        total_statistics["exp"],
        user_id
    ))

    conn.commit()

# Пример пересчета статистики для пользователя с id = 1
recalculate_statistics(1765556370)

# Закрытие соединения с базой данных
conn.close()
