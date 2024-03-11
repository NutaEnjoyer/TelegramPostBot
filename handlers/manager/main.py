from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import InputFile

from bot.start_bot_container import bot
from db import functions as db
from db.models import Channel, Manager
from . import templates, utils

async def manager_handler(message: types.Message, state: FSMContext):
	await state.finish()
	await message.answer(templates.manager_text, reply_markup=templates.manager_menu())


async def schedule_handler(message: types.Message, state: FSMContext):
	channels = Manager.select().where(Manager.admin_id == message.from_user.id)
	channels = [Channel.get(channel_id=i.channel_id) for i in channels]

	await message.answer(templates.schedule_text, reply_markup=templates.schedule_menu(channels))


async def channel_schedule_handler(call: types.CallbackQuery, state: FSMContext):
	channel_id = int(call.data.split('$')[1])
	today = db.get_all_content_plan(0, channel_id=channel_id)
	next_1 = db.get_all_content_plan(1, channel_id=channel_id)
	next_2 = db.get_all_content_plan(2, channel_id=channel_id)

	text = utils.content_plan_text(today, next_1, next_2)

	await call.message.edit_text(text, reply_markup=templates.back_to_schedule_choose())


async def back_schedule_handler(call: types.CallbackQuery, state: FSMContext):
	channels = Manager.select().where(Manager.admin_id == call.from_user.id)
	channels = [Channel.get(channel_id=i.channel_id) for i in channels]
	await call.message.edit_text(templates.schedule_text, reply_markup=templates.schedule_menu(channels))

def register_manager_handlers(dp: Dispatcher):
	from handlers.manager.cabinet import register_cabinet_handlers
	from handlers.manager.poster import register_poster_handlers

	dp.register_message_handler(manager_handler, text=[templates.manager_button, templates.main_menu_button], state='*')
	dp.register_message_handler(schedule_handler, text=templates.schedule_button, state="*")

	dp.register_callback_query_handler(channel_schedule_handler, text_startswith="manager_open_channel_schedule", state="*")
	dp.register_callback_query_handler(back_schedule_handler, text="back_to_schedule_choose", state="*")

	register_cabinet_handlers(dp)
	register_poster_handlers(dp)


