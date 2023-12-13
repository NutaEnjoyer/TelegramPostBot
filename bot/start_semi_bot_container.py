from aiogram import Bot
from bot_data import config


if config.DEBUG: 
    bot = Bot(token=config.BUY_BOT_TOKEN_DEBUG, parse_mode='HTML', disable_web_page_preview=True)
else:
    bot = Bot(token=config.BUY_BOT_TOKEN, parse_mode='HTML', disable_web_page_preview=True)