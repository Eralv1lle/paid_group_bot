from aiogram import Bot, Dispatcher

import json
import asyncio
import logging

from config import *
from handlers import router, pending_requests


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
dp.include_router(router)


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logging.info(pending_requests)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("бот остановлен")

        with open("pending_requests.json", "w", encoding="utf-8") as file:
            json.dump(pending_requests, file, ensure_ascii=False, indent=2)

        print("Данные сохранены")
