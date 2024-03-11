from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import InputFile

from bot.start_bot_container import bot
from db import functions as db
from db.models import Channel, Manager, ManagerPlacement
from . import templates, utils


async def cabinet_handler(message: types.Message, state: FSMContext):
	await message.answer(templates.cabinet_message, reply_markup=templates.cabinet_menu())

async def cabinet_my_channels_handler(message: types.Message, state: FSMContext):
	channels = Manager.select().where(Manager.admin_id == message.from_user.id)
	channels = [await bot.get_chat(i.channel_id) for i in channels]

	await message.answer(templates.cabinet_my_channels_message(channels))

async def channel_debt_handler(message: types.Message, state: FSMContext):
	debt = await utils.get_channel_debt(message.from_user.id)
	await message.answer(templates.channel_debt_message, reply_markup=templates.channel_debt_menu(debt))


async def client_debt_handler(message: types.Message, state: FSMContext):
	debt = await utils.get_client_debt(message.from_user.id)
	await message.answer(templates.client_debt_message, reply_markup=templates.client_debt_menu(debt))

async def back_to_channel_debt_handler(call: types.CallbackQuery, state: FSMContext):
	debt = await utils.get_channel_debt(call.from_user.id)
	await call.message.edit_text(templates.channel_debt_message, reply_markup=templates.channel_debt_menu(debt))

async def back_to_client_debt_handler(call: types.CallbackQuery, state: FSMContext):
	debt = await utils.get_client_debt(call.from_user.id)
	await call.message.edit_text(templates.client_debt_message, reply_markup=templates.client_debt_menu(debt))

async def open_client_debt_handler(call: types.CallbackQuery, state: FSMContext):
	id = int(call.data.split('$')[1])
	placement = ManagerPlacement.get(id=id)
	client = placement.client_name
	await call.message.edit_text(templates.client_debt_form_message(client, placement), reply_markup=templates.client_debt_manu(placement))

async def open_channel_debt_handler(call: types.CallbackQuery, state: FSMContext):
	id = int(call.data.split('$')[1])
	placement = ManagerPlacement.get(id=id)
	chat = await bot.get_chat(placement.channel_id)
	channel = f"""<a href="{chat.invite_link}">{chat.title}</a>"""
	manager = Manager.get(admin_id=call.from_user.id)
	await call.message.edit_text(templates.channel_debt_form_message(channel, placement, manager.rate),
								 reply_markup=templates.channel_debt_manu(placement))


async def pay_client_debt_handler(call: types.CallbackQuery, state: FSMContext):
	id = int(call.data.split('$')[1])
	placement = ManagerPlacement.get(id=id)
	placement.is_paid = True
	if placement.fee_is_paid: placement.fee_is_paid = False
	placement.save()

	await back_to_client_debt_handler(call, state)

async def pay_channel_debt_handler(call: types.CallbackQuery, state: FSMContext):
	from .poster import service_poster_manager_post_paid

	await service_poster_manager_post_paid(call, state)

	await back_to_channel_debt_handler(call, state)


async def placement_stat_handler(message: types.Message, state: FSMContext):
	channels = Manager.select().where(Manager.admin_id == message.from_user.id)
	channels = [await bot.get_chat(i.channel_id) for i in channels]
	t = templates.placement_stat_form(utils.placement_stat(message.from_user.id))
	await message.answer(templates.placement_stat_form(utils.placement_stat(message.from_user.id)), reply_markup=templates.placement_stat_menu(channels))


async def channel_placement_stat_handler(call: types.CallbackQuery, state: FSMContext):
	channel = await bot.get_chat(int(call.data.split('$')[1]))
	await call.message.edit_text(templates.channel_placement_stat_form(channel, utils.channel_placement_stat(call.from_user.id, channel.id)),
						 reply_markup=templates.back_placement_stat_menu())


async def back_placement_stat_handler(call: types.CallbackQuery, state: FSMContext):
	channels = Manager.select().where(Manager.admin_id == call.from_user.id)
	channels = [await bot.get_chat(i.channel_id) for i in channels]
	await call.message.edit_text(templates.placement_stat_form(utils.placement_stat(call.from_user.id)),
						 reply_markup=templates.placement_stat_menu(channels))


def register_cabinet_handlers(dp: Dispatcher):
	dp.register_message_handler(cabinet_handler, text=templates.cabinet_button, state='*')
	dp.register_message_handler(cabinet_my_channels_handler, text=templates.my_manage_channels_button, state='*')
	dp.register_message_handler(channel_debt_handler, text=templates.channel_debt_button, state='*')
	dp.register_message_handler(client_debt_handler, text=templates.client_debt_button, state='*')
	dp.register_message_handler(placement_stat_handler, text=templates.placement_stat_button, state='*')

	dp.register_callback_query_handler(back_to_client_debt_handler, text='back_to_client_debt', state="*")
	dp.register_callback_query_handler(back_to_channel_debt_handler, text='back_to_channel_debt', state="*")

	dp.register_callback_query_handler(open_client_debt_handler, text_startswith='open_client_debt', state="*")
	dp.register_callback_query_handler(open_channel_debt_handler, text_startswith='open_channel_debt', state="*")

	dp.register_callback_query_handler(pay_client_debt_handler, text_startswith='pay_client_debt', state="*")
	dp.register_callback_query_handler(pay_channel_debt_handler, text_startswith='pay_channel_debt', state="*")

	dp.register_callback_query_handler(back_placement_stat_handler, text_startswith='back_placement_stat', state="*")
	dp.register_callback_query_handler(channel_placement_stat_handler, text_startswith='open_channel_placement_stat', state="*")


