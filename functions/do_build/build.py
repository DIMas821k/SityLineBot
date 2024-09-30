from aiogram.types import InlineKeyboardButton
import json
from ..imports import *
from data.sql_ import *
from ..Player import online_players

def add_back(builder: InlineKeyboardBuilder, back_id):
    builder.add(types.InlineKeyboardButton(text="назад", callback_data="back" + ":" + str(back_id)))


async def None_money(callback: types.CallbackQuery, reason:str):
    print("None_money funct")
    builder = InlineKeyboardBuilder()
    add_back(builder, 1)
    await bot.edit_message_text(
        text=reason,
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=builder.as_markup())


async def successful_purc(callback: types.CallbackQuery, player):
    print("successful_purc funct")
    builder = InlineKeyboardBuilder().add(types.InlineKeyboardButton(text="menu", callback_data="1"))

    builder.add(types.InlineKeyboardButton(text="Купить еще", callback_data=str(callback.data)))
    builder.add(types.InlineKeyboardButton(text="️◀Назад", callback_data="14"))

    levels = player.calculate_new_level()

    if levels > 0:
        await bot.edit_message_text(
            text=f"Уровень повышен до {player.get_profile_data('LEVEL')} \n Поздравляю вас!\n"
                 f"Оставшиеся деньги:{player.get_money()}\n"
                 f"Опыта до следующего уровня {player.profile['EXP_NEXT']}",
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            reply_markup=builder.as_markup()

        )
    else:
        text = (f"<blockquote>Счастье города: {round(player.profile['happines'], 2)}%\n"
                f"Производительность воды: {player.statistic['вода']}\n"
                f"Производительность энергии: {player.statistic['энергия']}\n"
                f"Скорость обработки мусора: {player.statistic['Производимый_мусор']}\n"
                f"Заработок: {player.statistic['Прибыль']}</blockquote>\n")

        await bot.edit_message_text(
            text=f"Успешная покупка,"
                 f"Ваша статистика !\n{text}\n"
                 f" хотели бы повторить еще? \n Оставшиеся деньги: "
                 f"{online_players.get_players(callback.from_user.id).get_money()}",
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            reply_markup=builder.as_markup(),parse_mode=ParseMode.HTML)


@dp.callback_query(F.data[:3] == "buy")
async def buy(callback: types.CallbackQuery):
    datas = callback.data.split(":")
    price = int(datas[2].replace(".", ""))
    name_build = datas[1].replace(" ", "_")
    exp = int(datas[3])
    player = online_players.get_players(callback.from_user.id)
    res, call = player.buy(name_build, price)
    if not res:
        await None_money(callback, call)
    else:
        player.profile["EXP"] += exp
        await successful_purc(callback, player)
