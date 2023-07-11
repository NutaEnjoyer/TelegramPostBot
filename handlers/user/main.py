import os
import time
from pprint import pprint

import pytz
from aiogram.dispatcher import FSMContext
from aiogram.types import InputFile

from bot.start_bot import bot, dp
from aiogram import types, Dispatcher

from data import config
from db.models import *
from keyboards import inline, reply
from keyboards.inline import setting_schedule, only_back
from states import user as user_state

from handlers.user import TEXTS, utils

from keyboards.reply import start_offer_access, add_channel, set_schedule

from db import functions as db


async def start_handler(message: types.Message, state: FSMContext):
	user = db.add_user(user_id=message.from_user.id)
	if user:
		await user_state.SendSmallAnswer.sendAnswerStartOfferAccess.set()
		await message.answer(TEXTS.start, reply_markup=start_offer_access())
	else:
		await message.answer(TEXTS.old_start, reply_markup=reply.main_keyboard())


async def send_answer_start_offer_access(message: types.Message, state: FSMContext):
	txt = message.text
	if txt == 'Согласиться':
		await message.answer(TEXTS.access_start_offer, reply_markup=add_channel())

	elif txt == 'Отказаться':
		await message.answer(TEXTS.bot_doesnot_work)

	await state.finish()


async def add_channel_begin(message: types.Message, state: FSMContext):
	await user_state.AddNewChannel.sendMessageFromChannel.set()
	current_directory = os.getcwd()
	photo = InputFile(path_or_bytesio=f'{current_directory}/images/bot_rights.png')
	await message.answer_photo(photo, caption=TEXTS.instruct_to_add_channel, reply_markup=types.ReplyKeyboardRemove())


async def add_channel_end(message: types.Message, state: FSMContext):
	_channel_id = message.forward_from_chat.id
	bot_is_admin = await utils.check_admin_rights(_channel_id)

	if bot_is_admin:
		info = await utils.get_channel_info(_channel_id)
		resp = db.add_channel(admin_id=message.from_user.id, channel_id=_channel_id, title=info.title)
		if resp is None:
			await message.answer(TEXTS.the_channel_already_added)
			return
		await message.answer(TEXTS.the_channel_success_added, reply_markup=set_schedule())

		await state.finish()
		await user_state.SettingSchedule.SettingSchedule.set()
		await state.update_data(channel_id=_channel_id)

	else:
		await message.answer(TEXTS.bot_is_not_admin)


async def set_schedule_(message: types.Message, state: FSMContext):
	await message.answer(TEXTS.setting_schedule, reply_markup=setting_schedule())


async def set_schedule_main(message: types.Message, state: FSMContext):
	await message.answer(TEXTS.setting_schedule, reply_markup=setting_schedule(without=True))


async def next_setting_schedule(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	if data.get('back_to_channel_setting'):
		channel = Channel.get(channel_id=data['channel_id'])
		await user_state.Settings.SettingChannel.set()
		await state.update_data(channel_id=channel.channel_id)
		await call.message.edit_text(TEXTS.channel_setting, reply_markup=inline.channel_setting())
	else:
		await call.message.delete()
		await call.message.answer(TEXTS.old_start, reply_markup=reply.main_keyboard())
		await state.finish()


async def set_output_time(call: types.CallbackQuery, state: FSMContext):
	context = await state.get_data()
	await state.finish()
	await user_state.SettingSchedule.SetPostCount.set()
	await state.update_data(channel_id=context['channel_id'], message_id=call.message.message_id)
	await call.message.edit_text(TEXTS.set_output_time, reply_markup=only_back())


async def set_output_time_answer(message: types.Message, state: FSMContext):
	context = await state.get_data()
	schedule = Schedule.get_or_none(channel_id=context['channel_id'])
	if schedule is None:
		schedule = Schedule.create(channel_id=context['channel_id'])

	try:
		num = int(message.text)
	except Exception as e:
		await message.answer(TEXTS.error)
		return

	db.update_schedule(schedule_id=schedule.id, posts_count=num)
	await state.finish()
	await user_state.SettingSchedule.SetOutputTime.set()
	await state.update_data(channel_id=context['channel_id'], post=1)
	await bot.delete_message(message.from_user.id, context['message_id'])
	await message.answer(TEXTS.set_post_output_time.format(post=1))


async def set_post_output_time(message: types.Message, state: FSMContext):
	context = await state.get_data()
	schedule = Schedule.get_or_none(channel_id=context['channel_id'])

	time = utils.time_message_convert(message.text)
	if time is None:
		await message.answer(TEXTS.error)
		return

	db.update_schedule(schedule_id=schedule.id, post_time=time)
	if context['post'] == schedule.posts_count:
		await state.finish()
		await user_state.SettingSchedule.SettingSchedule.set()
		await state.update_data(channel_id=context['channel_id'])
		await message.answer(TEXTS.setting_schedule, reply_markup=setting_schedule())

	else:
		await state.update_data(post=context['post']+1)
		await message.answer(TEXTS.set_post_output_time.format(post=context['post']+1))


async def set_output_interval(call: types.CallbackQuery, state: FSMContext):
	context = await state.get_data()
	await state.finish()
	await user_state.SettingSchedule.SetOutputInterval.set()
	await state.update_data(channel_id=context['channel_id'], message_id=call.message.message_id)
	await call.message.edit_text(TEXTS.set_output_interval, reply_markup=inline.only_back())


async def set_output_interval_answer(message: types.Message, state: FSMContext):
	context = await state.get_data()
	schedule = Schedule.get_or_none(channel_id=context['channel_id'])
	if schedule is None:
		schedule = Schedule.create(channel_id=context['channel_id'])

	try:
		num = int(message.text)
	except Exception as e:
		await message.answer(TEXTS.error)
		return

	db.update_schedule(schedule_id=schedule.id, interval=num)
	await state.finish()
	await user_state.SettingSchedule.SettingSchedule.set()
	await state.update_data(channel_id=context['channel_id'])
	await bot.delete_message(message.from_user.id, context['message_id'])
	await message.answer(TEXTS.setting_schedule, reply_markup=setting_schedule())


async def set_day_interval(call: types.CallbackQuery, state: FSMContext):
	context = await state.get_data()
	await state.finish()
	await user_state.SettingSchedule.SetDayInterval.set()
	await state.update_data(channel_id=context['channel_id'], message_id=call.message.message_id)
	await call.message.edit_text(TEXTS.set_day_interval, reply_markup=inline.only_back())


async def set_day_interval_answer(message: types.Message, state: FSMContext):
	context = await state.get_data()
	schedule = Schedule.get_or_none(channel_id=context['channel_id'])
	if schedule is None:
		schedule = Schedule.create(channel_id=context['channel_id'])

	try:
		num = int(message.text)
	except Exception as e:
		await message.answer(TEXTS.error)
		return

	db.update_schedule(schedule_id=schedule.id, week_interval=num)
	await state.finish()
	await user_state.SettingSchedule.SettingSchedule.set()
	await state.update_data(channel_id=context['channel_id'])
	await bot.delete_message(message.from_user.id, context['message_id'])
	await message.answer(TEXTS.setting_schedule, reply_markup=setting_schedule())


async def setting_schedule_back(call: types.CallbackQuery, state: FSMContext):
	context = await state.get_data()
	await state.finish()
	await user_state.SettingSchedule.SettingSchedule.set()
	await state.update_data(channel_id=context['channel_id'])
	await call.message.edit_text(TEXTS.setting_schedule, reply_markup=setting_schedule())


async def set_confirm(call: types.CallbackQuery, state: FSMContext):
	context = await state.get_data()
	await state.finish()
	await user_state.SettingSchedule.SetConfirm.set()
	await state.update_data(channel_id=context['channel_id'])
	await call.message.edit_text(TEXTS.set_confirm, reply_markup=inline.set_confirm())


async def set_confirm_answer(call: types.CallbackQuery, state: FSMContext):
	context = await state.get_data()
	ans = call.data.split('_')[1] == 'yes'
	schedule = Schedule.get_or_none(channel_id=context['channel_id'])
	if schedule is None:
		schedule = Schedule.create(channel_id=context['channel_id'])

	db.update_schedule(schedule_id=schedule.id, confirm=ans)

	if ans:
		await state.finish()
		await user_state.SettingSchedule.SettingSchedule.set()
		await state.update_data(channel_id=context['channel_id'])
		await call.message.edit_text(TEXTS.setting_schedule, reply_markup=setting_schedule())

	else:
		await user_state.ChooseCategory.Main.set()
		pams = schedule.confirm_themes
		if pams is None:
			await state.update_data(channel_id=context['channel_id'], pams=[])
			await call.message.edit_text(TEXTS.choose_category, reply_markup=inline.choose_category([]))
		else:
			pams = pams.split('$')
			await state.update_data(channel_id=context['channel_id'], pams=pams)
			await call.message.edit_text(TEXTS.choose_category, reply_markup=inline.choose_category(pams))


async def choose_category(call: types.CallbackQuery, state: FSMContext):
	data = call.data.split('$')
	state_data = await state.get_data()
	pams = state_data['pams']

	if data[0] == 'choose_category_end':
		resp = ''
		for pam in pams:
			resp += pam + '$'
		resp = resp[:-1]
		schedule = Schedule.get(channel_id=state_data['channel_id'])
		db.update_schedule(schedule_id=schedule.id, confirm_themes=resp)
		await state.finish()
		await user_state.SettingSchedule.SettingSchedule.set()
		await state.update_data(channel_id=state_data['channel_id'])
		await call.message.edit_text(TEXTS.setting_schedule, reply_markup=setting_schedule())

		return

	cat = data[1]
	act = data[2]

	if act == 'on':
		pams.append(cat)
	else:
		pams.remove(cat)

	await state.update_data(pams=pams)
	await call.message.edit_reply_markup(reply_markup=inline.choose_category(pams))


async def publications_handler(message: types.Message, state: FSMContext):
	await message.answer(TEXTS.publications_menu, reply_markup=reply.publications_keyboard())


async def settings_handler(message: types.Message, state: FSMContext):
	await user_state.Settings.Main.set()
	await message.answer(TEXTS.settings_menu, reply_markup=inline.setting_keyboard())


async def advert_handler(message: types.Message, state: FSMContext):
	await user_state.Advert.Main.set()
	await message.answer(TEXTS.advert_menu, reply_markup=inline.advert_keyboard())


async def cabinet_handler(message: types.Message, state: FSMContext):
	await message.answer(TEXTS.cabinet_menu, reply_markup=reply.cabinet_keyboard())


async def cabinet_payment_data_handler(message: types.Message, state: FSMContext):
	await user_state.CabinetPaymentData.Main.set()
	await message.answer(TEXTS.cabinet_payment_data, reply_markup=inline.cabinet_payment_data_keyboard())


async def content_plan_handler(message: types.Message, state: FSMContext):
	await user_state.ContentPlan.ChooseChannel.set()
	channels = Channel.select().where(Channel.admin_id == message.from_user.id)

	await message.answer(TEXTS.choose_channel, reply_markup=inline.choose_channel(channels))


async def choose_channel_content_plan(call: types.CallbackQuery, state: FSMContext):
	channel = Channel.get(id=int(call.data))

	await user_state.ContentPlan.Main.set()
	await state.update_data(channel_id=channel.id)

	await call.message.edit_text(TEXTS.content_plan, reply_markup=inline.content_plan_keyboard())


async def balance_my_wallet_handler(message: types.Message, state: FSMContext):
	await user_state.BalanceMyWallet.Main.set()
	await message.answer(TEXTS.balance_my_wallet, reply_markup=inline.balance_my_wallet_keyboard())


async def advert_creatives(call: types.CallbackQuery, state: FSMContext):
	await call.message.edit_reply_markup(reply_markup=inline.advert_creatives_keyboard())


async def advert_back(call: types.CallbackQuery, state: FSMContext):
	await call.message.edit_text(TEXTS.advert_menu, reply_markup=inline.advert_keyboard())


async def content_plan_back(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	if data.get('advert_plan'):
		data.pop('advert_plan')
		print(data)
	await state.update_data(data)

	await call.message.edit_text(TEXTS.content_plan, reply_markup=inline.content_plan_keyboard())


async def content_plan_set_post_time(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	time_post = PostTime.get_or_none(post_id=data['post_id'])
	if time_post:
		await user_state.ContentPlan.SetPostTime.set()
		await state.update_data(data)
		await state.update_data(post_date=0)
		data = await state.get_data()
		await call.message.edit_text(TEXTS.postpone_rule, reply_markup=inline.postpone(data))


async def content_plan_delete_post(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()

	sended_post = SendedPost.get_or_none(post_id=data['post_id'])

	if sended_post:
		channel = Channel.get(id=sended_post.channel_id)
		await bot.delete_message(channel.channel_id, sended_post.message_id)
		sended_post.delete_instance()
		post = Post.get(id=data['post_id'])
		post.delete_instance()

	else:
		time_post = PostTime.get(post_id=data['post_id'])
		time_post.delete_instance()
		post = Post.get(id=data['post_id'])
		post.delete_instance()

	data = await state.get_data()
	posts = db.get_all_content_plan(0, channel_id=data['channel_id'])
	pprint(posts)

	await call.message.edit_text('Общий контент план', reply_markup=inline.all_content_plan_keyboard(0, posts))


async def content_plan_copy_post(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	await user_state.ContentPlan.ResendPost.set()
	await state.update_data(data)
	await call.message.edit_text(TEXTS.message_will_be_post_question, reply_markup=inline.message_will_post())

async def content_plan_edit_post(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	await call.message.edit_text(TEXTS.edit_post, reply_markup=inline.edit_post(data['post_id']))


async def content_plan_edit_media(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	post = Post.get(id=data['post_id'])
	if post.media is None or post.media == '':
		await call.message.answer('Не доступно для данного сообщения')
		return
	await user_state.EditPost.EditMedia.set()
	await state.update_data(data)

	await call.message.edit_text(TEXTS.edit_media, reply_markup=inline.only_back())

async def edit_post_media(message: types.Message, state: FSMContext):
	data = await state.get_data()
	if data.get('date') is None or data.get('date') == message.date:
		try:
			await state.update_data(media=(data.get('media') if data.get('media') else []) + [message.photo[0].file_id])
		except Exception as e:
			new_media = (data.get('media') if data.get('media') else []) + [] if (
				data.get('media') is None or message.video.file_id in data.get('media')) else [
				message.video.file_id]
			await state.update_data(media=new_media)

	else:
		try:
			await state.update_data(media=(data.get('media') if data.get('media') else []) + [message.photo[0].file_id])
		except Exception as e:
			new_media = (data.get('media') if data.get('media') else []) + [] if (
					data.get('media') is None or message.video.file_id in data.get('media')) else [
				message.video.file_id]
			await state.update_data(media=new_media)

	flag = False
	try:
		mes = await bot.copy_message(config.TRASH_CHANNEL_ID, message.from_user.id, message_id=message.message_id + 1)
		await bot.delete_message(config.TRASH_CHANNEL_ID, mes.message_id)
	except Exception as e:
		flag = True

	if flag:  # the last message
		data = await state.get_data()
		media = data.pop('media')

		resp = await utils.edit_post_media(data['post_id'], media)

		if resp:
			await message.answer('Error!')
			return

		await user_state.ContentPlan.Main.set()
		await state.update_data(data)
		await message.answer(TEXTS.edit_post, reply_markup=inline.edit_post(data['post_id']))


async def content_plan_edit_text(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	await user_state.EditPost.EditText.set()
	await state.update_data(data)

	await call.message.edit_text(TEXTS.edit_text, reply_markup=inline.only_back())




async def edit_post_text(message: types.Message, state: FSMContext):
	data = await state.get_data()
	await utils.edit_post_text(post_id=data['post_id'], text=message.html_text)
	await user_state.ContentPlan.Main.set()
	await state.update_data(data)
	await message.answer(TEXTS.edit_post, reply_markup=inline.edit_post(data['post_id']))


async def content_plan_edit_markup(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	post = Post.get(id=data['post_id'])
	if not(post.media is None) and len(post.media.split('$')) > 1:
		await call.message.answer('Не доступно для данного сообщения')
		return
	await user_state.EditPost.EditMarkup.set()
	await state.update_data(data)

	await call.message.edit_text(TEXTS.edit_markup, reply_markup=inline.only_back())

async def edit_post_markup(message: types.Message, state: FSMContext):
	data = await state.get_data()
	try:
		reply_markup, reaction_with = inline.parse_swap_keyboard(message.text, data['channel_id'])
		mes = await bot.send_message(config.TRASH_CHANNEL_ID, 'qwerty', reply_markup=reply_markup)
		await bot.delete_message(config.TRASH_CHANNEL_ID, mes.message_id)
	except Exception as e:
		await message.answer(TEXTS.error_parse_keyboard)
		return

	if reply_markup is None:
		await message.answer(TEXTS.error_parse_keyboard)
		return

	await utils.edit_post_markup(post_id=data['post_id'], reply_markup=reply_markup, reaction_with=reaction_with)

	await user_state.ContentPlan.Main.set()
	await state.update_data(data)
	await message.answer(TEXTS.edit_post, reply_markup=inline.edit_post(data['post_id']))

async def content_plan_back_to_edit_post(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	await user_state.ContentPlan.Main.set()
	await state.update_data(data)
	await call.message.edit_text(TEXTS.edit_post, reply_markup=inline.edit_post(data['post_id']))

async def content_plan_set_price(call: types.CallbackQuery, state: FSMContext):
	await call.message.edit_text(TEXTS.set_price_rule, reply_markup=inline.only_back())
	data = await state.get_data()
	await user_state.ContentPlan.SetPrice.set()
	await state.update_data(data)


async def content_plan_send_price(message: types.Message, state: FSMContext):
	if not message.text.isdigit():
		await message.answer('Ошибка!')
		return
	price = int(message.text)
	data = await state.get_data()
	post = Post.get(id=data['post_id'])
	post.price = price
	post.save()

	post_id = data['post_id']
	post = Post.get(id=post_id)
	sended_post = SendedPost.get_or_none(post_id=post_id)
	post_data = db.from_post_id_to_data(post_id)
	await user_state.ContentPlan.Main.set()
	await state.update_data(data)

	if sended_post:
		chat = await bot.get_chat(sended_post.user_id)
		print(chat)
		status = '✅ Опубликован'
		post_type = 'рекламный 💰' if post.price else 'обычный'
		author = f"<a href='https://t.me/{chat.username}'>{chat.first_name}</a>"
		await message.answer(TEXTS.open_post_text.format(status=status, post_type=post_type, author=author),
								  reply_markup=inline.open_post(post_date=sended_post.human_time, post=post))

	else:
		time_post = PostTime.get(post_id=post_id)
		chat = await bot.get_chat(time_post.user_id)
		print(chat)
		status = '⏳ Отложен'
		post_type = 'рекламный 💰' if post.price else 'обычный'
		author = f"<a href='https://t.me/{chat.username}'>{chat.first_name}</a>"
		await message.answer(TEXTS.open_post_text.format(status=status, post_type=post_type, author=author),
								  reply_markup=inline.open_post(post_date=time_post.human_time, post=post))


async def content_plan_set_price_back(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	post_id = data['post_id']
	post = Post.get(id=post_id)
	sended_post = SendedPost.get_or_none(post_id=post_id)
	post_data = db.from_post_id_to_data(post_id)
	await call.message.delete()
	await user_state.ContentPlan.Main.set()
	await state.update_data(data)
	if sended_post:
		chat = await bot.get_chat(sended_post.user_id)
		print(chat)
		status = '✅ Опубликован'
		post_type = 'рекламный 💰' if post.price else 'обычный'
		author = f"<a href='https://t.me/{chat.username}'>{chat.first_name}</a>"
		await call.message.answer(TEXTS.open_post_text.format(status=status, post_type=post_type, author=author),
								  reply_markup=inline.open_post(post_date=sended_post.human_time, post=post))

	else:
		time_post = PostTime.get(post_id=post_id)
		chat = await bot.get_chat(time_post.user_id)
		print(chat)
		status = '⏳ Отложен'
		post_type = 'рекламный 💰' if post.price else 'обычный'
		author = f"<a href='https://t.me/{chat.username}'>{chat.first_name}</a>"
		await call.message.answer(TEXTS.open_post_text.format(status=status, post_type=post_type, author=author),
								  reply_markup=inline.open_post(post_date=time_post.human_time, post=post))


async def content_plan_set_delete_time(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	await user_state.ContentPlan.SetDeleteTime.set()
	await state.update_data(data)
	await state.update_data(post_date=0)
	data = await state.get_data()
	await call.message.edit_text(TEXTS.delete_time_rule, reply_markup=inline.postpone(data))

async def advert_content_plan(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	await state.update_data(advert_plan=True)
	posts = db.get_advert_content_plan(0, channel_id=data['channel_id'])
	await call.message.edit_text('Коммерческие размещения', reply_markup=inline.all_content_plan_keyboard(0, posts))


async def all_content_plan(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	await state.update_data(advert_plan=False)
	print('IT is all_content_plan', data)
	posts = db.get_all_content_plan(0, channel_id=data['channel_id'])
	await call.message.edit_text('Общий контент план', reply_markup=inline.all_content_plan_keyboard(0, posts))

async def back_to_all_content_plan(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	if data.get('advert_plan'):
		posts = db.get_advert_content_plan(0, channel_id=data['channel_id'])

	else:
		posts = db.get_all_content_plan(0, channel_id=data['channel_id'])


	pprint(posts)
	await bot.delete_message(call.message.chat.id, data.pop('message_to_delete'))
	await call.message.edit_text('Общий контент план', reply_markup=inline.all_content_plan_keyboard(0, posts))


async def open_all_content_plan(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	time_delta = int(call.data.split('$')[1])
	print(1)
	print(data.get('advert_plan'))
	if data.get('advert_plan'):
		print(1)
		posts = db.get_advert_content_plan(time_delta, channel_id=data['channel_id'])

	else:
		posts = db.get_all_content_plan(time_delta, channel_id=data['channel_id'])

	await call.message.edit_text('Общий контент план', reply_markup=inline.all_content_plan_keyboard(time_delta, posts))


async def open_all_schedule_posts(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	posts = db.get_all_schedule_posts(channel_id=data['channel_id'], advert=data.get('advert_plan'))
	pprint(posts)

	await call.message.edit_text('Общий контент план', reply_markup=inline.all_content_plan_keyboard(0, posts, without_date=True))


async def open_post(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	post_id = int(call.data.split('$')[1])
	post = Post.get(id=post_id)
	sended_post = SendedPost.get_or_none(post_id=post_id)
	post_data = db.from_post_id_to_data(post_id)
	mes = await utils.send_old_post_to_user(call.from_user.id, post_data)
	if type(mes) is list:
		mes = mes[-1]
	await state.update_data(post_id=post_id, message_to_delete=mes.message_id)
	await call.message.delete()
	if sended_post:
		chat = await bot.get_chat(sended_post.user_id)
		print(chat)
		status = '✅ Опубликован'
		post_type = 'рекламный 💰' if post.price else 'обычный'
		author = f"<a href='https://t.me/{chat.username}'>{chat.first_name}</a>"
		await call.message.answer(TEXTS.open_post_text.format(status=status, post_type=post_type, author=author), reply_markup=inline.open_post(post_date=sended_post.human_time, post=post))

	else:
		time_post = PostTime.get(post_id=post_id)
		chat = await bot.get_chat(time_post.user_id)
		print(chat)
		status = '⏳ Отложен'
		post_type = 'рекламный 💰' if post.price else 'обычный'
		author = f"<a href='https://t.me/{chat.username}'>{chat.first_name}</a>"
		await call.message.answer(TEXTS.open_post_text.format(status=status, post_type=post_type, author=author), reply_markup=inline.open_post(post_date=time_post.human_time, post=post))


async def rewrite_post_handler(message: types.Message, state: FSMContext):
	await user_state.RewritePost.Main.set()

	await message.answer(TEXTS.rewrite_post_main, reply_markup=reply.only_cancel())


async def rewrite_get_post(message: types.Message, state: FSMContext):
	print(message)
	try:
		channel_id = message.forward_from_chat.id
		message_id = message.forward_from_message_id
	except Exception as e:
		print(e)
		await message.answer('Ошибка!')
		return

	bot_is_admin = await utils.check_admin_rights(channel_id)
	if not bot_is_admin:
		await message.answer(TEXTS.bot_is_not_admin)
		return

	channel = Channel.get(channel_id=channel_id)
	sended_posts = SendedPost.select().where(SendedPost.channel_id==channel.id)
	sended_post = None

	for post in sended_posts:
		if post.message_id == message_id:
			sended_post = post

	if sended_post is None:
		await message.answer('Сообщение отправлено не через бота')
		return

	mes = await message.answer(TEXTS.edit_post, reply_markup=inline.edit_post_main())

	post = Post.get(id=sended_post.post_id)

	await state.update_data(post_id=post.id, messages_to_delete=[message.message_id, mes.message_id])


async def rewrite_get_post_back(message: types.Message, state: FSMContext):
	data = await state.get_data()
	await state.finish()
	if data.get('messages_to_delete'):
		for i in data.get('messages_to_delete'):
			try:
				await bot.delete_message(message.from_user.id, i)
			except Exception as e:
				pass
	try:
		await bot.delete_message(message.from_user.id, message.message_id)
	except Exception as e:
		pass
	await message.answer(TEXTS.old_start, reply_markup=reply.main_keyboard())


async def rewrite_get_post_just_back(message: types.Message, state: FSMContext):
	data = await state.get_data()
	try:
		mes_id = data.pop('just_back_id')
		await bot.delete_message(message.from_user.id, message.message_id)
		await bot.delete_message(message.from_user.id, mes_id)
	except Exception as e:
		pass

	mes = await message.answer(TEXTS.edit_post, reply_markup=inline.edit_post_main())

	await user_state.RewritePost.Main.set()
	await state.update_data(messages_to_delete=data['messages_to_delete'] + [mes.message_id])


async def rewrite_post_edit_text(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	await user_state.RewritePost.EditText.set()
	await state.update_data(data)

	mes = await call.message.answer(TEXTS.edit_text)
	await state.update_data(just_back_id=mes.message_id)
	await call.message.delete()


async def rewrite_post_edit_text_send(message: types.Message, state: FSMContext):
	data = await state.get_data()
	await utils.edit_post_text(post_id=data['post_id'], text=message.html_text)
	await user_state.RewritePost.Main.set()
	await state.update_data(data)
	await rewrite_get_post_just_back(message, state)


async def rewrite_post_edit_media(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	post = Post.get(id=data['post_id'])
	print(post.media)
	if post.media is None or post.media == '':
		await call.message.answer('Не доступно для данного сообщения')
		return
	await user_state.RewritePost.EditMedia.set()
	await state.update_data(data)

	mes = await call.message.answer(TEXTS.edit_media)
	await state.update_data(just_back_id=mes.message_id)

	await call.message.delete()


async def rewrite_post_edit_media_send(message: types.Message, state: FSMContext):
	data = await state.get_data()
	if data.get('date') is None or data.get('date') == message.date:
		try:
			await state.update_data(media=(data.get('media') if data.get('media') else []) + [message.photo[0].file_id])
		except Exception as e:
			new_media = (data.get('media') if data.get('media') else []) + [] if (data.get('media') is None or (message.video.file_id in data.get('media'))) else [message.video.file_id]
			await state.update_data(media=new_media)

	else:
		try:
			await state.update_data(media=(data.get('media') if data.get('media') else []) + [message.photo[0].file_id])
		except Exception as e:
			new_media = (data.get('media') if data.get('media') else []) + [] if (data.get('media') is None or (message.video.file_id in data.get('media'))) else [message.video.file_id]
			await state.update_data(media=new_media)

	flag = False
	try:
		mes = await bot.copy_message(config.TRASH_CHANNEL_ID, message.from_user.id, message_id=message.message_id + 1)
		await bot.delete_message(config.TRASH_CHANNEL_ID, mes.message_id)
	except Exception as e:
		flag = True

	if flag:  # the last message
		data = await state.get_data()
		media = data.pop('media')

		resp = await utils.edit_post_media(data['post_id'], media)

		if resp:
			await message.answer('Error!')
			return

		await user_state.RewritePost.Main.set()
		await state.update_data(data)
		await message.answer(TEXTS.edit_post, reply_markup=inline.edit_post(data['post_id']))


async def rewrite_post_edit_markup(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	post = Post.get(id=data['post_id'])
	if not (post.media is None) and len(post.media.split('$')) > 1:
		await call.message.answer('Не доступно для данного сообщения')
		return
	await user_state.RewritePost.EditMarkup.set()
	await state.update_data(data)

	mes = await call.message.answer(TEXTS.edit_markup)
	await state.update_data(just_back_id=mes.message_id)

	await call.message.delete()


async def rewrite_post_edit_markup_send(message: types.Message, state: FSMContext):
	data = await state.get_data()
	try:
		sended_post = SendedPost.get(post_id=data['post_id'])
		reply_markup, reaction_with = inline.parse_swap_keyboard(message.text, sended_post.channel_id)
		if reaction_with is None:
			channel = Channel.get(id=sended_post.channel_id)
			channel_config = ChannelConfiguration.get(channel_id=channel.channel_id)
			reaction_with = channel_config.reactions
		mes = await bot.send_message(config.TRASH_CHANNEL_ID, 'qwerty', reply_markup=reply_markup)
		await bot.delete_message(config.TRASH_CHANNEL_ID, mes.message_id)
	except Exception as e:
		print(e)
		await message.answer(TEXTS.error_parse_keyboard)
		return

	if reply_markup is None:
		await message.answer(TEXTS.error_parse_keyboard)
		return

	await utils.edit_post_markup(post_id=data['post_id'], reply_markup=reply_markup, reaction_with=reaction_with)

	await user_state.RewritePost.Main.set()
	await state.update_data(data)
	await rewrite_get_post_just_back(message, state)

async def create_post_handler(message: types.Message, state: FSMContext):
	channels = Channel.select().where(Channel.admin_id == message.from_user.id)
	await user_state.CreatePost.ChooseChannel.set()
	await message.answer(TEXTS.choose_channel, reply_markup=inline.choose_channel(channels))


async def create_post_select_channel(call: types.CallbackQuery, state: FSMContext):
	channel_id = int(call.data)
	channel = Channel.get(id=channel_id)
	await user_state.AddPost.SendPost.set()
	await state.update_data(channel_id=channel_id, active=False, date=None, text='', media=[], reply_markup=None)
	await call.message.delete()
	await call.message.answer(TEXTS.send_post.format(title=channel.title), reply_markup=reply.send_post())


async def phys_person(call: types.CallbackQuery, state: FSMContext):
	await user_state.SelfPerson.Main.set()
	await call.message.edit_text(TEXTS.phys_person, reply_markup=inline.add_card_number())


async def self_employed(call: types.CallbackQuery, state: FSMContext):
	await user_state.SelfPerson.Main.set()
	await call.message.edit_text(TEXTS.self_employed, reply_markup=inline.add_card_number_ORD())


async def IPOOO(call: types.CallbackQuery, state: FSMContext):
	await user_state.SelfPerson.Main.set()
	await call.message.edit_text(TEXTS.IPOOO, reply_markup=inline.add_INN_ORD())


async def self_person_add_card(call: types.CallbackQuery, state: FSMContext):
	await user_state.SelfPerson.SendCardNumber.set()
	await call.message.edit_text(TEXTS.send_card_number, reply_markup=only_back())


async def self_person_send_card(message: types.Message, state: FSMContext):
	await message.answer('Готово')
	await user_state.CabinetPaymentData.Main.set()
	db.update_admin(admin_id=message.from_user.id, card_number=message.text)
	await user_state.CabinetPaymentData.Main.set()
	await message.answer(TEXTS.cabinet_payment_data, reply_markup=inline.cabinet_payment_data_keyboard())


async def self_person_add_ORD(call: types.CallbackQuery, state: FSMContext):
	pass

async def self_person_send_ORD(message: types.Message, state: FSMContext):
	pass

async def self_person_add_INN(call: types.CallbackQuery, state: FSMContext):
	pass

async def self_person_send_INN(message: types.Message, state: FSMContext):
	pass


async def self_person_back(call: types.CallbackQuery, state: FSMContext):
	await user_state.CabinetPaymentData.Main.set()
	await call.message.edit_text(TEXTS.cabinet_payment_data, reply_markup=inline.cabinet_payment_data_keyboard())

#####################################

async def cancel_send_post_handler(message: types.Message, state: FSMContext):
	await state.finish()
	await message.answer(TEXTS.old_start, reply_markup=reply.main_keyboard())


async def swap_keyboard(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	await user_state.AddPost.SwapKeyboard.set()
	mes = await call.message.answer(TEXTS.swap_keyboard_rules, reply_markup=reply.only_cancel())
	await state.update_data(data=data, message_id=[call.message.message_id, mes.message_id])


async def cancel_swap_keyboard(message: types.Message, state: FSMContext):
	data = await state.get_data()
	message_id = data.pop('message_id')
	await user_state.AddPost.SendPost.set()
	await state.update_data(data=data)

	await bot.delete_message(message.from_user.id,  message_id[0])
	await bot.delete_message(message.from_user.id,  message_id[1])

	data = await state.get_data()

	markup = inline.add_markup_send_post(data['reply_markup'])

	data['reply_markup'] = markup

	await utils.send_post_to_user(data, message.from_user.id)
	await bot.delete_message(message.from_user.id, message.message_id)

	await message.answer('Продолжай отправлять сообщения.', reply_markup=reply.send_post())


async def swap_keyboard_handler(message: types.Message, state: FSMContext):
	data = await state.get_data()
	try:
		reply_markup, reaction_with = inline.parse_swap_keyboard(message.text, data['channel_id'])
		print(reply_markup)
		mes = await bot.send_message(config.TRASH_CHANNEL_ID, 'qwerty', reply_markup=reply_markup)
	except Exception as e:
		await message.answer(TEXTS.error_parse_keyboard)
		return

	if reply_markup is None:
		await message.answer(TEXTS.error_parse_keyboard)
		return

	await state.update_data(reply_markup=reply_markup, reaction_with=reaction_with)
	data = await state.get_data()
	data['reaction_with'] = reaction_with
	await user_state.AddPost.SendPost.set()
	await state.update_data(data=data)

	print(f'DATA: ', data)
	print(1, data['reply_markup'])


	new_data = {}
	for k in data.keys():
		new_data[k] = data[k]

	print(2, data['reply_markup'])

	markup = inline.add_markup_send_post(new_data['reply_markup'])

	new_data['reply_markup'] = markup
	new_data['reaction_with'] = reaction_with

	print(1, data['reply_markup'])

	await utils.send_post_to_user(new_data, message.from_user.id)

	data['reply_markup'] = mes.reply_markup
	await bot.delete_message(config.TRASH_CHANNEL_ID, mes.message_id)
	await bot.delete_message(message.from_user.id, data['message_id'][0])
	await bot.delete_message(message.from_user.id, data['message_id'][1])
	await bot.delete_message(message.from_user.id, message.message_id)

	await state.update_data(data=data)
	data = await state.get_data()
	print(data)
	await message.answer('Клавиатура сохраненна.\nПродолжай отправлять сообщения.', reply_markup=reply.send_post())


async def send_photo_post_handler(message: types.Message, state: FSMContext):
	data = await state.get_data()
	print(message)
	if data['date'] is None or data['date'] == message.date:
		try:
			text = message.html_text
		except Exception as e:
			text = data['text']
		try:
			type = 'photo'
			media = data['media'] + [message.photo[0].file_id]
		except Exception as e:
			type = 'video'
			media = data['media'] + [message.video.file_id]

		await state.update_data(active=True,
								media=media,
								text=text,
								reply_markup=inline.rewrite_keyboard(message.reply_markup) if message.reply_markup else data['reply_markup'])
	else:
		try:
			text = message.html_text
		except Exception as e:
			text = ''

		try:
			type = 'photo'
			media =[message.photo[0].file_id]
		except Exception as e:
			type = 'video'
			media = [message.video.file_id]

		await state.update_data(active=True,
								media=media,
								text=text,
								reply_markup=message.reply_markup if message.reply_markup else None)

	flag = False
	try:
		mes = await bot.copy_message(config.TRASH_CHANNEL_ID, message.from_user.id, message_id=message.message_id + 1)
		await bot.delete_message(config.TRASH_CHANNEL_ID, mes.message_id)
	except Exception as e:
		flag = True

	if flag:  # the last message
		data = await state.get_data()
		print(data['text'])

		markup = inline.add_markup_send_post(data['reply_markup'])
		if len(data['media']) == 1:
			try:
				await message.answer_photo(data['media'][0], caption=data['text'], reply_markup=markup)
			except Exception as e:
				await message.answer_video(data['media'][0], caption=data['text'], reply_markup=markup)

		else:
			media = types.MediaGroup()
			for i in range(len(data['media'])):
				if i == len(data['media']) - 1:
					try:
						print('photo is')
						mes = await bot.send_photo(config.TRASH_CHANNEL_ID, data['media'][i])
						type = 'photo'

					except Exception as e:
						print('Except')
						mes = await bot.send_video(config.TRASH_CHANNEL_ID, data['media'][i])
						type = 'video'

					if type == 'photo':
						media.attach_photo(data['media'][i], caption=data['text'])
					elif type == 'video':
						media.attach_video(data['media'][i], caption=data['text'])

					# try:
					# 	media.attach_photo(data['media'][i], data['text'])
					# except Exception as e:
					# 	media.attach_video(data['media'][i], data['text'])
				else:
					try:
						print('photo is')
						mes = await bot.send_photo(config.TRASH_CHANNEL_ID, data['media'][i])
						type = 'photo'

					except Exception as e:
						print('Except')
						mes = await bot.send_video(config.TRASH_CHANNEL_ID, data['media'][i])
						type = 'video'

					if type == 'photo':
						media.attach_photo(data['media'][i])
					elif type == 'video':
						media.attach_video(data['media'][i])

					# try:
					# 	media.attach_photo(data['media'][i])
					# except Exception as e:
					# 	media.attach_video(data['media'][i])

			print('SEND')

			await message.answer_media_group(media)
			await message.answer(TEXTS.album_edit, disable_web_page_preview=True)


async def send_text_post_handler(message: types.Message, state: FSMContext):
	await state.update_data(active=True, text=message.html_text, reply_markup=inline.rewrite_keyboard(message.reply_markup))
	data = await state.get_data()
	markup = inline.add_markup_send_post(data['reply_markup'])
	await message.answer(data['text'], reply_markup=markup, disable_web_page_preview=True)


async def next_send_post_handler(message: types.Message, state: FSMContext):
	data = await state.get_data()
	print(data)
	if data['active']:
		channel = Channel.get(id=data['channel_id'])
		await message.answer(TEXTS.message_will_be_post.format(title=channel.title), reply_markup=types.ReplyKeyboardRemove())
		await message.answer(TEXTS.message_will_be_post_question, reply_markup=inline.message_will_post())
	else:
		await message.answer(TEXTS.no_one_send_post)


async def send_post_now(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	print(data)
	channel = Channel.get(id=data['channel_id'])

	try:
		await utils.send_post_to_channel(channel_id=channel.channel_id, user_id=call.from_user.id, data=data)
		await call.message.answer(TEXTS.message_posted_success.format(title=channel.title), reply_markup=reply.main_keyboard())

	except Exception as e:
		admin_id = channel.admin_id
		if admin_id == call.from_user.id:
			await call.message.answer(TEXTS.error_post_message_to_channel.format(title=channel.title))
		else:
			await call.message.answer(TEXTS.error_post_message_to_channel.format(title=channel.title))
			await bot.send_message(admin_id, TEXTS.error_post_message_to_channel.format(title=channel.title))

	await call.message.delete()

	await state.finish()

async def content_plan_copy_post_now(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	channel = Channel.get(id=data['channel_id'])

	print(1)
	await utils.send_post_to_channel_by_post_id(channel_id=channel.channel_id, user_id=call.from_user.id, post_id=data['post_id'])

	try:
		# await utils.send_post_to_channel_by_post_id(channel_id=channel.channel_id, user_id=call.from_user.id, post_id=data['post_id'])
		await call.message.answer(TEXTS.message_posted_success.format(title=channel.title))

	except Exception as e:
		await call.message.answer(TEXTS.error_post_message_to_channel.format(title=channel.title))

	post_id = data['post_id']
	post = Post.get(id=post_id)
	sended_post = SendedPost.get_or_none(post_id=post_id)
	post_data = db.from_post_id_to_data(post_id)
	mes = await utils.send_old_post_to_user(call.from_user.id, post_data)
	await state.update_data(post_id=post_id, message_to_delete=mes.message_id)

	if sended_post:
		chat = await bot.get_chat(sended_post.user_id)
		print(chat)
		status = '✅ Опубликован'
		post_type = 'рекламный 💰' if post.price else 'обычный'
		author = f"<a href='https://t.me/{chat.username}'>{chat.first_name}</a>"
		await call.message.answer(TEXTS.open_post_text.format(status=status, post_type=post_type, author=author),
							 reply_markup=inline.open_post(post_date=sended_post.human_time, post=post))

	else:
		time_post = PostTime.get(post_id=post_id)
		chat = await bot.get_chat(time_post.user_id)
		print(chat)
		status = '⏳ Отложен'
		post_type = 'рекламный 💰' if post.price else 'обычный'
		author = f"<a href='https://t.me/{chat.username}'>{chat.first_name}</a>"
		await call.message.answer(TEXTS.open_post_text.format(status=status, post_type=post_type, author=author),
							 reply_markup=inline.open_post(post_date=time_post.human_time, post=post))

	data = {
		'channel_id': data['channel_id'],
		'advert_plan': data['advert_plan']
	}

	await user_state.ContentPlan.Main.set()
	await state.update_data(data)

	await call.message.edit_text(TEXTS.edit_post)
	await user_state.ContentPlan.Main.set()
	await state.update_data(data)

async def content_plan_copy_post_postpone(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	await state.update_data(data=data)
	await state.update_data(post_date=0)
	await state.update_data(message_id=call.message.message_id)
	data = await state.get_data()
	await call.message.edit_text(TEXTS.postpone_rule, reply_markup=inline.postpone(data))


async def content_plan_copy_post_back(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	data = await state.get_data()
	await user_state.ContentPlan.Main.set()
	await state.update_data(data)
	post_id = data['post_id']
	post = Post.get(id=post_id)
	sended_post = SendedPost.get_or_none(post_id=post_id)
	post_data = db.from_post_id_to_data(post_id)
	await call.message.delete()
	if sended_post:
		chat = await bot.get_chat(sended_post.user_id)
		print(chat)
		status = '✅ Опубликован'
		post_type = 'рекламный 💰' if post.price else 'обычный'
		author = f"<a href='https://t.me/{chat.username}'>{chat.first_name}</a>"
		await call.message.answer(TEXTS.open_post_text.format(status=status, post_type=post_type, author=author),
								  reply_markup=inline.open_post(post_date=sended_post.human_time, post=post))

	else:
		time_post = PostTime.get(post_id=post_id)
		chat = await bot.get_chat(time_post.user_id)
		print(chat)
		status = '⏳ Отложен'
		post_type = 'рекламный 💰' if post.price else 'обычный'
		author = f"<a href='https://t.me/{chat.username}'>{chat.first_name}</a>"
		await call.message.answer(TEXTS.open_post_text.format(status=status, post_type=post_type, author=author),
								  reply_markup=inline.open_post(post_date=time_post.human_time, post=post))


async def postpone_post(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	await user_state.AddPost.SendTime.set()
	await state.update_data(data=data)
	await state.update_data(post_date=0)
	await state.update_data(message_id=call.message.message_id)
	data = await state.get_data()
	await call.message.edit_text(TEXTS.postpone_rule, reply_markup=inline.postpone(data))


async def postpone_back(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	channel = Channel.get(id=data['channel_id'])
	await state.update_data(active=False, date=None, text='', media=[], reply_markup=None)
	await call.message.delete()
	await call.message.answer(TEXTS.send_post.format(title=channel.title), reply_markup=reply.send_post())


async def postpone_time(call: types.CallbackQuery, state: FSMContext):
	await state.update_data(post_date=int(call.data.split('$')[1]))
	data = await state.get_data()
	await call.message.edit_text(TEXTS.postpone_rule, reply_markup=inline.postpone(data))


async def content_plan_postpone_time(call: types.CallbackQuery, state: FSMContext):
	await state.update_data(post_date=int(call.data.split('$')[1]))
	data = await state.get_data()
	await call.message.edit_text(TEXTS.postpone_rule, reply_markup=inline.postpone(data))


async def content_plan_delete_time(call: types.CallbackQuery, state: FSMContext):
	await state.update_data(post_date=int(call.data.split('$')[1]))
	data = await state.get_data()
	await call.message.edit_text(TEXTS.postpone_rule, reply_markup=inline.postpone(data))


async def postpone_time_back(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	await state.finish()
	await user_state.AddPost.SendPost.set()
	await state.update_data(channel_id=data['channel_id'], active=data['active'], date=data['date'], text=data['text'],
							media=data['media'], reply_markup=data['reply_markup'])
	await call.message.edit_text(TEXTS.message_will_be_post_question, reply_markup=inline.message_will_post())


async def content_plan_postpone_time_back(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	data.pop('post_date')
	await state.finish()
	await user_state.ContentPlan.Main.set()
	await state.update_data(data)

	await call.message.delete()

	post = Post.get(id=data['post_id'])
	post_data = db.from_post_id_to_data(data['post_id'])

	time_post = PostTime.get(post_id=data['post_id'])
	chat = await bot.get_chat(time_post.user_id)
	print(chat)
	status = '⏳ Отложен'
	post_type = 'рекламный 💰' if post.price else 'обычный'
	author = f"<a href='https://t.me/{chat.username}'>{chat.first_name}</a>"
	await call.message.answer(TEXTS.open_post_text.format(status=status, post_type=post_type, author=author),
							  reply_markup=inline.open_post(post_date=time_post.human_time, post=post))


async def content_plan_delete_time_back(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	data.pop('post_date')
	await state.finish()
	await user_state.ContentPlan.Main.set()
	await state.update_data(data)

	post_id = data['post_id']
	post = Post.get(id=post_id)
	sended_post = SendedPost.get_or_none(post_id=post_id)
	post_data = db.from_post_id_to_data(post_id)
	mes = await utils.send_old_post_to_user(call.from_user.id, post_data)
	await state.update_data(post_id=post_id, message_to_delete=mes.message_id)
	await call.message.delete()
	if sended_post:
		chat = await bot.get_chat(sended_post.user_id)
		print(chat)
		status = '✅ Опубликован'
		post_type = 'рекламный 💰' if post.price else 'обычный'
		author = f"<a href='https://t.me/{chat.username}'>{chat.first_name}</a>"
		await call.message.answer(TEXTS.open_post_text.format(status=status, post_type=post_type, author=author),
								  reply_markup=inline.open_post(post_date=sended_post.human_time, post=post))

	else:
		time_post = PostTime.get(post_id=post_id)
		chat = await bot.get_chat(time_post.user_id)
		print(chat)
		status = '⏳ Отложен'
		post_type = 'рекламный 💰' if post.price else 'обычный'
		author = f"<a href='https://t.me/{chat.username}'>{chat.first_name}</a>"
		await call.message.answer(TEXTS.open_post_text.format(status=status, post_type=post_type, author=author),
								  reply_markup=inline.open_post(post_date=time_post.human_time, post=post))



async def parse_postpone_time(message: types.Message, state: FSMContext):
	data = await state.get_data()
	pprint(data)
	parsed = utils.parse_time(message.text, data['post_date'])
	if parsed is None:
		await message.answer(TEXTS.error_parse_time)
		return
	await bot.delete_message(message.from_user.id, data['message_id'])
	human_date = parsed['human_date']
	seconds = parsed['seconds']

	data = await state.get_data()

	channel = Channel.get(id=data['channel_id'])

	db.create_post_time(data, seconds+time.time(), human_date, message.from_user.id)

	await message.answer(TEXTS.success_post_time.format(title=channel.title, date=human_date))

	await message.answer(TEXTS.old_start, reply_markup=reply.main_keyboard())

	await state.finish()

async def content_plan_copy_post_send_time(message: types.Message, state: FSMContext):
	print('Callback')
	data = await state.get_data()
	pprint(data)
	parsed = utils.parse_time(message.text, data['post_date'])
	if parsed is None:
		await message.answer(TEXTS.error_parse_time)
		return
	await bot.delete_message(message.from_user.id, data['message_id'])
	human_date = parsed['human_date']
	seconds = parsed['seconds']

	data = await state.get_data()

	channel = Channel.get(id=data['channel_id'])

	print('its ')
	d = db.from_post_id_to_data(data['post_id'])
	pprint(d)
	d['channel_id'] = data['channel_id']
	if d.get('reaction_with'):
		print('get is true')
		d['rection_with'] = inline.recreate_reactions(channel_id=data['channel_id'], reactions=d.get('reaction_with'))
	db.create_post_time(d, seconds + time.time(), human_date, message.from_user.id)

	await message.answer(TEXTS.success_post_time.format(title=channel.title, date=human_date))

	post_id = data['post_id']
	post = Post.get(id=post_id)
	sended_post = SendedPost.get_or_none(post_id=post_id)
	post_data = db.from_post_id_to_data(post_id)
	mes = await utils.send_old_post_to_user(message.from_user.id, post_data)
	if type(mes) == list:
		mes = mes[-1]
	await state.update_data(post_id=post_id, message_to_delete=mes.message_id)

	if sended_post:
		chat = await bot.get_chat(sended_post.user_id)
		print(chat)
		status = '✅ Опубликован'
		post_type = 'рекламный 💰' if post.price else 'обычный'
		author = f"<a href='https://t.me/{chat.username}'>{chat.first_name}</a>"
		await message.answer(TEXTS.open_post_text.format(status=status, post_type=post_type, author=author),
								  reply_markup=inline.open_post(post_date=sended_post.human_time, post=post))

	else:
		time_post = PostTime.get(post_id=post_id)
		chat = await bot.get_chat(time_post.user_id)
		print(chat)
		status = '⏳ Отложен'
		post_type = 'рекламный 💰' if post.price else 'обычный'
		author = f"<a href='https://t.me/{chat.username}'>{chat.first_name}</a>"
		await message.answer(TEXTS.open_post_text.format(status=status, post_type=post_type, author=author),
								  reply_markup=inline.open_post(post_date=time_post.human_time, post=post))


	data = {
		'channel_id': data['channel_id'],
		'advert_plan': data['advert_plan']
	}

	await user_state.ContentPlan.Main.set()
	await state.update_data(data)

async def content_plan_parse_postpone_time(message: types.Message, state: FSMContext):
	data = await state.get_data()
	pprint(data)
	parsed = utils.parse_time(message.text, data['post_date'])
	if parsed is None:
		await message.answer(TEXTS.error_parse_time)
		return

	human_date = parsed['human_date']
	seconds = parsed['seconds']

	channel = Channel.get(id=data['channel_id'])

	post_time = PostTime.get(post_id=data['post_id'])
	post_time.human_time = human_date
	post_time.time = seconds + time.time()
	post_time.save()

	await message.answer('Готово')

	data = await state.get_data()
	data.pop('post_date')
	await state.finish()
	await user_state.ContentPlan.Main.set()
	await state.update_data(data)

	post = Post.get(id=data['post_id'])
	post_data = db.from_post_id_to_data(data['post_id'])

	time_post = PostTime.get(post_id=data['post_id'])
	chat = await bot.get_chat(time_post.user_id)
	print(chat)
	status = '⏳ Отложен'
	post_type = 'рекламный 💰' if post.price else 'обычный'
	author = f"<a href='https://t.me/{chat.username}'>{chat.first_name}</a>"
	await message.answer(TEXTS.open_post_text.format(status=status, post_type=post_type, author=author),
							  reply_markup=inline.open_post(post_date=time_post.human_time, post=post))


async def content_plan_parse_delete_time(message: types.Message, state: FSMContext):
	data = await state.get_data()
	pprint(data)
	parsed = utils.parse_time(message.text, data['post_date'])
	if parsed is None:
		await message.answer(TEXTS.error_parse_time)
		return

	human_date = parsed['human_date']
	seconds = parsed['seconds']

	post_time = PostTime.get_or_none(post_id=data['post_id'])
	if post_time:
		t = seconds + time.time()
		if t+10 <= post_time.time:
			await message.answer(TEXTS.error_parse_time)
			return
	post = Post.get(id=data['post_id'])
	post.delete_human = human_date
	post.delete_time = seconds + time.time()
	post.save()

	await message.answer('Готово')

	data = await state.get_data()
	data.pop('post_date')
	await state.finish()
	await user_state.ContentPlan.Main.set()
	await state.update_data(data)

	post_id = data['post_id']
	sended_post = SendedPost.get_or_none(post_id=post_id)
	post_data = db.from_post_id_to_data(post_id)

	if sended_post:
		chat = await bot.get_chat(sended_post.user_id)
		print(chat)
		status = '✅ Опубликован'
		post_type = 'рекламный 💰' if post.price else 'обычный'
		author = f"<a href='https://t.me/{chat.username}'>{chat.first_name}</a>"
		await message.answer(TEXTS.open_post_text.format(status=status, post_type=post_type, author=author),
								  reply_markup=inline.open_post(post_date=sended_post.human_time, post=post))

	else:
		time_post = PostTime.get(post_id=post_id)
		chat = await bot.get_chat(time_post.user_id)
		print(chat)
		status = '⏳ Отложен'
		post_type = 'рекламный 💰' if post.price else 'обычный'
		author = f"<a href='https://t.me/{chat.username}'>{chat.first_name}</a>"
		await message.answer(TEXTS.open_post_text.format(status=status, post_type=post_type, author=author),
								  reply_markup=inline.open_post(post_date=time_post.human_time, post=post))


async def setting_back(call: types.CallbackQuery, state: FSMContext):
	await user_state.Settings.Main.set()
	await call.message.edit_text(TEXTS.settings_menu, reply_markup=inline.setting_keyboard())


async def setting_channel_back(call: types.CallbackQuery, state: FSMContext):
	await call.message.edit_text(TEXTS.channel_setting, reply_markup=inline.channel_setting())


async def setting_channel(call: types.CallbackQuery, state: FSMContext):
	await user_state.Settings.ChooseSettingChannel.set()
	channels = Channel.select().where(Channel.admin_id == call.from_user.id)
	await call.message.edit_text(TEXTS.choose_channel, reply_markup=inline.choose_channel(channels))


async def setting_channel_choose_channel(call: types.CallbackQuery, state: FSMContext):
	channel = Channel.get(id=int(call.data))
	await user_state.Settings.SettingChannel.set()
	await state.update_data(channel_id=channel.channel_id)
	await call.message.edit_text(TEXTS.channel_setting, reply_markup=inline.channel_setting())


async def setting_add_channel(call: types.CallbackQuery, state: FSMContext):
	await user_state.Settings.sendMessageFromChannel.set()
	current_directory = os.getcwd()
	photo = InputFile(path_or_bytesio=f'{current_directory}/images/bot_rights.png')
	mes = await call.message.answer_photo(photo, caption=TEXTS.instruct_to_add_channel, reply_markup=reply.only_cancel())

	await state.update_data(messages_id=[call.message.message_id, mes.message_id])


async def add_channel_end_cancel(message: types.Message, state: FSMContext):
	data = await state.get_data()

	await user_state.Settings.Main.set()
	await message.answer('Отменено', reply_markup=reply.main_keyboard())
	await message.answer(TEXTS.settings_menu, reply_markup=inline.setting_keyboard())

	try:
		await bot.delete_message(message.from_user.id, data['messages_id'][0])
		await bot.delete_message(message.from_user.id, data['messages_id'][1])
		await bot.delete_message(message.from_user.id, message.message_id)

	except Exception as e:
		pass


async def setting_application_manage(call: types.CallbackQuery, state: FSMContext):
	pass


async def setting_referal_program(call: types.CallbackQuery, state: FSMContext):
	await call.message.answer(TEXTS.referal_message.format(user_id=call.from_user.id))


async def new_join_channel(chat_join: types.ChatJoinRequest, state: FSMContext):
	channel_id = chat_join.chat.id
	user_id = chat_join.from_user.id
	channel_config = ChannelConfiguration.get_or_none(channel_id=channel_id)
	if channel_config:
		if channel_config.auto_approve:
			await chat_join.approve()
		else:
			new_join = NewJoin.create(channel_id=channel_id, user_id=user_id)
			new_join.save()


async def setting_channel_schedule(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	await user_state.SettingSchedule.SettingSchedule.set()
	await state.update_data(data, back_to_channel_setting=True)
	await call.message.edit_text(TEXTS.setting_schedule, reply_markup=setting_schedule())


async def setting_channel_public(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	channel_config = ChannelConfiguration.get(channel_id=data['channel_id'])
	await call.message.edit_text(TEXTS.public, reply_markup=inline.public(channel_config))


async def setting_channel_application_manage(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	channel_config = ChannelConfiguration.get(channel_id=data['channel_id'])
	await call.message.edit_text(TEXTS.application_manage, reply_markup=inline.application_manage(channel_config))

async def setting_channel_auto_write(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	await user_state.Settings.SendAutoWrite.set()
	await state.update_data(data, message_id=call.message.message_id)
	channel_config = ChannelConfiguration.get(channel_id=data['channel_id'])
	now_value = channel_config.auto_write if channel_config else 'Нет'
	await call.message.delete()
	await call.message.answer(TEXTS.auto_wtire_rules.format(now_value=now_value), reply_markup=reply.only_cancel())

async def setting_channel_auto_write_send(message: types.Message, state: FSMContext):
	data = await state.get_data()

	if message.text == 'Отмена':
		new_config = ChannelConfiguration.get(channel_id=data['channel_id'])
	else:
		auto_write = message.html_text
		new_config = db.update_channel_configurations(channel_id=data['channel_id'], auto_write=auto_write)

	try:
		await bot.delete_message(message.from_user.id, data.pop('message_id'))
		await bot.delete_message(message.from_user.id, message.message_id)
	except Exception as e:
		pass

	await user_state.Settings.SettingChannel.set()
	await state.update_data(data)
	mes = await message.answer('Готово', reply_markup=reply.main_keyboard())
	await message.answer(TEXTS.public, reply_markup=inline.public(new_config))


async def setting_channel_auto_approve(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	channel_config = ChannelConfiguration.get(channel_id=data['channel_id'])
	new_value = not channel_config.auto_approve
	new_config = db.update_channel_configurations(channel_id=data['channel_id'], auto_approve=new_value)
	await call.message.edit_reply_markup(inline.application_manage(new_config))


async def setting_channel_collect_orders(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	channel_config = ChannelConfiguration.get(channel_id=data['channel_id'])
	new_value = not channel_config.collect_orders
	new_config = db.update_channel_configurations(channel_id=data['channel_id'], collect_orders=new_value)
	await call.message.edit_reply_markup(inline.application_manage(new_config))


async def setting_channel_full_approve(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	await utils.approve_all(channel_id=data['channel_id'])
	await call.message.answer('Готово')


async def setting_channel_water_mark(call: types.CallbackQuery, state: FSMContext):
	pass


async def setting_channel_hour_line(call: types.CallbackQuery, state: FSMContext):
	await call.message.edit_text(TEXTS.choose_time_zone, reply_markup=inline.time_zones())


async def setting_channel_time_zone(call: types.CallbackQuery, state: FSMContext):
	new_value = int(call.data.split('$')[1])
	data = await state.get_data()
	new_config = db.update_channel_configurations(channel_id=data['channel_id'], hour_line=new_value)
	await call.message.edit_text(TEXTS.public, reply_markup=inline.public(new_config))


async def setting_channel_reactions(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	await user_state.Settings.SendReactions.set()
	await state.update_data(data, message_id=call.message.message_id)
	await call.message.delete()
	await call.message.answer(TEXTS.reactions_rule, reply_markup=reply.only_cancel())


async def setting_channel_reactions_end(message: types.Message, state: FSMContext):
	data = await state.get_data()

	if message.text == 'Отмена':
		new_config = ChannelConfiguration.get(channel_id=data['channel_id'])
	else:
		for i in message.text.split('/'):
			if len(i) > 5:
				await message.answer('Ошибка!')
				return

		new_config = db.update_channel_configurations(channel_id=data['channel_id'], reactions=message.text)

	try:
		await bot.delete_message(message.from_user.id, data.pop('message_id'))
		await bot.delete_message(message.from_user.id, message.message_id)
	except Exception as e:
		pass

	await user_state.Settings.SettingChannel.set()
	await state.update_data(data)
	mes = await message.answer('Готово', reply_markup=reply.main_keyboard())
	await message.answer(TEXTS.public, reply_markup=inline.public(new_config))


async def setting_channel_support(call: types.CallbackQuery, state: FSMContext):
	pass


async def setting_channel_preview(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	channel_config = ChannelConfiguration.get(channel_id=data['channel_id'])
	new_value = not channel_config.preview
	new_config = db.update_channel_configurations(channel_id=data['channel_id'], preview=new_value)
	await call.message.edit_reply_markup(inline.public(new_config))


async def setting_channel_point(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	channel_config = ChannelConfiguration.get(channel_id=data['channel_id'])
	new_value = not channel_config.point
	new_config = db.update_channel_configurations(channel_id=data['channel_id'], point=new_value)
	await call.message.edit_reply_markup(inline.public(new_config))


async def setting_channel_post_without_sound(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	channel_config = ChannelConfiguration.get(channel_id=data['channel_id'])
	new_value = not channel_config.post_without_sound
	new_config = db.update_channel_configurations(channel_id=data['channel_id'], post_without_sound=new_value)
	await call.message.edit_reply_markup(inline.public(new_config))


async def click_reaction_handler(call: types.CallbackQuery, state: FSMContext):
	reaction_id = int(call.data.split('$')[1])
	reaction = Reaction.get(id=reaction_id)

	user_reaction = UserReaction.select().where(UserReaction.user_id == call.from_user.id)
	flag = False
	correct = None
	for i in user_reaction:
		if i.reaction_id == reaction_id:
			correct = i
			flag = True
	if flag is False:
		user_reaction = UserReaction.create(user_id=call.from_user.id, reaction_id=reaction_id)
		user_reaction.save()
	else:
		correct	.delete_instance()

	value = len(UserReaction.select().where(UserReaction.reaction_id == reaction_id))
	reaction.value = value
	reaction.save()

	keyboard = ReactionsKeyboard.get(id=reaction.reaction_keyboard_id)
	channel = Channel.get_or_none(id=keyboard.channel_id)
	if channel is None:
		channel = Channel.get(channel_id=keyboard.channel_id)
	channel = Channel.get(channel_id=call.message.chat.id)
	posts = SendedPost.select().where(SendedPost.channel_id == channel.id)
	print(len(posts))
	correct_post = None
	for post in posts:
		if post.message_id == call.message.message_id:
			correct_post = post

	if not correct_post:
		print('not')
		return

	post = correct_post
	print('clicked')
	await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=inline.click_reaction(post, reaction_keyboard_id=keyboard.id))

async def change_links(call: types.CallbackQuery, state: FSMContext):
	await call.message.edit_text(TEXTS.change_links_start, reply_markup=inline.only_back())
	await user_state.ChangeLinks.SendPost.set()

async def change_links_back(call: types.CallbackQuery, state: FSMContext):
	await state.finish()
	await call.message.edit_text(TEXTS.advert_menu, reply_markup=inline.advert_keyboard())


async def change_links_send_text_post(message: types.Message, state: FSMContext):
	data = await state.get_data()
	await user_state.ChangeLinks.SendLink.set()
	text = message.html_text
	reply_markup = message.reply_markup
	print(data)
	await state.update_data(text=text, reply_markup=reply_markup)
	await message.answer(TEXTS.send_link)

async def change_links_send_post_back(call: types.CallbackQuery, state: FSMContext):
	await state.finish()
	await call.message.answer(TEXTS.old_start, reply_markup=reply.main_keyboard())
	await  call.message.delete()

async def change_links_send_post(message: types.Message, state: FSMContext):
	data = await state.get_data()
	if data.get('date') is None or data.get('date') == message.date:
		try:
			await state.update_data(media=(data.get('media') if data.get('media') else []) + [message.photo[0].file_id])
		except Exception as e:
			new_media = (data.get('media') if data.get('media') else []) + [message.video.file_id] if (
				data.get('media') is None or not (message.video.file_id in data.get('media'))) else []
			await state.update_data(media=new_media)

	else:
		try:
			await state.update_data(media=(data.get('media') if data.get('media') else []) + [message.photo[0].file_id])
		except Exception as e:
			new_media = (data.get('media') if data.get('media') else []) + [message.video.file_id] if (
				data.get('media') is None or not(message.video.file_id in data.get('media'))) else []
			await state.update_data(media=new_media)
	try:
		text = message.html_text
		await state.update_data(text=text)
	except Exception as e:
		pass
	flag = False
	try:
		mes = await bot.copy_message(config.TRASH_CHANNEL_ID, message.from_user.id, message_id=message.message_id + 1)
		await bot.delete_message(config.TRASH_CHANNEL_ID, mes.message_id)
	except Exception as e:
		flag = True

	if flag:  # the last message
		data = await state.get_data()
		reply_markup = message.reply_markup
		print(data)
		await user_state.ChangeLinks.SendLink.set()
		await state.update_data(data)
		await state.update_data(reply_markup=reply_markup)
		await message.answer(TEXTS.send_link)

async def change_links_send_link(message: types.Message, state: FSMContext):
	link = message.text
	data = await state.get_data()

	text = utils.swap_links_in_text(data.get('text'), link)
	text = str(text)
	markup = inline.swap_links_in_markup(data.get('reply_markup'), link)

	print(data.get('media'))

	if data.get('media') is None or data.get('media') == []:
		await message.answer(text, reply_markup=markup)

	else:
		if len(data['media']) == 1:
			try:
				await message.answer_photo(data['media'][0], caption=text, reply_markup=markup)
			except Exception as e:
				await message.answer_video(data['media'][0], caption=text, reply_markup=markup)

		else:
			media = types.MediaGroup()
			for i in range(len(data['media'])):
				if i == len(data['media']) - 1:
					try:
						print('photo is')
						mes = await bot.send_photo(config.TRASH_CHANNEL_ID, data['media'][i])
						type = 'photo'

					except Exception as e:
						print('Except')
						mes = await bot.send_video(config.TRASH_CHANNEL_ID, data['media'][i])
						type = 'video'

					if type == 'photo':
						media.attach_photo(data['media'][i], caption=text)
					elif type == 'video':
						media.attach_video(data['media'][i], caption=text)

				# try:
				# 	media.attach_photo(data['media'][i], data['text'])
				# except Exception as e:
				# 	media.attach_video(data['media'][i], data['text'])
				else:
					try:
						print('photo is')
						mes = await bot.send_photo(config.TRASH_CHANNEL_ID, data['media'][i])
						type = 'photo'

					except Exception as e:
						print('Except')
						mes = await bot.send_video(config.TRASH_CHANNEL_ID, data['media'][i])
						type = 'video'

					if type == 'photo':
						media.attach_photo(data['media'][i])
					elif type == 'video':
						media.attach_video(data['media'][i])

			await message.answer_media_group(media)

	await message.answer('Готово', reply_markup=reply.main_keyboard())
	await state.finish()

def register_user_handlers(dp: Dispatcher):
	dp.register_message_handler(start_handler, commands=['start', 'restart'], state='*')
	dp.register_message_handler(send_answer_start_offer_access,
								state=user_state.SendSmallAnswer.sendAnswerStartOfferAccess)
	dp.register_message_handler(add_channel_end_cancel, state=user_state.Settings.sendMessageFromChannel,
								text='Отмена')
	dp.register_message_handler(add_channel_end, state=[user_state.AddNewChannel.sendMessageFromChannel, user_state.Settings.sendMessageFromChannel],
								content_types=['text', 'photo', 'video', 'voice'])
	dp.register_message_handler(add_channel_begin, text='Добавить канал')
	dp.register_message_handler(start_handler, text='Меню', state='*')
	dp.register_message_handler(publications_handler, text='Публикации', state='*')
	dp.register_message_handler(settings_handler, text='Настройки', state='*')
	dp.register_message_handler(advert_handler, text='Реклама и ВП', state='*')
	dp.register_message_handler(cabinet_handler, text='Кабинет', state='*')
	dp.register_message_handler(cabinet_payment_data_handler, text='Платежные данные', state='*')
	dp.register_message_handler(balance_my_wallet_handler, text='Баланс лицевого счета', state='*')
	dp.register_message_handler(content_plan_handler, text='Контент план', state='*')
	dp.register_message_handler(create_post_handler, text='Создать пост', state='*')
	dp.register_message_handler(rewrite_post_handler, text='Редактировать пост', state='*')
	dp.register_message_handler(set_schedule_, text='Настройка расписания', state=user_state.SettingSchedule.SettingSchedule)
	dp.register_message_handler(set_schedule_main, text='Настройка расписания', state='*')
	dp.register_message_handler(edit_post_text, state=user_state.EditPost.EditText)
	dp.register_message_handler(rewrite_post_edit_text_send, state=user_state.RewritePost.EditText)
	dp.register_message_handler(edit_post_markup, state=user_state.EditPost.EditMarkup)
	dp.register_message_handler(rewrite_post_edit_markup_send, state=user_state.RewritePost.EditMarkup)
	dp.register_callback_query_handler(next_setting_schedule, state=user_state.SettingSchedule.SettingSchedule, text='next')
	dp.register_callback_query_handler(set_confirm, state=user_state.SettingSchedule.SettingSchedule, text='confirm')
	dp.register_callback_query_handler(set_confirm_answer, text_startswith='confirm_', state=user_state.SettingSchedule.SetConfirm)
	dp.register_callback_query_handler(set_day_interval, state=user_state.SettingSchedule.SettingSchedule, text='day_interval')
	dp.register_callback_query_handler(setting_schedule_back, text='back', state=user_state.SettingSchedule)
	dp.register_message_handler(set_day_interval_answer, state=user_state.SettingSchedule.SetDayInterval)
	dp.register_message_handler(set_output_interval_answer, state=user_state.SettingSchedule.SetOutputInterval)
	dp.register_callback_query_handler(set_output_interval, state=user_state.SettingSchedule.SettingSchedule, text='output_interval')
	dp.register_message_handler(set_output_time_answer, state=user_state.SettingSchedule.SetPostCount)
	dp.register_callback_query_handler(set_output_time, state=user_state.SettingSchedule.SettingSchedule, text='output_time')
	dp.register_message_handler(set_post_output_time, state=user_state.SettingSchedule.SetOutputTime)
	dp.register_callback_query_handler(advert_creatives, state=user_state.Advert.Main, text='advert_creatives')
	dp.register_callback_query_handler(advert_back, state=user_state.Advert.Main, text='back')
	dp.register_callback_query_handler(choose_channel_content_plan, state=user_state.ContentPlan.ChooseChannel)
	dp.register_callback_query_handler(advert_content_plan, state=user_state.ContentPlan.Main, text='advert')
	dp.register_callback_query_handler(all_content_plan, state=user_state.ContentPlan.Main, text='all')
	dp.register_callback_query_handler(back_to_all_content_plan, state=user_state.ContentPlan.Main, text='back_to_all_content_plan')
	dp.register_callback_query_handler(open_all_content_plan, state=user_state.ContentPlan.Main, text_startswith='open_all_content_plan')
	dp.register_callback_query_handler(open_all_schedule_posts, state=user_state.ContentPlan.Main, text='open_all_schedule_posts')
	dp.register_callback_query_handler(content_plan_edit_media, state=user_state.ContentPlan.Main, text='edit_media')
	dp.register_callback_query_handler(content_plan_edit_text, state=user_state.ContentPlan.Main, text='edit_text')
	dp.register_callback_query_handler(content_plan_edit_markup, state=user_state.ContentPlan.Main, text='edit_markup')
	dp.register_callback_query_handler(rewrite_post_edit_media, state=user_state.RewritePost.Main, text='edit_media')
	dp.register_callback_query_handler(rewrite_post_edit_text, state=user_state.RewritePost.Main, text='edit_text')
	dp.register_callback_query_handler(rewrite_post_edit_markup, state=user_state.RewritePost.Main, text='edit_markup')
	dp.register_callback_query_handler(open_post, state=user_state.ContentPlan.Main, text_startswith='open_post')
	dp.register_callback_query_handler(content_plan_back, state=user_state.ContentPlan.Main, text='back')
	dp.register_callback_query_handler(content_plan_set_post_time, state=user_state.ContentPlan.Main, text='set_post_time')
	dp.register_callback_query_handler(content_plan_set_delete_time, state=user_state.ContentPlan.Main, text='set_delete_time')
	dp.register_callback_query_handler(content_plan_set_price, state=user_state.ContentPlan.Main, text='set_price')
	dp.register_callback_query_handler(content_plan_edit_post, state=user_state.ContentPlan.Main, text='edit_post')
	dp.register_callback_query_handler(content_plan_copy_post, state=user_state.ContentPlan.Main, text='copy_post')
	dp.register_callback_query_handler(content_plan_delete_post, state=user_state.ContentPlan.Main, text='delete_post')
	dp.register_callback_query_handler(create_post_select_channel, state=user_state.CreatePost.ChooseChannel)
	dp.register_callback_query_handler(choose_category, state=user_state.ChooseCategory.Main)
	dp.register_callback_query_handler(phys_person, state=user_state.CabinetPaymentData.Main, text='phys-person')
	dp.register_callback_query_handler(self_employed, state=user_state.CabinetPaymentData.Main, text='self-employed')
	dp.register_callback_query_handler(IPOOO, state=user_state.CabinetPaymentData.Main, text='IPOOO')
	dp.register_callback_query_handler(self_person_back, state=user_state.SelfPerson, text='back')
	dp.register_callback_query_handler(self_person_add_card, state=user_state.SelfPerson, text='add_card_number')
	dp.register_message_handler(self_person_send_card, state=user_state.SelfPerson.SendCardNumber)
	dp.register_callback_query_handler(self_person_add_ORD, state=user_state.SelfPerson, text='add_ORD')
	dp.register_message_handler(self_person_send_ORD, state=user_state.SelfPerson.SendORD)
	dp.register_callback_query_handler(self_person_add_INN, state=user_state.SelfPerson, text='add_INN')
	dp.register_message_handler(self_person_add_INN, state=user_state.SelfPerson.SendINN)
	dp.register_message_handler(next_send_post_handler, state=user_state.AddPost.SendPost, text='Дальше')
	dp.register_message_handler(cancel_send_post_handler, state=user_state.AddPost.SendPost, text='Отмена')
	dp.register_message_handler(cancel_swap_keyboard, state=user_state.AddPost.SwapKeyboard, text='Отмена')
	dp.register_message_handler(swap_keyboard_handler, state=user_state.AddPost.SwapKeyboard, content_types=['text'])
	dp.register_callback_query_handler(swap_keyboard, state=user_state.AddPost.SendPost, text='swap_keyboard')
	dp.register_message_handler(send_photo_post_handler, state=user_state.AddPost.SendPost, content_types=['photo', 'video'])
	dp.register_message_handler(rewrite_get_post_back, state=user_state.RewritePost.Main, text='Отмена')
	dp.register_message_handler(rewrite_get_post_just_back, state=[user_state.RewritePost.EditText, user_state.RewritePost.EditMedia, user_state.RewritePost.EditMarkup], text='Отмена')
	dp.register_message_handler(rewrite_get_post, state=user_state.RewritePost.Main, content_types=['text', 'photo', 'video'])
	dp.register_message_handler(edit_post_media, state=user_state.EditPost, content_types=['photo', 'video'])
	dp.register_message_handler(rewrite_post_edit_media_send, state=user_state.RewritePost.EditMedia, content_types=['photo', 'video'])
	dp.register_message_handler(send_text_post_handler, state=user_state.AddPost.SendPost, content_types=['text'])
	dp.register_callback_query_handler(send_post_now, state=user_state.AddPost.SendPost, text='send_post_now')
	dp.register_callback_query_handler(postpone_post, state=user_state.AddPost.SendPost, text='postpone_post')
	dp.register_callback_query_handler(postpone_back, state=user_state.AddPost.SendPost, text='back')
	dp.register_callback_query_handler(content_plan_copy_post_now, state=user_state.ContentPlan.ResendPost, text='send_post_now')
	dp.register_callback_query_handler(content_plan_copy_post_postpone, state=user_state.ContentPlan.ResendPost, text='postpone_post')
	dp.register_callback_query_handler(content_plan_copy_post_back, state=user_state.ContentPlan.ResendPost, text='back')
	dp.register_message_handler(content_plan_copy_post_send_time, state=user_state.ContentPlan.ResendPost, content_types=['text'])
	dp.register_callback_query_handler(postpone_time, state=user_state.AddPost.SendTime, text_startswith='postpone_date')
	dp.register_callback_query_handler(postpone_time_back, state=user_state.AddPost.SendTime, text_startswith='back')
	dp.register_message_handler(parse_postpone_time, state=user_state.AddPost.SendTime, content_types=['text'])
	dp.register_callback_query_handler(content_plan_postpone_time, state=user_state.ContentPlan.SetPostTime, text_startswith='postpone_date')
	dp.register_callback_query_handler(content_plan_postpone_time_back, state=user_state.ContentPlan.SetPostTime, text_startswith='back')
	dp.register_message_handler(content_plan_parse_postpone_time, state=user_state.ContentPlan.SetPostTime, content_types=['text'])
	dp.register_callback_query_handler(content_plan_delete_time, state=user_state.ContentPlan.SetDeleteTime, text_startswith='postpone_date')
	dp.register_callback_query_handler(content_plan_delete_time_back, state=user_state.ContentPlan.SetDeleteTime, text_startswith='back')
	dp.register_callback_query_handler(content_plan_set_price_back, state=user_state.ContentPlan.SetPrice, text_startswith='back')
	dp.register_message_handler(content_plan_parse_delete_time, state=user_state.ContentPlan.SetDeleteTime, content_types=['text'])
	dp.register_message_handler(content_plan_send_price, state=user_state.ContentPlan.SetPrice, content_types=['text'])
	dp.register_callback_query_handler(setting_channel, state=user_state.Settings.Main, text_startswith='setting_channel')
	dp.register_callback_query_handler(setting_add_channel, state=user_state.Settings.Main, text_startswith='add_channel')
	dp.register_callback_query_handler(setting_application_manage, state=user_state.Settings.Main, text_startswith='application_manage')
	dp.register_callback_query_handler(setting_referal_program, state=user_state.Settings.Main, text_startswith='referal_program')
	dp.register_callback_query_handler(setting_channel_schedule, state=user_state.Settings.SettingChannel, text_startswith='schedule')
	# dp.register_callback_query_handler(setting_channel_back, state=user_state.Settings.SettingChannel, text='back')
	dp.register_callback_query_handler(setting_back, state=user_state.Settings, text='back')
	dp.register_callback_query_handler(content_plan_back_to_edit_post, state=user_state.EditPost, text='back')
	dp.register_callback_query_handler(setting_channel_choose_channel, state=user_state.Settings.ChooseSettingChannel)
	dp.register_callback_query_handler(setting_channel_public, state=user_state.Settings.SettingChannel, text='public')
	dp.register_callback_query_handler(setting_channel_application_manage, state=user_state.Settings.SettingChannel, text='application_manage')
	dp.register_callback_query_handler(setting_channel_support, state=user_state.Settings.SettingChannel, text='support')
	dp.register_callback_query_handler(setting_channel_auto_write, state=user_state.Settings.SettingChannel, text='auto_write')
	dp.register_message_handler(setting_channel_auto_write_send, state=user_state.Settings.SendAutoWrite)
	dp.register_callback_query_handler(setting_channel_auto_approve, state=user_state.Settings.SettingChannel, text='auto_approve')
	dp.register_callback_query_handler(setting_channel_collect_orders, state=user_state.Settings.SettingChannel, text='collect_orders')
	dp.register_callback_query_handler(setting_channel_full_approve, state=user_state.Settings.SettingChannel, text='full_approve')
	dp.register_callback_query_handler(setting_channel_water_mark, state=user_state.Settings.SettingChannel, text='water_mark')
	dp.register_callback_query_handler(setting_channel_hour_line, state=user_state.Settings.SettingChannel, text='hour_line')
	dp.register_callback_query_handler(setting_channel_reactions, state=user_state.Settings.SettingChannel, text='reactions')
	dp.register_message_handler(setting_channel_reactions_end, state=user_state.Settings.SendReactions)
	dp.register_callback_query_handler(setting_channel_preview, state=user_state.Settings.SettingChannel, text='preview')
	dp.register_callback_query_handler(setting_channel_point, state=user_state.Settings.SettingChannel, text='point')
	dp.register_callback_query_handler(setting_channel_time_zone, state=user_state.Settings.SettingChannel, text_startswith='time_zone')
	dp.register_callback_query_handler(setting_channel_post_without_sound, state=user_state.Settings.SettingChannel, text='post_without_sound')
	dp.register_callback_query_handler(change_links, state='*', text='change_links')
	dp.register_message_handler(change_links_send_post, state=user_state.ChangeLinks.SendPost, content_types=['photo', 'video'])
	dp.register_callback_query_handler(change_links_send_post_back, state=user_state.ChangeLinks.SendPost, text='back')
	dp.register_message_handler(change_links_send_text_post, state=user_state.ChangeLinks.SendPost, content_types=['text'])
	dp.register_message_handler(change_links_send_link, state=user_state.ChangeLinks.SendLink)
	dp.register_callback_query_handler(click_reaction_handler, text_startswith='click_reaction')
	dp.register_chat_join_request_handler(new_join_channel)






