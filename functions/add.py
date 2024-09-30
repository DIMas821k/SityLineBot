from .imports import *
import sqlite3 as sq
import aiosqlite
from config import  database_path


class BuildingForm(StatesGroup):
    name = State()
    price = State()
    from_type = State()
    from_id = State()
    workers = State()
    citizen = State()
    roads = State()
    profit = State()
    trash = State()
    energy = State()
    water = State()




# Функция для сохранения данных здания в таблицу SQLite
async def save_building(table_name: str, name: str, price: int, from_type: str, from_id: int, workers: int,
                        energy: int, citizen: int, water: int, roads: int, profit: int, trash: int):
    async with aiosqlite.connect(database_path) as db:
        await db.execute(f"""
            INSERT INTO "{table_name}" (название, стоимость, откуда_тип, from_id, работяги, энергия, жители, вода, дороги,
             Прибыль, Производимый_мусор, INFO,TYPE)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?)
        """, (name, price, from_type, from_id, workers, energy, citizen, water, roads, profit, trash, "Обычное", None))
        await db.commit()


async def add_column(table_name: str, column_name: str):
    pass


@dp.callback_query(F.data == "create_build")
async def create_building_(message: Message, state: FSMContext):
    print("create_building_")
    await message.answer("Введите название здания:")
    await state.set_state(BuildingForm.name)


# Получаем название здания
@dp.message(BuildingForm.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите цену здания:")
    await state.set_state(BuildingForm.price)


# Получаем цену здания
@dp.message(BuildingForm.price)
async def process_price(message: Message, state: FSMContext):
    try:
        price = int(message.text)
        await state.update_data(price=price)
        await message.answer("Введите количество энергии для здания:")
        await state.set_state(BuildingForm.energy)
    except ValueError:
        await message.answer("Цена должна быть числом. Введите цену снова:")


# Получаем количество энергии
@dp.message(BuildingForm.energy)
async def process_energy(message: Message, state: FSMContext):
    try:
        energy = int(message.text)
        await state.update_data(energy=energy)

        await message.answer("Введите количество воды для здания:", )
        await state.set_state(BuildingForm.water)
    except ValueError:
        await message.answer("Энергия должна быть числом. Введите энергию снова:")


# Получаем количество воды и сохраняем данные
@dp.message(BuildingForm.water)
async def process_water(message: Message, state: FSMContext):
    try:
        water = int(message.text)
        await state.update_data(water=water)
        button1 = KeyboardButton(text="Правительственные здания")
        button2 = KeyboardButton(text="Жилые здания")
        button3 = KeyboardButton(text="Рабочие места")
        button4 = KeyboardButton(text="Электричество")
        button5 = KeyboardButton(text="Добыча воды")
        button6 = KeyboardButton(text="Общественный транспорт")
        button7 = KeyboardButton(text="Образование")
        markup5 = ReplyKeyboardMarkup(keyboard=[[button1, button2, button3], [button4, button5,button6],[button7]], resize_keyboard=True)

        await message.answer("Введите тип источника (например: город, фабрика):", reply_markup=markup5)

        await state.set_state(BuildingForm.from_type)
    except ValueError:
        await message.answer("Количество воды должно быть числом. Введите количество воды снова:")


# Получаем тип источника (from_type)
@dp.message(BuildingForm.from_type)
async def process_from_type(message: Message, state: FSMContext):
    await state.update_data(from_type=message.text)
    await message.answer("Введите ID источника:",reply_markup=None)
    await state.set_state(BuildingForm.from_id)
    await process_from_id(message, state)

# Получаем ID источника (from_id)
async def process_from_id(message: Message, state: FSMContext):
    from_id_dict = {"Правительственные здания": 18, "Жилые здания": 19, "Рабочие места": 20, "Электричество": 21,
                    "Добыча воды": 22, }
    try:
        from_id = from_id_dict[message.text]
        await state.update_data(from_id=from_id)
        await message.answer("Введите количество работников:")
        await state.set_state(BuildingForm.workers)
    except ValueError:
        await message.answer("ID источника должно быть числом. Введите ID снова:")


# Получаем количество работников
@dp.message(BuildingForm.workers)
async def process_workers(message: Message, state: FSMContext):
    try:
        workers = int(message.text)
        await state.update_data(workers=workers)
        await message.answer("Введите количество жителей:")
        await state.set_state(BuildingForm.citizen)
    except ValueError:
        await message.answer("Количество работников должно быть числом. Введите количество снова:")


# Получаем количество жителей
@dp.message(BuildingForm.citizen)
async def process_citizen(message: Message, state: FSMContext):
    try:
        citizen = int(message.text)
        await state.update_data(citizen=citizen)
        await message.answer("Введите состояние дорог (например: хорошее, среднее, плохое):")
        await state.set_state(BuildingForm.roads)
    except ValueError:
        await message.answer("Количество жителей должно быть числом. Введите количество снова:")


# Получаем состояние дорог
@dp.message(BuildingForm.roads)
async def process_roads(message: Message, state: FSMContext):
    await state.update_data(roads=message.text)
    await message.answer("Введите прибыль от здания:")
    await state.set_state(BuildingForm.profit)


# Получаем прибыль
@dp.message(BuildingForm.profit)
async def process_profit(message: Message, state: FSMContext):
    try:
        profit = int(message.text)
        await state.update_data(profit=profit)
        await message.answer("Введите количество производимого мусора:")
        await state.set_state(BuildingForm.trash)
    except ValueError:
        await message.answer("Прибыль должна быть числом. Введите прибыль снова:")


@dp.message(BuildingForm.trash)
async def process_trash(message: Message, state: FSMContext):
    try:
        trash = int(message.text)
        await state.update_data(trash=trash)

        # Собираем все данные и выводим пользователю
        user_data = await state.get_data()
        await message.answer(f"Здание успешно создано с данными:\n"
                             f"Название: {user_data['name']}\n"
                             f"Цена: {user_data['price']}\n"
                             f"Энергия: {user_data['energy']}\n"
                             f"Вода: {user_data['water']}\n"
                             f"Тип источника: {user_data['from_type']}\n"
                             f"ID источника: {user_data['from_id']}\n"
                             f"Работники: {user_data['workers']}\n"
                             f"Жители: {user_data['citizen']}\n"
                             f"Дороги: {user_data['roads']}\n"
                             f"Прибыль: {user_data['profit']}\n"
                             f"Мусор: {user_data['trash']}")

        # Создаем таблицу (если не создана) и сохраняем данные
        # await create_table(table_name)
        await save_building("Постройки",
                            user_data["name"],
                            user_data["price"],
                            user_data["from_type"],
                            user_data["from_id"],
                            user_data["workers"],
                            user_data["energy"],
                            user_data["citizen"],
                            user_data["water"],
                            user_data["roads"],
                            user_data["profit"],
                            user_data["trash"])
        await add_column("buildings", user_data["name"])
        await state.clear()

    except ValueError:
        await message.answer("Количество мусора должно быть числом. Введите количество снова:")
