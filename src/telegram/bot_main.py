import asyncio
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramBadRequest, TelegramNetworkError
from dotenv import load_dotenv

from src.conf import CustomLogger

from .handlers import router


async def bot_startup():
    telegram = CustomLogger("admin_bot")._logger
    while True:
        try:
            telegram.info("Load env data")
            load_dotenv(override=True)

            telegram.info("Configure bot")
            bot = Bot(token=getenv("TOKEN"))
            dp = Dispatcher()
            dp.include_router(router)

            telegram.info("Start polling")
            await dp.start_polling(bot)

        except (TelegramNetworkError, TelegramBadRequest) as e:
            telegram.info(f"Error with type: {e}")

        except Exception as e:
            telegram.critical(f"Critical Error with type: {e}", exc_info=True)


if __name__ == "__main__":
    try:
        print("Startup bot")
        asyncio.run(bot_startup())

    except KeyboardInterrupt:
        print("Bot Close")
