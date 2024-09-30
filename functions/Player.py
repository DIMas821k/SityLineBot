from typing import Dict
from typing import Any
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from data.sql_ import *
from datetime import datetime
import asyncio
from aiogram.types import Message, CallbackQuery
import pandas as pd
import math
from config import  database_path



def update_build_name():
    conn, cur = connect_sql()
    if conn:
        query = "SELECT * FROM Постройки"

        conn.commit()
    conn.close()


class Player:
    profile: dict[str, Any]

    def __init__(self, id_Player: int):

        self.id = id_Player
        # self.money = 50000
        self.last_des = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.environments = dict()
        self.statistic = dict()
        self.inventory = dict()
        self.own_builds = dict()
        self.db_path = database_path
        self.level = 1
        self.exp = 0
        self.effects = dict()
        self.profile = dict()
        self.profile["happines"] = 100
        self.data_registration = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # self.exp_next = 0
    def upload_full_name(self, full_name: str) -> None:
        """
        Sets the name of the player
        @param full_name: string
        @return: None
        """
        self.profile["FULL_NAME"] = full_name

    def reg_player(self, table_name):
        connection = sqlite3.connect(self.db_path)
        columns = [col[0] for col in sql_fetch_column_name(table_name, connection)]
        datas = [self.id]
        for i in range(len(columns) - 1):
            datas.append(None)
        insert_row(table_name, columns, datas)

    def get_profile_data(self, data: str) -> Any:
        """
        may return:
        "last_des": str,
        Money: int,
        happines: int,
        data_registration": str,
        FULL_NAME": str,"
        LEVEL:int,
        EXP": int,"
        EXP_NEXT": int,"
        EFFECTS": dict,"

        """
        return self.profile[data]

    def _effects(self):
        self.effects = {}

    def load_profile(self):
        try:
            values, columns = pd_data_fetch(select="*", table_name="Players", id_name="id", id=self.id)
            print("load_profile")
            for i in range(1, len(columns)):
                print(columns[i], values[i])
                self.profile[columns[i]] = values[i]

            # self.exp_next = self.profile["EXP_NEXT"]

            self.level = self.profile["LEVEL"]
            # self.full_name = self.profile["FULL_NAME"]

        except Exception:
            self.reg_player("Players")
            self.profile["data_registration"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.profile["EXP"] = 0
            self.profile["EXP_NEXT"] = 0
            self.profile["happines"] = 0
            self.profile["FULL_NAME"] = ""
            self.profile["Money"] = 50000
            self.profile["LEVEL"] = 1
            self.profile["data_registration"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.profile["last_des"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.profile["EFFECTS"] = ""
        self.data_registration = self.profile["data_registration"]
        self.last_des = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        pass

    def upload_profile(self) -> None:
        """

        @rtype: None
        """
        # self.profile["EXP_NEXT"] = self.exp_next
        self.profile["data_registration"] = self.data_registration
        self.profile["last_des"] = self.last_des
        print("upload_profile")
        update_record("PLayers", list(self.profile.keys()), list(self.profile.values()), "id", self.id)
        pass

    def calculate_happiness(self) -> Any:
        """
        Calculates the player's happiness level based on their statistics.

        @return:str or int
        """
        from_level = {"вода": 3, "энергия": 3, "Производимый_мусор": 4}
        # Определим требуемые значения для каждого параметра
        required_values = {}
        for key in from_level:
            if from_level[key] <= self.get_profile_data("LEVEL"):
                required_values[key] = 100 * math.exp(self.get_profile_data("LEVEL") // 10)

        required_values = {
            "вода": 100 * math.exp(self.get_profile_data("LEVEL") // 10),
            "энергия": 1000 * math.exp(self.get_profile_data("LEVEL") // 10),
            "Производимый_мусор": 500 * math.exp(self.get_profile_data("LEVEL") // 10)
            # Например, 500 единиц мусора — оптимум
        }

        happiness = 0

        for param, required_value in required_values.items():
            # Рассчитаем разницу между текущим количеством и требуемым значением
            difference = int(self.statistic[param]) / required_value * 10
            difference = round(difference)

            # Ограничим значение счастья для каждого параметра в пределах от -10 до 10
            param_happiness = max(-10, min(difference, 100 // len(required_values)))

            # Суммируем результат для общего показателя счастья
            happiness += param_happiness
            if happiness > 100:
                happiness = 100

        # Устанавливаем значение счастья
        self.profile["happines"] = happiness

        return self.profile["happines"]

    def register_player(self, types_columns, name_table: str):
        """

        @type name_table: str
        @param types_columns:
        @param name_table:
        @return:
        """
        print("register_player")
        new_datas = [self.id]
        n = len(types_columns)
        for i in range(1, n):
            new_datas.append(None)
            current_dict = getattr(self, name_table, {})
            current_dict[types_columns[i]] = 0

            setattr(self, name_table, current_dict)
        insert_row(name_table, types_columns, new_datas)

    def experience_to_next_level(self) -> int:
        """
        Функция для вычисления, сколько опыта осталось до нового уровня с экспоненциальной зависимостью.
        :return: Оставшийся опыт до нового уровня
        @return:
        """
        # Формула для опыта: базовый опыт 1000, увеличивается в 1.5 раза с каждым уровнем
        next_level_exp = int(1000 * (1.5 ** (self.get_profile_data("LEVEL") - 1)))

        # Вычисляем, сколько опыта осталось до следующего уровня
        return max(0, next_level_exp - self.get_profile_data("EXP"))

    def calculate_new_level(self) -> int:
        """
        Функция для вычисления нового уровня игрока с учетом прироста опыта.


        :return: Возвращает цифру, на сколько уровень повысился
        """
        # Текущий уровень и опыт игрока
        last_level = self.profile['LEVEL']

        # Продолжаем повышать уровень, пока опыта хватает
        while True:
            # Вычисляем опыт до следующего уровня
            remaining_exp = self.experience_to_next_level()

            # Если опыта не хватает на новый уровень, выходим из цикла
            if self.get_profile_data("EXP") < remaining_exp:
                break
            earned_money = last_level * 100
            # Если игрок может перейти на новый уровень
            self.profile["Money"] += earned_money  # Добавляем деньги, полученные за переход уровня
            self.profile["EXP"] -= remaining_exp  # Убираем опыт, потраченный на переход уровня
            self.level_up()  # Увеличиваем уровень
        self.profile["EXP_NEXT"] = remaining_exp
        self.statistic['exp'] = self.profile["EXP"]
        return self.get_profile_data("LEVEL") - last_level

    def get_builds(self) -> dict:
        return self.own_builds

    def _load_builds(self):
        """
        Скрытая функция загрузки строений из БД
        В случае отсутствия строений в БД, регестрирует игрока в БД
        @return:
        """
        try:
            values: list
            columns: list
            values, columns = pd_data_fetch(select="*", table_name="OWN_BUILDS", id_name="ID", id=self.id)
            print(values[1])
            if len(values[1]) > 0:
                builds = values[1].split(";")
                print(builds)
                if len(builds) > 0:
                    for i in builds:
                        name, count = i.split(":")
                        self.own_builds[name] = int(count)
        except Exception as e:
            self.reg_player("OWN_BUILDS")
        pass

    def upload_builds(self):
        """
        Создает строку формата название:кол-во и загружает в таблицу БД полученную строку
        БД: OWN_BUILDS, column = BUILDS
        @return:
        """
        queue_build = ""
        for name, count in self.own_builds.items():
            queue_build += f"{name}:{count};"
        if len(queue_build) > 0:
            queue_build = queue_build[:-1] if queue_build[-1] == ";" else queue_build
        print(queue_build)
        update_record("OWN_BUILDS", "BUILDS", queue_build, "ID", self.id)
        pass

    def level_up(self):
        """
        Увеличивает уровень игрока на 1
        @return:
        """
        self.profile["LEVEL"] += 1

    def get_profit(self):
        """"""
        effects: dict = self.get_profile_data("EFFECTS")
        # for i in effects:

        pass

    def __load_data__(self, name_table, target_attribute):
        """
        Функция загрузки информации из БД
        В случае отсутствия строений в БД, регестрирует игрока в БД
        """
        # print(f"__load_data from {name_table}")
        types_columns = fetch_column_name(name_table)
        datas_inventory = fetch_data_id(name_table, self.id)

        if not datas_inventory:
            self.register_player(types_columns, name_table)
        else:
            current_dict = getattr(self, target_attribute, {})
            for i in range(1, len(types_columns)):
                data = datas_inventory[0][i] if datas_inventory[0][i] is not None else 0
                current_dict[types_columns[i]] = data
                setattr(self, target_attribute, current_dict)

    def __str__(self) -> str:
        # return f"Player {self.buildings},\n Money: {self.statistic}"
        return f"Player {self.profile['happines']}"

    def load_data(self, db_path: str = r"D:\Database_SQL\Telegram_Bot.db") -> object:
        """
        Отвечает за загрузку всех параметров пользователя, вызывая под_функции
        :rtype: object
        :param db_path:
        """
        print("LOAD_DATA")
        datas = ["environments", "statistic", "inventory"]
        for name_table in datas:
            self.__load_data__(name_table, name_table)

        """self.__load_environments()
        self.__load_buildings()
        self.__load_inventory()
        
        self.__load_statistic()"""
        # self.__load_money_tax_des()
        # print("update_DATA")

        # self.load_combined_inventory()
        self._load_builds()
        self.load_profile()
        self.calculate_happiness()
        self.__update_des()
        self.profile["EXP_NEXT"] = self.experience_to_next_level()
        self.update_money_by_time()
        return self

    def upload_data(self) -> None:
        """
        Отвечает за выгрузку параметров в таблицы statistics, environments, inventory
        """
        print("upload_data")
        print("-------------------------------------")
        tables = ["statistic", "environments", "inventory"]

        for table in tables:
            columns: list = fetch_column_name(table)[1:]
            print(table)
            # dat = eval(f"self.{table}.keys()")
            dat = getattr(self, table)
            t = dat.values()
            # data = ",".join(str(x) for x in t)
            # print(data)
            # print("Uploading " + table)
            update_record(table, columns, t, "id", self.id)

        print("Uploaded")

        self.upload_profile()
        self.upload_builds()

    def cond_buy(self, cost: int) -> bool:
        """
        На вход подается стоимость строения. возвращает True, если игроку хватает денег на покупку, иначе False.

        @param: cost:int
        @return:bool
        """
        print("cond_buy")
        print(self.profile["Money"])
        if self.profile["Money"] < cost:
            return False
        else:
            return True

    def update_statistic(self, name_build) -> None:
        """

        @param name_build:
        @return:
        """
        print("update_statistic")
        name_build = name_build.replace(" ", "_")
        # Подключение к базе данных
        conn = sqlite3.connect('./database/Telegram_Bot.db')

        # Используем pandas для получения данных из таблицы Постройки
        query = f"SELECT * FROM Постройки WHERE название = '{name_build}'"
        # print(query)
        df = pd.read_sql_query(query, conn)

        # Закрываем соединение с базой данных
        conn.close()

        # Проверяем, есть ли данные
        if not df.empty:
            # Извлекаем данные начиная с 5-го столбца (индекс 4)
            relevant_data = df.iloc[0, 4:]  # Получаем данные начиная с 5-го элемента
            # print("relevant data", relevant_data)
            # Обновляем self.statistic
            for column in relevant_data.index:
                if column == "ACCESSES_FROM":
                    break
                #  Если ключ уже есть, складываем значения
                # print(column)
                if column in self.statistic:
                    # print("self.statistic[column]", self.statistic[column], type(self.statistic[column]))
                    self.statistic[column] += int(relevant_data[column])
                else:
                    # Иначе добавляем новый ключ и значение
                    self.statistic[column] = int(relevant_data[column])

    def buy(self, name: str, cost: int, id=0, effects=None) -> [bool, str]:
        # print()
        print(f"Купить предмет, cost = {cost}, name = {name}")
        # name.replace(" ", "_")
        values, column = pd_data_fetch(f"'{name}'", "STUFF", "FROM_TABLE, TYPE", "название")
        if self.cond_buy(cost):
            if values[0] == "STORE":
                if self.inventory[values[1]] == name:
                    return False, "У вас уже стоит такой предмет"

                self.inventory[values[1]] = name
                if name not in self.inventory["SUMMARY"].split(";"):
                    self.profile["Money"] -= cost
                    self.inventory["SUMMARY"] += name + ";"
            elif values[0] == "Постройки":
                self.build(name)
                self.update_statistic(name)
                self.profile["Money"] -= cost
            return True, "Успешная покупка"
        print("the build isn't available")
        return False, "Недостаточно денег"

    def buy_build(self, name_build: str, cost: int, exp: int) -> bool:
        print()
        # print(f"buy_build, cost = {cost}, name_build = {name_build}")
        name_build.replace(" ", "_")
        if self.cond_buy(cost):
            keys = self.own_builds.keys()
            if name_build in keys:
                count = self.own_builds[name_build]

                self.own_builds[name_build] = count + 1
                # print("УСПЕШНО куплено здание", name_build)
            else:
                self.own_builds[name_build] = 1
                # print(name_build, "= 1")

            # print(f"difference = self.money{self.money - cost}")
            self.profile["Money"] -= cost
            self.profile["EXP"] += exp
            self.update_statistic(name_build)
            print("здание куплено")

            return True
        else:
            print('the build isn\'t available')
            return False

    def update_money(self, money: int) -> None:
        self.profile["Money"] = money

    def get_inventory(self) -> dict:
        return self.inventory
        pass

    def update_money_by_time(self):
        """
        Функция отвечает за вычисление заработанных денег за прошедшее время
        @return:
        """
        print("update_money")
        diff = self.diff_time()
        diff = min(diff, 36000)
        print(diff)
        self.profile["Money"] += diff * self.statistic["Прибыль"] // 60
        if self.get_profile_data("Money") < 0:
            self.set_profile_data("Money", 0)
        # print("self_money", self.money)

    def update_tax(self, tax):
        self.tax = tax
        pass

    def set_profile_data(self, name: str, value: Any) -> None:
        self.profile[name] = value
        pass

    def build(self, name: str) -> None:
        """
        Отвечает за строительство здания, увеличения кол-ва на 1
        @param name:
        @return:
        """
        if name in self.own_builds:
            self.own_builds[name] += 1
        else:
            self.own_builds[name] = 1

    # новая функция(18/09), мб будет ломаться
    def return_buildings(self) -> str:
        """
        Возвращает форматированную строку с описанием всех зданий в городе
        @return:
        """
        # Получаем сумму всех значений в словаре
        cnt_b = f"в Вашем городе {sum(self.own_builds.values())} зданий:\n"
        # Формируем строку из словаря, исключая пары со значением 0
        str_buildings = '\n'.join(
            f"{key.replace('_', ' ')} - {value}" for key, value in self.own_builds.items()
            if isinstance(value, int) and value != 0)
        return cnt_b + str_buildings

    def __update_des(self):
        """
        Обновляет дату последнего изменения игрового состояния
        @return:
        """
        print("update_des")
        self.last_des = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def diff_time(self):
        """
        вычисляет разницу в секундах между текущим временем и датой последнего изменения игрового состояния
        @return:
        """
        print("diff_time")
        # Если self.last_des это строка, сначала конвертируем её обратно в объект datetime
        if isinstance(self.last_des, str):
            last_des_datetime = datetime.strptime(self.last_des, "%Y-%m-%d %H:%M:%S")
        else:
            last_des_datetime = self.last_des

        return int((datetime.now() - last_des_datetime).total_seconds())

    def get_money(self):
        """
        Возващает текущее значение денег игрока
        @return:
        """
        # print(self.money)
        return self.profile["Money"]

    def update_des(self) -> int:
        """
        Обновляет дату последного действия игрового состояния
        @return: int difference in seconds
        """

        diff = self.diff_time()
        self.__update_des()
        # print("Decision")
        return diff

    async def check_time(self, sleep_time=60 * 5, time=60 * 60):
        if self.diff_time() >= time:
            return False
        else:
            await asyncio.sleep(time)
            await self.check_time()


class Players:
    players: dict[int, Player]

    def get_online(self) -> int:
        """
        Возвращает количество игроков в онлайне
        @return:
        """
        return len(self.players)

    def __init__(self):
        self.players = dict()
        pass

    def remove_players(self):
        """
        Функция удаляет игроков из списка онлайн
        @return:
        """
        print("remove_players")
        players_id_to_remove: list[int] = list(self.players.keys())
        for player_id in players_id_to_remove:
            # print("remove")
            self.get_players(player_id).upload_data()
            self.remove_player(player_id)

    async def add_player(self, player):
        """
        добавляет игрока в список онлайн
        @param player:
        @return:
        """
        k = Player(player)
        k.load_data()
        self.players[player] = k

        await self.time_check(player)
        # print("add player")
        # print(self.players)
        # print("1")

    def get_players(self, element: int) -> Player:
        """
        Возвращает игрока по его id из списка онлайн
        @param element:
        @return:
        """
        return self.players[element]

    def check_player(self, id: int) -> bool:
        """
        Проверяет наличие игрока в списке онлайн по его id
        @param id:
        @return:
        """
        # ("check_player")
        if id not in self.players:
            return False
        return True

    async def rem_player(self, id):
        """
        Удаляет игрока из списка онлайн по его id
        @param id:
        @return:
        """
        # print("-------------------------------------------------\nrem_player", id)
        self.get_players(id).upload_data()
        self.remove_player(id)

    def remove_player(self, id: int) -> None:

        self.players.pop(id)
        # print("remove player")

    async def loop_checker(self, player):
        k = True
        while k:
            k = await player.check_time()
        if not k:
            player.upload_data()
            self.remove_player(player.id)
            # print("remove player")

    async def time_check(self, user_id: int):
        """

        :type user_id: object
        """
        # print("time_check")
        player = self.get_players(user_id)
        asyncio.create_task(self.loop_checker(player))
        pass


import sqlite3

online_players = Players()


class LastActionMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        if isinstance(event, Message):
            user_id = event.from_user.id
            if online_players.check_player(event.from_user.id):
                # print(1)
                online_players.players[user_id].update_money_by_time()
            else:
                await online_players.add_player(user_id)
                online_players.get_players(user_id).upload_full_name(event.from_user.full_name)

                # ("add player")
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
            if online_players.check_player(event.from_user.id):
                # print(1)

                online_players.players[user_id].update_money_by_time()
            else:
                await online_players.add_player(user_id)
                online_players.get_players(user_id).upload_full_name(event.from_user.full_name)
        # print("worked")
        # print(f"Middleware: event = {event}, data = {data}")
        return await handler(event, data)
