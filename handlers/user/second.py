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
	await message.answer("WORK!!!")

async def admin_handler(message: types.Message, state: FSMContext):
	await message.answer("<b>🥷🏿 Панель администратора 🥷🏿</b>", reply_markup=reply.admin())

async def mail_handler(message: types.Message, state: FSMContext):
	await message.answer("<b>🥷🏿 Пришлите сообщение для рассылки 📩</b>", reply_markup=inline.only_back())
	await user_state.Admin.SendMail.set()

async def block_handler(message: types.Message, state: FSMContext):
	await message.answer("<b>🥷🏿 Пришлите id канала который хотите заблокировать 🚫</b>", reply_markup=inline.only_back())
	await user_state.Admin.SendBlock.set()

async def send_block_back(call: types.Message, state: FSMContext):
	await state.finish()
	await call.message.delete()

async def send_block(message: types.Message, state: FSMContext):
	if not message.text.isdigit():
		await message.answer('Ошибка Id!')
		return
	
	channel_id = int(message.text)
	channel = Channel.get_or_none(channel_id=channel_id)

	if not channel:
		await message.answer('Канал с данным Id не найден!')
		return
	
	find_channel = FindChannel.get_or_none(channel_id=channel_id)

	if find_channel:
		find_channel.delete_instance()

	moderators = Moderator.select().where(Moderator.channel_id==channel_id)
	for moder in moderators:
		moder.delete_instance()

	post_times = PostTime.select().where(PostTime.channel_id==channel.id)
	for pt in post_times:
		pt.delete_instance()

	block_channel = ChannelBlock.create(channel_id=channel_id)
	block_channel.save()
	try:
		await bot.send_message(channel.admin_id, f"<b>🚫 Ваш канал {channel.title} заблокирова администрацией 🚫</b>")
	except Exception as e:
		pass

	channel.delete_instance()
	
	await message.answer("<b>🥷🏿 Канал успешно заблокирован 🚫</b>")
	await state.finish()

async def send_mail(message: types.Message, state: FSMContext):
	await state.finish()

	await message.answer(f"<b>🥷🏿 Рассылка началась 📩\n\n</b><i>ℹ️ После завершения вам придет уведомление</i>")

	users = User.select()
	success = 0
	failed = 0 
	for user in users:
		if ((success + failed) % 50 == 0) and (success + failed) != 0:
			time.sleep(20)
		try: 
			await message.copy_to(user.user_id)
			success += 1
		except Exception as e:
			failed += 1 
		

	await message.answer(f"<b>🥷🏿 Рассылка завершена 📩\n\n📬 Отправлено: {success}\n🚫 Заблокировано: {failed}</b>")

async def echo_handler(message: types.Message, state: FSMContext):
	import json

	print('\n###################################################')
	print('                   # NEW MESSAGE #                 ')
	print('###################################################\n')	
	print(json.dumps(message.to_python(), indent=4, sort_keys=True))
	# await bot.send_video_note(message.from_user.id, message.video_note.file_id)
	await bot.send_voice(message.from_user.id, message.voice.file_id, caption="А прикинь можно")
	
async def all_other(message: types.Message, state: FSMContext):
	print(message)
	print(message.chat.type)
	if not message.forward_from_chat:
		print('forward')
		return
	channel = Channel.get_or_none(channel_id=message.forward_from_chat.id)
	config = ChannelConfiguration.get_or_none(channel_id=message.forward_from_chat.id)
	if not(config and channel):
		print('config')

		return
	if config.linked_chat_id != message.chat.id:
		print('linked_chat')
		return
	sended_posts = SendedPost.select().where((SendedPost.channel_id==channel.id) & (time.time() - SendedPost.time < 100))
	for sended_post in sended_posts:
		print('Sended post: ', sended_post.id)
		if type(sended_post.message_id) is int:
			if sended_post.message_id == message.forward_from_message_id:
				print('IN')
				post_info = PostInfo.get(post_id=sended_post.post_id)
				print(post_info.with_comment)
				if not post_info.with_comment:
					await bot.delete_message(message.chat.id, message.message_id)
		else:
			message_ids = [int(i) for i in sended_post.message_id.split('$')]
			if message.forward_from_message_id in message_ids:
				post_info = PostInfo.get(post_id=sended_post.post_id)
				if not post_info.with_comment:
					await bot.delete_message(message.chat.id, message.message_id)

def register_second_handlers(dp: Dispatcher):
	# dp.register_message_handler(echo_handler, state='*', content_types=types.ContentTypes.ANY)
	dp.register_message_handler(start_handler, commands=['check'], state='*')
	dp.register_message_handler(admin_handler, commands=['admin'], state='*')
	dp.register_message_handler(mail_handler, content_types=['text'], text='Рассылка', state='*')
	dp.register_message_handler(block_handler, content_types=['text'], text='Блокировать канал', state='*')
	dp.register_message_handler(all_other, lambda message: message.chat.type=='supergroup', content_types=types.ContentTypes.ANY, state='*')	