import os
import time
from pprint import pprint

import pytz
from aiogram.dispatcher import FSMContext
from aiogram.types import InputFile

from bot.start_bot import bot, dp
from aiogram import types, Dispatcher

from bot_data import config
from db.models import *
from handlers.other import telegraph_api
from keyboards import inline, reply
from keyboards.inline import setting_schedule, only_back
from states import user as user_state
from bot.start_bot import bot

from handlers.user import TEXTS, utils

from keyboards.reply import start_offer_access, add_channel, set_schedule

from db import functions as db


async def start_handler(message: types.Message, state: FSMContext):
	await user_state.Schedule.ChooseChannel.set()
	channels = Channel.select().where(Channel.admin_id == message.from_user.id)
	await message.answer(TEXTS.choose_channel, reply_markup=inline.choose_channel(channels))

async def back_to_choose_channel(call: types.CallbackQuery, state: FSMContext):
	await user_state.Schedule.ChooseChannel.set()
	channels = Channel.select().where(Channel.admin_id == call.from_user.id)
	await call.message.edit_text(TEXTS.choose_channel, reply_markup=inline.choose_channel(channels))


async def choose_channel(call: types.CallbackQuery, state: FSMContext):
	await user_state.Schedule.Main.set()
	channel = Channel.get(id=int(call.data))
	id = channel.channel_id
	await state.update_data(channel_id=id)

	schedule = ChannelSchedule.get_or_none(channel_id=id)

	if not schedule:
		schedule = ChannelSchedule.create(channel_id=id)
		schedule.save()

	chat = await bot.get_chat(id)

	await call.message.edit_text(TEXTS.schedule_message(chat, schedule), reply_markup=inline.schedule_menu(schedule))

async def edit_schedule(call: types.CallbackQuery, state: FSMContext):
	await state.set_state(user_state.Schedule.SendSchedule)
	mes = await call.message.answer(TEXTS.edit_schedule_message, reply_markup=inline.only_back())
	await state.update_data(delete_it=mes.message_id, main_message=call.message.message_id)

async def back_edit_schedule(call: types.CallbackQuery, state: FSMContext):
	await state.set_state(user_state.Schedule.Main)
	await call.message.delete()

async def send_edit_schedule(message: types.Message, state: FSMContext):
	times = []
	for i in message.text.splitlines():
		parsed = utils.just_parse_time(i)
		if not parsed:
			await message.answer("Ошибка!")
			return
		times.append(parsed)

	if len(times) > 9:
		await message.answer("Ошибка! Слишком много!")
		return

	data = await state.get_data()

	schedule = ChannelSchedule.get(channel_id=data.get('channel_id'))

	for t in range(10):
		if t <= len(times):
			setattr(schedule, f"place_{t}", times[t-1])
		else:
			setattr(schedule, f"place_{t}", None)

	schedule.save()

	ads = AdSlot.select().where(AdSlot.channel_id==schedule.channel_id)
	for ad in ads:
		ad.delete_instance()

	await state.set_state(user_state.Schedule.Main)

	await bot.delete_message(message.chat.id, message.message_id)
	await bot.delete_message(message.chat.id, data.get('delete_it'))

	chat = await bot.get_chat(schedule.channel_id)

	await bot.edit_message_text(TEXTS.schedule_message(chat, schedule), message.chat.id, data.get('main_message'), reply_markup=inline.schedule_menu(schedule))


async def click_schedule(call: types.CallbackQuery, state: FSMContext):
	spl = call.data.split('$')
	schedule = ChannelSchedule.get(channel_id=int(spl[1]))
	day = int(spl[2])
	slot = int(spl[3])

	ad = utils.slot_status(schedule.channel_id, day, slot)
	if ad:
		ad.delete_instance()
	else:
		utils.create_slot(schedule.channel_id, day, slot)

	chat = await bot.get_chat(schedule.channel_id)

	await call.message.edit_text(TEXTS.schedule_message(chat, schedule), reply_markup=inline.schedule_menu(schedule))


def register_schedule_handlers(dp: Dispatcher):
	dp.register_message_handler(start_handler, text="Расписание", state='*')

	dp.register_callback_query_handler(choose_channel, state=user_state.Schedule.ChooseChannel)
	dp.register_callback_query_handler(back_to_choose_channel, state=user_state.Schedule.Main, text="back_to_choose_channel_schedule")

	dp.register_callback_query_handler(edit_schedule, state=user_state.Schedule.Main, text="edit_schedule")
	dp.register_callback_query_handler(back_edit_schedule, state=user_state.Schedule.SendSchedule, text="back")

	dp.register_message_handler(send_edit_schedule, state=user_state.Schedule.SendSchedule, content_types=['text'])
	dp.register_callback_query_handler(click_schedule, state=user_state.Schedule.Main, text_startswith="click_schedule")
