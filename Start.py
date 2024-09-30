from functions.Importis import *
from loader import *
import sys
import asyncio

async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":

    
    try:
        asyncio.run(main())

    except Exception as e:
        print(f"Завершение программы,код завершения - {e}  ")
    finally:
        print("Удачи")
