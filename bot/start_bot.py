import datetime
import time
from pprint import pprint

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from aiogram.utils import executor
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from bot_data import config
from db import functions
from db.models import *
from handlers.user import utils
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.start_bot_container import bot

scheduler = AsyncIOScheduler()


# if config.DEBUG: 
#     bot = Bot(token=config.ADS_BOT_TOKEN_DEBUG, parse_mode='HTML', disable_web_page_preview=True)
# else:
#     bot = Bot(token=config.ADS_BOT_TOKEN, parse_mode='HTML', disable_web_page_preview=True)
    
dp = Dispatcher(bot, storage=MemoryStorage())


async def do_some():
    posts = PostTime.select().where(PostTime.active)
    for post_time in posts:
        now_time = time.time()
        if now_time >= post_time.time:
            if now_time - post_time.time < 100:
                if not await utils.is_no_paid(post_time):
                    post = functions.get_post_by_id(post_time.id)
                    if post:
                        mes = await utils.send_post(post, post_time.user_id, post_time.id)
                        if utils.is_ad(post_time):
                            await utils.new_contract(post_time, mes)
                            utils.new_ad_placement(post_time, mes)


            post_time.active = False
            post_time.save()

    posts = DictObject.select()
    for post in posts:
        if post.delete_time is None:
            continue
        if post.delete_time < time.time():
            print(post.id)
            try:
                sended_message = SendedPost.get_or_none(post_id=post.id)
                if not sended_message:
                    post.delete_instance()
                    continue
                channel = Channel.get(id=sended_message.channel_id)
                if type(sended_message.message_id) is str:
                    for i in sended_message.message_id.split('$'):
                        await bot.delete_message(channel.channel_id, int(i))
                else:
                    await bot.delete_message(channel.channel_id, sended_message.message_id)
                sended_message.delete_instance()
                post.delete_instance()
            except Exception as e:
                print(e)

    dvs = DeferredVerification.select().where((DeferredVerification.active) &
                                             (DeferredVerification.finish_time < time.time()))
    for dv in dvs:
        print(f"{dv.id=}")
        await utils.dv_proccess(dv)
    

def update_channel_info(find_channel: FindChannel):
    from handlers.other.tg_stat import (
        get_channel_views,
        get_channel_err,
        get_channel_subscriber,
        get_channel_stat,
        get_channel_info,
        get_channel_avg_posts_reach
    )


    v = get_channel_avg_posts_reach(find_channel.channel_id)
    e = get_channel_err(find_channel.channel_id)
    s = get_channel_subscriber(find_channel.channel_id)

    find_channel.subscribers = s
    find_channel.views = v
    find_channel.err = e

    find_channel.save()


async def update_channels_info():
    print('START')

    find_channels = FindChannel.select()

    for find_channel in find_channels:
        update_channel_info(find_channel)

def schedule_job():
    current_time = datetime.datetime.now()
    next_day = current_time + datetime.timedelta(days=1)
    desired_time = next_day.replace(hour=4, minute=0, second=0, microsecond=0)
    scheduler.add_job(do_some, 'interval', seconds=8)
    scheduler.add_job(update_channels_info, 'interval', seconds=86400, next_run_time=desired_time)

async def __on_start_up(dp: Dispatcher) -> None:
    from filters import register_all_filters
    from handlers import register_all_handlers

    register_all_filters.register(dp)
    register_all_handlers.register(dp)

    schedule_job()

def start_bot():
    scheduler.start()
    executor.start_polling(dp, skip_updates=True, on_startup=__on_start_up)
