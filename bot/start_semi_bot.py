import time
from pprint import pprint

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from aiogram.utils import executor
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from data import config
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

bot = Bot(token=config.SEMI_BOT_TOKEN, parse_mode='HTML', disable_web_page_preview=True)
dp = Dispatcher(bot, storage=MemoryStorage())


async def do_some():
    pass


def schedule_job():
    scheduler.add_job(do_some, 'interval', seconds=20)

async def __on_start_up(dp: Dispatcher) -> None:
    from filters import register_all_semi_filters
    from handlers import register_all_semi_handlers

    register_all_semi_filters.register(dp)
    register_all_semi_handlers.register(dp)

    schedule_job()

def start_bot():
    scheduler.start()
    executor.start_polling(dp, skip_updates=True, on_startup=__on_start_up)
