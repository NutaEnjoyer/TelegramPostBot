import time
from pprint import pprint

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from aiogram.utils import executor
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from bot_data import config
from db import functions
from db.models import PostTime, Post, SendedPost, Channel
from handlers.user import utils
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

bot = Bot(token=config.ADMIN_TOKEN, parse_mode='HTML', disable_web_page_preview=True)
dp = Dispatcher(bot, storage=MemoryStorage())


async def do_some():
    posts = PostTime.select().where(PostTime.active)
    for post_time in posts:
        if time.time() >= post_time.time:
            post = functions.get_post_by_id(post_time.id)
            if post:
                await utils.send_post(post, post_time.user_id)

            post_time.active = False
            post_time.save()

    posts = Post.select()
    for post in posts:
        if post.delete_time is None:
            continue
        if post.delete_time < time.time():
            print(post.id)
            try:
                sended_message = SendedPost.get(post_id=post.id)
                channel = Channel.get(id=sended_message.channel_id)
                await bot.delete_message(channel.channel_id, sended_message.message_id)
                sended_message.delete_instance()
                post.delete_instance()
            except Exception as e:
                print(e)


def schedule_job():
    scheduler.add_job(do_some, 'interval', seconds=5)

async def __on_start_up(dp: Dispatcher) -> None:
    from filters import register_all_filters
    from handlers import register_all_handlers

    register_all_filters.register(dp)
    register_all_handlers.register(dp)

    schedule_job()

def start_bot():
    scheduler.start()
    executor.start_polling(dp, skip_updates=True, on_startup=__on_start_up)
