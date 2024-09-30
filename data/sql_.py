import sqlite3 as sq
from multipledispatch import dispatch
import pandas as pd
from loader import *
from typing import List
from config import  database_path


def connect_sql() -> [sq.Connection, sq.Connection.cursor]:
    conection = sq.connect(database_path)
    if not conection:
        conection.close()
        return False

    cur = conection.cursor()
    return conection, cur


def check_column_exist(conn, table_name, column_name):
    cursor = conn.cursor()
    sql_query = f"""SELECT name FROM PRAGMA_TABLE_INFO('{table_name}') WHERE name = '{column_name}';"""
    return len(cursor.execute(sql_query).fetchall()) > 0


def add_column(table_name, column_name, column_type, conn=None):
    with (conn or connect_sql()) as conn:
        cursor = conn.cursor()
        query = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
        cursor.execute(query)
        conn.commit()


@dispatch(object, object, list)
def fetch_data(conn, table_name):
    cursor = conn.cursor()
    query = f"SELECT * FROM {table_name}"
    cursor.execute(query)
    rows = cursor.fetchall()
    return rows


def fetch_data_id(table_name, id, conn=None):
    if conn is None:
        conn, cursor = connect_sql()
    else:
        cursor = conn.cursor()

    query = f"SELECT * FROM {table_name} WHERE id = {id}"

    cursor.execute(query)
    rows = cursor.fetchall()
    return rows


def fetch_data_by_name(table_name, column_name, data):
    conn, cursor = connect_sql()
    query = f"SELECT * FROM {table_name} WHERE {column_name} = {data}"

    cursor.execute(query)
    rows = cursor.fetchall()
    return rows
def drop_triggers(connection, trigger_names: List[str]):
    cursor = connection.cursor()

    for trigger_name in trigger_names:
        drop_trigger_sql = f"DROP TRIGGER IF EXISTS {trigger_name};"
        cursor.execute(drop_trigger_sql)

    connection.commit()
    #print(f"Триггеры {', '.join(trigger_names)} успешно удалены.")


def create_update_triggers(connection, combined_table: str, inventory_table: str, buildings_table: str,
                           combined_columns: List[str], inventory_columns: List[str], buildings_columns: List[str]):
    cursor = connection.cursor()

    # Генерация триггера для обновления таблицы inventory
    inventory_trigger_sql = f"""
    CREATE TRIGGER IF NOT EXISTS update_inventory_from_combined
    AFTER UPDATE ON {combined_table}
    FOR EACH ROW
    BEGIN
        UPDATE {inventory_table}
        SET
    """

    # Добавляем колонки из inventory
    inventory_updates = []
    for col in inventory_columns:
        if col != 'id':  # id не нужно обновлять
            inventory_updates.append(f"{col} = NEW.{col}")

    inventory_trigger_sql += ",\n".join(inventory_updates)
    inventory_trigger_sql += f"\nWHERE id = NEW.id;\nEND;"

    # Выполняем SQL для создания триггера
    cursor.execute(inventory_trigger_sql)

    # Генерация триггера для обновления таблицы buildings
    buildings_trigger_sql = f"""
    CREATE TRIGGER IF NOT EXISTS update_buildings_from_combined
    AFTER UPDATE ON {combined_table}
    FOR EACH ROW
    BEGIN
        UPDATE {buildings_table}
        SET
    """

    # Добавляем колонки из buildings
    buildings_updates = []
    for col in buildings_columns:
        if col != 'id':  # id не нужно обновлять
            buildings_updates.append(f"{col} = NEW.{col}")

    buildings_trigger_sql += ",\n".join(buildings_updates)
    buildings_trigger_sql += f"\nWHERE id = NEW.id;\nEND;"

    # Выполняем SQL для создания триггера
    cursor.execute(buildings_trigger_sql)

    connection.commit()
    #print("Триггеры успешно созданы/обновлены.")
def update_triggers_on_structure_change(connection, combined_table: str, inventory_table: str, buildings_table: str):
    cursor = connection.cursor()

    # Получаем текущие колонки из таблиц
    cursor.execute(f"PRAGMA table_info({combined_table});")
    combined_columns = [row[1] for row in cursor.fetchall()]

    cursor.execute(f"PRAGMA table_info({inventory_table});")
    inventory_columns = [row[1] for row in cursor.fetchall()]

    cursor.execute(f"PRAGMA table_info({buildings_table});")
    buildings_columns = [row[1] for row in cursor.fetchall()]

    # Удаление старых триггеров перед созданием новых
    drop_triggers(connection, ['update_inventory_from_combined', 'update_buildings_from_combined'])

    # Создание новых триггеров с учётом изменений в структуре таблиц
    create_update_triggers(connection, combined_table, inventory_table, buildings_table, combined_columns, inventory_columns, buildings_columns)

    #print("Триггеры обновлены с учётом изменений структуры таблиц.")

def sql_fetch_column_name(table_name, conn=None):
    if conn is None:
        conn, cursor = connect_sql()
    else:
        cursor = conn.cursor()

    types_columns = f"""SELECT name FROM PRAGMA_TABLE_INFO('{table_name}');"""
    result = cursor.execute(types_columns).fetchall()
    return result


def fetch_column_name(table_name: str) -> list:
    raw = sql_fetch_column_name(table_name)
    result = [x[0] for x in raw]
    return result

# хорошая функция, не сокр.
def update_record(table_name, column_name, new_value, identifier_column, identifier_value, conn=None):
    if conn is None:

        conn, cursor = connect_sql()
    else:
        cursor = conn.cursor()
    # print(column_name)
    if type(column_name) is list:
        column_name = ", ".join(f"{x} = ?" for x in column_name)  # задаем формат для каждого столбца
        new_values = [str(x) for x in new_value]  # предполагая, что new_value также должен быть списком
        # print(new_values)
        # print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        query = f"UPDATE {table_name} SET {column_name} WHERE {identifier_column} = {identifier_value}"
        print(column_name)
        # print(len(new_values))
        # print(len(column_name))
        # print("New_values", new_values)
        # print("query", query)
        # Теперь выполняем запрос с параметрами
        cursor.execute(query, new_values)  # добавляем идентификатор в значения
    else:

        query = f'UPDATE {table_name} SET {column_name} = "{new_value}" WHERE {identifier_column} = {identifier_value}'
        print(query)
        cursor.execute(query)
    conn.commit()
    conn.close()


def insert_row(table_name, columns, values):
    """
    Функция для добавления новой строки в таблицу.


    :param table_name: Имя таблицы.
    :param columns: Список колонок, в которые будут добавлены значения.
    :param values: Список значений, которые будут добавлены в соответствующие колонки.
    """
    # Преобразование списка колонок в строку
    #print(f"Inserting")
    #print(table_name)
    #print(columns)
    #print(values)
    if type(columns) is list:
        columns_str = ', '.join(columns)

        # Создание плейсхолдеров для значений (например, (?, ?, ?))
        placeholders = ', '.join('?' * len(values))
    else:
        placeholders = "?"
        columns_str = columns
    # SQL-запрос для вставки данных
    sql_query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
    print(sql_query)
    try:
        # Подключение к базе данных
        conn, cursor = connect_sql()

        # Выполнение запроса
        cursor.execute(sql_query, values)

        # Сохранение изменений
        conn.commit()

        #("Строка успешно добавлена!")

    except sq.Error as e:
        print(f"Ошибка при добавлении данных: {e}")

    finally:
        # Закрытие соединения с базой данных
        if conn:
            conn.close()


@dispatch(object, object, list)
def select_table_by_id(id, table, select):
    try:
        conn, cur = connect_sql()
    except sq.Error as err:
        return "error"

    #print("Подключен к SQlite")
    sql_select_query = f'SELECT {",".join(select)} FROM {table} WHERE id == "{id}"'
    cur.execute(sql_select_query)
    conn.close()
    return cur.fetchall()


@dispatch(object, object, str)
def select_table_id(id, table, select, id_name):
    global conn
    try:
        conn, cur = connect_sql()
        if not conn:
            return "error"
        #print("Подключен к SQlite")
        sql_select_query = f'SELECT {select} FROM {table} WHERE {id_name} == "{id}"'
        cur.execute(sql_select_query)
        return cur.fetchall()

    except sq.Error as error:

        pass
        #print("Ошибка при работе с SQLite", error)
    finally:
        if conn:
            conn.close()
            #print("Соединение с SQLite закрыто")


@dispatch(object, object, list)
def select_table(column_name, table, select, id_name="id", ):
    global conn
    try:
        conn, cur = connect_sql()
        if not conn:
            return "error"
        #print("Подключен к SQlite")
        sql_select_query = f'SELECT {",".join(select)} FROM {table} WHERE {id_name} == "{column_name}"'
        cur.execute(sql_select_query)
        return cur.fetchall()

    except sq.Error as error:
        pass
        #print("Ошибка при работе с SQLite", error)
    finally:
        if conn:
            conn.close()
            #print("Соединение с SQLite закрыто")


@dispatch(object, object, str)
def select_table(id, table, select, id_name="id", ):
    global conn
    try:
        conn, cur = connect_sql()
        if not conn:
            return "error"
        #print("Подключен к SQlite")
        sql_select_query = f'SELECT {select} FROM {table} WHERE {id_name} == "{id}"'
        cur.execute(sql_select_query)
        return cur.fetchall()

    except sq.Error as error:
        pass
        #print("Ошибка при работе с SQLite", error)
    finally:
        if conn:
            conn.close()
            #print("Соединение с SQLite закрыто")


def select_Data_dict(id, table_name, select, id_name="id"):
    conn, cur = connect_sql()
    if type(select) is list:
        select = ','.join(select)
    conn.row_factory = sq.Row
    cursor = conn.cursor()
    cursor.execute(f"SELECT {select} FROM {table_name} WHERE {id_name} = {id}")
    row = cursor.fetchone()
    if row:
        result = {key: row[key] for key in row.keys()}
        #print(result)
        return result
    else:
        print("No data found.")
        return None


def pd_data_fetch(id: object, table_name: str, select: object = "*", id_name: str = "id") -> [list, list]:
    """
    query = f"SELECT {select} FROM {table_name} WHERE {id_name} = {id}"
    """
    conn, cur = connect_sql()
    query = f"SELECT {select} FROM {table_name} WHERE {id_name} = {id}"
    df = pd.read_sql_query(query, conn)
    return list(df.values[0]), list(df.columns)
