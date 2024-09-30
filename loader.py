from functions.Player import LastActionMiddleware
from data.library import *
import payment
from config import database_path
TOKEN = "example_token_here"

# Initialize Bot instance with default bot properties which will be passed to all API calls
# bot = Bot(TOKEN)
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher()
dp.message.middleware(LastActionMiddleware())
dp.callback_query.middleware(LastActionMiddleware())

dp.message.register(payment.send_invoice_handler, Command(commands="donate"))
dp.pre_checkout_query.register(payment.pre_checkout_handler)
dp.message.register(payment.success_payment_handler, F.successful_payment)
dp.message.register(payment.pay_support_handler, Command(commands="paysupport"))
