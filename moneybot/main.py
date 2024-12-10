import logging
import asyncio
from aiogram import Bot, Dispatcher
from config import API_TOKEN
from registration import register_handlers
from handlers import registerr_handlers
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters.state import StateFilter
from database import init_db

storage = MemoryStorage()
dp = Dispatcher(storage=storage)

dp.message.filter(StateFilter)


logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

init_db()

register_handlers(dp)
registerr_handlers(dp)


async def main():
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())
