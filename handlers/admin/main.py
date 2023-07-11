import os
import time
from pprint import pprint

import pytz
from aiogram.dispatcher import FSMContext
from aiogram.types import InputFile

from bot.start_semi_bot import bot, dp
from aiogram import types, Dispatcher

from data import config
from db.models import *
from keyboards_admin import inline, reply
from keyboards.inline import setting_schedule, only_back
from states import admin as admin_state

from handlers.admin import TEXTS, utils

from keyboards.reply import start_offer_access, add_channel, set_schedule

from db import functions as db


async def start_handler(message: types.Message, state: FSMContext):
	user = Admin.get_or_none(user_id=message.from_user.id)
	if user:
		await message.answer(TEXTS.old_start, reply_markup=reply.main_keyboard())
	else:
		await admin_state.SendSmallAnswer.sendAnswerStartOfferAccess.set()
		await message.answer(TEXTS.start, reply_markup=start_offer_access())


async def send_answer_start_offer_access(message: types.Message, state: FSMContext):
	txt = message.text
	if txt == 'Согласиться':
		user = db.add_admin(user_id=message.from_user.id)
		if user:
			await admin_state.SendSmallAnswer.sendAnswerStartOfferAccess.set()
		await message.answer(TEXTS.old_start, reply_markup=reply.main_keyboard())

	elif txt == 'Отказаться':
		await message.answer(TEXTS.bot_doesnot_work)

	await state.finish()

async def write_support(message: types.Message, state: FSMContext):
	await message.answer(TEXTS.write_support)


async def choose_cat_handler(message: types.Message, state: FSMContext):
	pass


async def all_price_handler(message: types.Message, state: FSMContext):
	pass


async def saved_handler(message: types.Message, state: FSMContext):
	pass


async def myself_cabinet_handler(message: types.Message, state: FSMContext):
	pass


async def swap_links(message: types.Message, state: FSMContext):
	pass


async def basket_handler(message: types.Message, state: FSMContext):
	pass

def register_admin_handlers(dp):
	dp.register_message_handler(start_handler, commands=['start', 'restart'], state='*')
	dp.register_message_handler(start_handler, commands=['start', 'restart'], state='*')
	dp.register_message_handler(send_answer_start_offer_access,
								state=admin_state.SendSmallAnswer.sendAnswerStartOfferAccess)
	dp.register_message_handler(write_support, state='*', text='Написать нам')
	dp.register_message_handler(choose_cat_handler, state='*', text='Выбрать по КАТЕГОРИИ')
	dp.register_message_handler(all_price_handler, state='*', text='ВЕСЬ ПРАЙС')
	dp.register_message_handler(saved_handler, state='*', text='Избранное')
	dp.register_message_handler(myself_cabinet_handler, state='*', text='Личный кабинет')
	dp.register_message_handler(swap_links, state='*', text='Замена ссылок')
	dp.register_message_handler(basket_handler, state='*', text='Корзина')