from aiogram.types import LabeledPrice, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import PreCheckoutQuery

def payment_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text=f"Оплатить 20 ⭐️", pay=True)

    return builder.as_markup()

async def send_invoice_handler(message: Message):
    prices = [LabeledPrice(label="XTR", amount=20)]
    builder = InlineKeyboardBuilder()
    builder.button(text=f"Оплатить 20 ⭐️", pay=True)
    await message.answer_invoice(
        title="Поддержка канала",
        description="Поддержать канал на 20 звёзд!",
        prices=prices,
        provider_token="",
        payload="channel_support",
        currency="XTR",
        reply_markup=builder.as_markup()
    )

async def send_invoice_handler(message: Message):
    prices = [LabeledPrice(label="XTR", amount=20)]
    await message.answer_invoice(
        title="Поддержка канала",
        description="Поддержать канал на 20 звёзд!",
        prices=prices,
        provider_token="",
        payload="channel_support",
        currency="XTR",
        reply_markup=payment_keyboard(),
    )
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)

async def success_payment_handler(message: Message):
    await message.answer(text="🥳Спасибо за вашу поддержку!🤗")
async def pay_support_handler(message: Message):
    await message.answer(
        text="Добровольные пожертвования не подразумевают возврат средств, "  
        "однако, если вы очень хотите вернуть средства - свяжитесь с нами."    )