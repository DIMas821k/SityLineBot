from functions.Player import Player, online_players
from loader import *
from data.library import *
from data.sql_ import *
from functions.Importis import *
from functions.TREE_DEC import Tree_Des
from aiogram import html
import math
from aiogram import Router
from config import admins
from aiogram.types import LabeledPrice, Message
router = Router()
dp.include_router(router)



class CreateStuff(StatesGroup):
    datas = State()
    sure = State()


def format_price(price):
    # Убираем 'p' и разделяем на название и число
    number = int(price)

    # Форматируем число с разделением на тысячи
    formatted_number = "{:,.0f}".format(number).replace(",", ".")
    # Добавляем ' р' в конец
    return f"{formatted_number} р"


def add_back(builder: InlineKeyboardBuilder, back_id):
    builder.add(types.InlineKeyboardButton(text="◀️Назад", callback_data="back" + ":" + str(back_id)))


@router.callback_query(F.data == "help")
async def send_random_value(callback: types.CallbackQuery):
    await callback.message.answer("мур")


@router.callback_query(F.data == "Admin_panel")
async def Admin_panel(callback: types.CallbackQuery):
    player_ = online_players.get_players(callback.from_user.id)
    Text = f"Админ панель, \n Текущий онлайн - {online_players.get_online()} игроков "
    builder = InlineKeyboardBuilder().add(types.InlineKeyboardButton(text="удалить игрока",
                                                                     callback_data="discon_player"))
    builder.add(types.InlineKeyboardButton(text="exit_python", callback_data="exit_py"))
    builder.add(types.InlineKeyboardButton(text="create_build", callback_data="create_build"))
    builder.add(types.InlineKeyboardButton(text="Add_money", callback_data="add_money"))
    await callback.message.answer(Text, reply_markup=builder.as_markup())


@router.callback_query(F.data == "add_money")
async def add_money(callback: types.CallbackQuery):
    pass


@router.callback_query(F.data == "exit_py")
async def exit_py(callback: types.CallbackQuery):
    online_players.remove_players()
    sys.exit(0)


@router.callback_query(F.data == "discon_player")
async def del_player(callback: types.CallbackQuery):
    await online_players.rem_player(1777893126)


@router.callback_query(F.data[:4] == "back")
async def back(callback: types.CallbackQuery):
    dat_call = callback.data.split(":")
    back_id = dat_call[1]
    # datas = fetch_data_by_name("actions", "id", dat_call[1])
    # parent_id = datas[0][2]
    # datas = fetch_data_by_name("actions", "parent_id", parent_id)
    name, id_parent = Tree_Des.get_ancestors(back_id).name, Tree_Des.get_parent_id(back_id)
    # datas = fetch_data(name_table, name, id)
    text = ""

    builder = create_inline_keyboard_(id_parent)
    await bot.edit_message_text(text="◀️ " + name + ",\nКуда желаете пойти❔",
                                chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                reply_markup=builder.as_markup()
                                )
    pass


@router.callback_query(F.data == "15")
async def statistik_building(callback: types.CallbackQuery):
    builds_dict = online_players.get_players(callback.from_user.id).get_builds()
    columns, values = list(builds_dict.keys()), list(builds_dict.values())
    text = "\n"
    count = 0
    for col, value in zip(columns, values):  # Пропускаем id в результатах
        if value > 0:
            text += f"{col.replace('_', ' ')} - {value}\n"
            count += value
    text += f"Общее количество: {count}\n"
    builder = InlineKeyboardBuilder()
    add_back(builder, callback.data)
    await bot.edit_message_text(text=f"{callback.from_user.full_name}, " + text,
                                chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                reply_markup=builder.as_markup()
                                )
    pass


def problems_with_city(player: Player):
    list_problems = ["вода", "энергия", ]

    text = ""
    for problem in list_problems:
        if int(player.statistic[problem]) <= 100 * math.exp(player.get_profile_data("LEVEL") // 10):
            text += f"<blockquote>Вам нужно поднять производительность {problem.replace('_', ' ')}, иначе жители не будут довольны.</blockquote>\n"

    if int(player.statistic["Производимый_мусор"]) <= 100 * math.exp(player.get_profile_data("LEVEL") // 10):
        text += (f"<blockquote>Вам нужно поднять производительность Переработки мусора, иначе жители не будут "
                 f"довольны.</blockquote>\n")

    total_citizens = player.statistic["жители"]

    if int(total_citizens) == 0:
        text += "<blockquote>В городе нет жителей, постройте больше домов, чтобы производство могло работать </blockquote>\n"
    else:
        workers = player.statistic["работяги"]
        unemployment_rate = (total_citizens - workers) / total_citizens * 100
        if unemployment_rate < 2:
            text += f"<blockquote>В городе не хватает людей для работы, постройте больше домов, чтобы производство могло работать </blockquote>\n"
        elif unemployment_rate > 5:
            text += (
                f"<blockquote>В городе слишком безработных, процент безработицы - {round(unemployment_rate, 2)} , "
                f"рекомендуется построить"
                f"больше заводов</blockquote>\n")
    return text


@router.callback_query(F.data == "35")
async def profile(callback: types.CallbackQuery):
    player = online_players.get_players(callback.from_user.id)
    money = player.get_money()
    text = f"""{callback.from_user.full_name}, Ваш профиль:\n
    🔎 ID: {callback.from_user.id}\n
    💰 Баланс: {player.get_money()}\n
    Заработок: {player.statistic["Прибыль"]}\n
    Счастье города: {round(player.profile["happines"], 2)}%\n
    Производительность воды: {player.statistic['вода']}\n
    Производительность энергии: {player.statistic['энергия']}\n
    Скорость обработки мусора: {player.statistic['Производимый_мусор']}\n
    Опыт: {player.statistic['exp']}\n
    Уровень: {player.get_profile_data("LEVEL")}\n
    Опыта до следующего уровня: {player.profile['EXP_NEXT']}\n
{problems_with_city(player)}
    """

    builder = InlineKeyboardBuilder().add(types.InlineKeyboardButton(text="Inventory", callback_data="Inventory"))
    builder.add(types.InlineKeyboardButton(text="Обновить", callback_data="35"))
    add_back(builder, 1)

    await bot.edit_message_text(text=text,
                                chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML
                                )
    pass


@router.callback_query(F.data == "create_item")
async def create_item(message: Message, state: FSMContext):
    flag = True
    while flag:
        text = f"Вы хотите добавить в магазин\n Введите данные в формате название:type:цена:доступ_уровень:info"
        await message.answer(text)
        await state.set_state(CreateStuff.datas)
        await state.update_data(datas=message.text)
        datas = await state.get_data()

        button1 = KeyboardButton(text="Да")
        button2 = KeyboardButton(text="Нет")
        markup = ReplyKeyboardMarkup(keyboard=[[button1, button2]], resize_keyboard=True)
        await message.answer(f"вы уверены в данных?:{datas['datas']}", reply_markup=markup)
        await state.set_state(CreateStuff.sure)
        await state.update_data(datas=message.text)
        sure = await state.get_data()
        sure = sure['datas']
        if sure == "да":
            flag = False
            await state.clear()
            datas = datas["datas"].split(":")
            columns = ["from_id", "название", "TYPE",
                       "стоимость", "ACCESSES_FROM", "exp", "DELETE_FROM", "INFO"]
            result = ', '.join(map(lambda x: '0' if x == '' else x, datas))

            insert_row("STORE", columns, result)
            await message.answer("Предмет добавлен в магазин", reply_markup=None)


@router.callback_query(F.data == "add_stuff")
async def add_stuff(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="Вернуться", callback_data="35"))
    builder.add(types.InlineKeyboardButton(text="Дом", callback_data="create_build"))
    builder.add(types.InlineKeyboardButton(text="Инвентарь", callback_data="create_item"))
    await bot.edit_message_text(text="Какой предмет вы хотите добавить?",
                                chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                reply_markup=builder.as_markup()
                                )


@router.callback_query(F.data == "Inventory")
async def inventory(callback: types.CallbackQuery):
    inventory = online_players.get_players(callback.from_user.id).inventory

    items = []

    for item in inventory:
        if inventory[item] == 0 or inventory[item] == "0":
            items.append("Ничего нет")
        else:
            items.append(inventory[item])
    print(items)
    text = \
        (
            f"Верхний убор: {items[0]}\n"
            f"Ваше украшение:  {items[1]}\n"
            f"Питомец : {html.bold(items[2])}\n")

    builder = InlineKeyboardBuilder().add(types.InlineKeyboardButton(text="Меню", callback_data="1"))
    add_back(builder, 35)
    await bot.edit_message_text(text=text,
                                chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                reply_markup=builder.as_markup()
                                )


@router.callback_query(F.data[:3] == "dec")
async def decision(callback: types.CallbackQuery):
    dat_call = callback.data.split(":")
    builder, text = create_inline_builds(int(dat_call[2]), callback.from_user.id)

    await bot.edit_message_text(text="Что желаете купить?\n" + text,
                                chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                reply_markup=builder.as_markup(), parse_mode="HTML"
                                )
    pass


def switcher(id_):
    if id_ == 41:
        return 1
    elif id_ == 14:
        return 0


def create_inline_builds(id_, user_id):
    childrens = Tree_Des.get_children(id_)
    text = ""
    builder = InlineKeyboardBuilder()
    childr = Tree_Des.get_node(id_)
    player = online_players.get_players(user_id)
    buildings = player.get_builds()
    text = f"{html.italic(childr.optional_datas['COMMENT'])}\nВыберите:\n"
    for child in childrens:

        name_build = child.name
        price = child.options()['стоимость']

        adjusted_price = price * math.exp(1 / 10 * (buildings.get(name_build, 1)))
        adjusted_price = int(adjusted_price)
        if len(name_build) > 62 or len(str(adjusted_price)) > 63 or len(str(child.optional_datas['exp'])) > 63:
            assert "Превышен размер текста в inline кнопке"
        if int(child.optional_datas["ACCESSES_FROM"]) < player.get_profile_data("LEVEL") < int(
                child.optional_datas["DELETE_FROM"]):
            builder.add(types.InlineKeyboardButton(text=name_build[:62],
                                                   callback_data=f"buy:"
                                                                 f"{str(name_build).replace('_', ' ')}:"
                                                                 f"{adjusted_price}:{child.optional_datas['exp']}:"))

            text += (html.bold(str(name_build).replace("_", " "))
                     + ": " + html.code(str(format_price(adjusted_price))) + '\n')
            text += "characteristic: \n<blockquote>"
            text += child.optional_datas['INFO'] + '</blockquote>\n'
    add_back(builder, id_)
    builder.adjust(3)
    return builder, text


def create_inline_keyboard_start(datas, back="1"):
    """
    Эта функция создает инлайн-клавиатуру с начальными опциями для пользователя.

    Параметры:
    datas (list): Список кортежей, содержащий данные действий. Каждый кортеж содержит:
                   (id, название_действия, parent_id, category_id, доступность)
    back (str, optional): Строка, представляющая данные обратного вызова для кнопки 'назад'.
                          По умолчанию равно "1".

    Возвращает:
    InlineKeyboardBuilder: Экземпляр InlineKeyboardBuilder с начальными опциями.
    """
    builder = InlineKeyboardBuilder()
    text = "somet"
    for i in range(1, len(datas)):

        if datas[i][5] == 0:
            continue
        else:
            builder.add(types.InlineKeyboardButton(text=str(datas[i][1]), callback_data=str(datas[i][0])))
    return builder


def create_inline_keyboard(datas, back="1"):
    builder = InlineKeyboardBuilder()
    text = "somet"
    if datas[0][3] == 1:
        for data in datas:
            if data[5] == 0:
                continue
            else:
                builder.add(types.InlineKeyboardButton(text=str(data[1]), callback_data="dec" + ":"
                                                                                        + "1" + ":" + str(data[0])))
    else:
        for data in datas:
            if data[5] == 0:
                continue
            else:
                builder.add(types.InlineKeyboardButton(text=str(data[1]), callback_data=str(data[0])))
    if str(datas[0][2]) != "1":
        builder.add(types.InlineKeyboardButton(text="назад", callback_data="back:" + str(datas[0][2])))
    builder.adjust(3)
    return builder


def create_inline_keyboard_(id, back="1", level=1):
    childrens = Tree_Des.get_children(id)
    builder = InlineKeyboardBuilder()
    end = 1 if childrens[0].is_leaf else 0

    callback_text = f"dec:{end}:" if end else ""
    for child in childrens:
        if child.visible and level > int(child.optional_datas["ACCESSES_FROM"]):
            builder.add(types.InlineKeyboardButton(text=str(child.name),
                                                   callback_data=callback_text + str(child.node_id)))
    builder.adjust(3)

    if id != "1":
        builder.row(types.InlineKeyboardButton(text="◀️Назад", callback_data=f"back:{id}"))
    #
    return builder





def add_user(user_id, username, referrer_id=None):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE id = ?', (user_id,))
    if cursor.fetchone() is None:
        print("new_player")
        cursor.execute('INSERT INTO users (id, username, referrer_id) VALUES (?, ?, ?)',
                       (user_id, username, referrer_id))
        conn.commit()


def is_new_user(user_id):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE id = ?', (user_id,))
    return cursor.fetchone() is None


async def send_tutorial(message: Message):
    tutorial_text = """

📜 Основное
Это основной раздел, где находятся важные элементы игры. Вот, что вы можете найти:

🌆 Мой город
Этот раздел предназначен для управления вашим городом. 
Он особенно важен для выполнения основных задач, связанных со строительством и развитием инфраструктуры.
В нем вы найдете:

2. 🔨 Построить здание
Самое интересное начинается здесь! Чтобы приступить к строительству зданий, выберите раздел Построить здание.
Далее перед вами откроется несколько типов строений:

Правительственные здания — важные для управления и развития вашего города.
Жилые здания — создавайте дома для жителей города.
Рабочие места — постройте фабрики, офисы и другие рабочие места для ваших горожан.
Электричество и Добыча воды — постройте объекты для обеспечения города ресурсами.
3. Дополнительные разделы
Помимо строительства, вы также можете:

В разделе Профиль вы можете посмотреть ваши вещи, статистику
Покупать питомцев, аксессуары, получать бонусы и многое другое.
Что дальше?
Теперь вы готовы начинать строить свой город! Исследуйте разделы, стройте здания и развивайте инфраструктуру.
Следите за 📊 Статистикой города, чтобы правильно распределять ресурсы и делать улучшения.

Желаем вам удачи в строительстве успешного города!

С уважением,
Команда разработчиков
    """
    await message.answer(tutorial_text, parse_mode=ParseMode.HTML)


@router.message(Command("start"))
async def start(message: Message) -> None:
    """
    This function handles the '/start' command and sends a welcome message to the user.
    It also initializes the inline keyboard with the available sections for the user to navigate.

    Parameters:
    message (Message): The Telegram message object containing the user's command.

    Returns:
    None
    """

    # Получаем ID текущего пользователя
    user_id = message.from_user.id
    username = message.from_user.username

    # Проверяем, является ли пользователь новым
    if is_new_user(user_id):
        # Получаем реферальный код (если он есть)
        args = message.text.split()

        referrer_id = int(args[1]) if len(args) > 1 and args[1].isdigit() else None

        # Сохраняем нового пользователя в базе данных
        add_user(user_id, username, referrer_id)
        name_pet = "Волк"
        online_players.get_players(user_id).inventory["Питомец"] = name_pet

        # Приветственное сообщение для новых пользователей
        await message.answer(f"Привет, {html.bold(message.from_user.full_name)}! "
                             f"Спасибо за присоединение! {'Вы были приглашены пользователем с ID ' + str(referrer_id) if referrer_id else ''}",
                             parse_mode=ParseMode.HTML)
        await send_tutorial(message)

    # Генерация и отправка стандартного приветственного сообщения и клавиатуры
    datas = fetch_data_by_name("actions", "parent_id", 1)
    builder = create_inline_keyboard_start(datas)
    if message.from_user.id in admins:
        builder.add(types.InlineKeyboardButton(text="Secret", callback_data="Admin_panel"))

    await message.answer("Вот мои команды:\n"
                         "💡 Разделы:\n"
                         "💎 Основное\n"
                         "🚀 Профиль\n"
                         "▶ Введите «Помощь [название или номер раздела]» для просмотра остальных команд",
                         reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)


@router.message(Command('referral'))
async def referral_command(message: types.Message):
    user_id = message.from_user.id
    referral_link = f"https://t.me/{(await bot.get_me()).username}?start={user_id}"
    await message.answer(f"Ваша реферальная ссылка: {referral_link}")


# Команда /my_referrals для отображения приглашенных пользователей
@router.message(Command('my_referrals'))
async def my_referrals_command(message: types.Message):
    user_id = message.from_user.id
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    # Получаем список пользователей, которых пригласил текущий пользователь
    cursor.execute('SELECT id, username FROM users WHERE referrer_id = ?', (user_id,))
    referrals = cursor.fetchall()

    if referrals:
        referral_list = "\n".join([f"ID: {ref_id}, Имя: {ref_username}" for ref_id, ref_username in referrals])
        await message.answer(f"Ваши рефералы:\n{referral_list}")
    else:
        await message.answer("У вас пока нет рефералов.")


@router.callback_query()
async def move(callback: types.CallbackQuery, last=""):
    childr = Tree_Des.get_node(callback.data)

    text = f"{html.bold(callback.from_user.full_name)},  {childr.name} \n{childr.optional_datas['COMMENT']}"
    builder = create_inline_keyboard_(callback.data,
                                      level=online_players.get_players(callback.from_user.id).get_profile_data("LEVEL"))
    await bot.edit_message_text(text=text,
                                chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                reply_markup=builder.as_markup(), parse_mode="HTML"
                                )
