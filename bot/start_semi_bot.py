import tinkoff.main
from bot_data import config

import time
from pprint import pprint

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from aiogram.utils import executor
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from db.models import TinkoffOrder

scheduler = AsyncIOScheduler()

bot = Bot(token=config.ADMIN_TOKEN, parse_mode='HTML', disable_web_page_preview=True)
dp = Dispatcher(bot, storage=MemoryStorage())


async def do_some():
    ts = TinkoffOrder.select().where(TinkoffOrder.active)
    now_time = time.time()

    for t in ts:
        if now_time - int(t.order_id) > 30 * 60:
            t.active = False
            t.save()
            continue
        info = tinkoff.main.get_order_info(t.order_id)
        status = info['Payments'][0]['Status']
        if status in ['NEW', 'FORM_SHOWED']:
            continue

        if status in ['CANCELED', 'REJECTED']:
            try:
                await bot.send_message(t.user_id, 'Платеж отменен!')
            except Exception as e:
                pass
            t.active = False
            t.save()

        elif status in ['AUTHORIZED', 'CONFIRMED']:
            try:
                await bot.send_message(t.user_id, '<b>Платеж успешно получен!</b>')
                await bot.send_message(t.user_id, '<b>После выхода рекламы вы получите уведомление!</b>')
            except Exception as e:
                pass
            t.active = False
            t.save()
            tinkoff.main.confirm_order(t.payment_id)

def schedule_job():
    scheduler.add_job(do_some, 'interval', seconds=10)

async def __on_start_up(dp: Dispatcher) -> None:
    from filters import register_all_semi_filters
    from handlers import register_all_semi_handlers

    register_all_semi_filters.register(dp)
    register_all_semi_handlers.register(dp)

    schedule_job()

def start_bot():
    scheduler.start()
    executor.start_polling(dp, skip_updates=True, on_startup=__on_start_up)
