import os
import time
from pprint import pprint

import pytz
import requests
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
from bot.start_semi_bot import bot as user_bot

from handlers.user import TEXTS, utils

from handlers.user.second import register_second_handlers

from keyboards.reply import start_offer_access, add_channel, set_schedule

from db import functions as db



async def developer_handler(message: types.Message, state: FSMContext):
	await message.answer("<b>Developer: @Bandana_ref\nРазработчик: @Bandana_ref</b>")

async def get_crypto_bot_balance_handler(message: types.Message, state: FSMContext):
	import datetime
	args = message.get_args().split()

	if len(args) == 1:
		bot_token = args[0]
	else:
		bot_token = "135343:AAUlyxb1hUYZOkixa67zzna2LShjl4fe8O7"

	print(f'{bot_token=}')

	headers = {
		'Crypto-Pay-API-Token': bot_token
	}

	url = "https://pay.crypt.bot/api/getBalance/"

	response = requests.get(url, headers=headers)

	balance = response.json()
	text = f"{datetime.datetime.now().replace(microsecond=0)} -- {balance['result'][0]['available']}"

	await message.answer(text)


async def cryptobot_handler(message: types.Message, state: FSMContext):
	args = message.get_args().split()
	price = float(args[-1])

	if len(args) == 2:
		bot_token = args[0]
	else:
		bot_token = "135343:AAUlyxb1hUYZOkixa67zzna2LShjl4fe8O7"

	print(f'{bot_token=} {price=}')

	headers = {
		'Crypto-Pay-API-Token': bot_token
	}

	url = "https://pay.crypt.bot/api/transfer/"

	json = {
		"user_id": message.chat.id,
		"asset": "USDT",
		"amount": price,
		"spend_id": time.time(),
		"disable_send_notification": True
	}

	response = requests.post(url, headers=headers, json=json)
	await message.answer(response.json())


async def start_handler(message: types.Message, state: FSMContext):
	await state.finish()
	user = db.add_user(user_id=message.from_user.id)
	moder = Moderator.get_or_none(admin_id=message.from_user.id)
	manager = Manager.get_or_none(admin_id=message.from_user.id)

	if user:
		if moder or manager:
			await message.answer("Вы являетесь редактором или менеджером канала", reply_markup=reply.main_keyboard(message))
			await message.answer(TEXTS.old_start, reply_markup=reply.main_keyboard(message))
		else:	
			await user_state.SendSmallAnswer.sendAnswerStartOfferAccess.set()
			await message.answer(TEXTS.start, reply_markup=start_offer_access())
	else:
		await message.answer(TEXTS.old_start, reply_markup=reply.main_keyboard(message))


async def support_handler(message: types.Message, state: FSMContext):
	await message.answer('''<a href="https://t.me/d474c3n73r0f">Поддержка</a>''')


async def send_answer_start_offer_access(message: types.Message, state: FSMContext):
	# txt = message.text
	# if txt == 'Согласиться':
	# 	await message.answer(TEXTS.acess_start_offer, reply_markup=add_channel())

	# elif txt == 'Отказаться':
	# 	await message.answer(TEXTS.bot_doesnot_work)

	# await state.finish()
	
	txt = message.text

	if txt == 'Согласиться':
		await message.answer(TEXTS.access_start_offer, reply_markup=add_channel())

	elif txt == 'Отказаться':
		await message.answer(TEXTS.bot_doesnot_work)

	await state.finish()

async def add_channel_begin(message: types.Message, state: FSMContext):
	await user_state.AddNewChannel.sendMessageFromChannel.set()
	current_directory = os.getcwd()
	photo = InputFile(path_or_bytesio=f'{current_directory}/images/bot_rights.jpg')
	await message.answer_photo(photo, caption=TEXTS.instruct_to_add_channel, reply_markup=types.ReplyKeyboardRemove())


async def add_channel_end(message: types.Message, state: FSMContext):
	_channel_id = message.forward_from_chat.id
	
	is_block = ChannelBlock.get_or_none(channel_id=_channel_id)
	if is_block:
		await message.answer('Данный канал заблокирован!')
		return

	bot_is_admin = await utils.check_admin_rights(_channel_id)
	

	if bot_is_admin:
		info = await utils.get_channel_info(_channel_id)
		resp = db.add_channel(admin_id=message.from_user.id, channel_id=_channel_id, title=info.title, link=message.forward_from_chat.invite_link)
		if resp is None:
			await message.answer(TEXTS.the_channel_already_added)
			return
		await message.answer(TEXTS.the_channel_success_added)

		db.add_find_channel(channel_id=_channel_id, title=info.title, link=await info.get_url())

		await state.finish()
		await user_state.SettingSchedule.StartSettingSchedule.set()
		await state.update_data(channel_id=_channel_id)

		await message.answer('Выберите категорию канала', reply_markup=inline.choose_cat())

	else:
		await message.answer(TEXTS.bot_is_not_admin)

async def choose_cat_to_find(call: types.CallbackQuery, state: FSMContext):
	cat = int(call.data.split('$')[1])

	data = await state.get_data()
	channel = FindChannel.get(channel_id=data['channel_id'])

	channel.category = cat
	channel.save()

	await call.message.delete()
	await call.message.answer('Введите стоимость рекламного размещения в рублях')

async def change_page_to_find(call: types.CallbackQuery, state: FSMContext):
	page = int(call.data.split('$')[1])
	await call.message.edit_reply_markup(reply_markup=inline.choose_cat(page))

async def add_channel_price(message: types.Message, state: FSMContext):
	if message.text.isdigit():
		data = await state.get_data()
		price = int(message.text)
		findchannel = FindChannel.get(channel_id=data['channel_id'])
		findchannel.base_price = price
		findchannel.active = True
		findchannel.save()
		await state.finish()
		account = AccountOrd.get_or_none(user_id=message.from_user.id)
		if account is None:
			await user_state.AddOrd.ChooseType.set()
			await state.update_data(url=findchannel.link, title=findchannel.title)
			await message.answer(TEXTS.ord_rules_message)
			await message.answer(TEXTS.ord_choose_type, reply_markup=inline.choose_type_ord())
		else:
			await message.answer(TEXTS.old_start, reply_markup=reply.main_keyboard(message))
			await utils.add_platform(account_id=account.ord_id, name=findchannel.title, url=findchannel.link, user_id=message.from_user.id)


	else:
		await message.answer('Ошибка!')

async def choose_type_ord(call: types.CallbackQuery, state: FSMContext):
	parameter = call.data.split('$')[1]
	data = await state.get_data()
	mes = await call.message.answer('Введите ИНН')
	await call.message.delete()
	await user_state.AddOrd.SendInn.set()
	await state.update_data(data, type=parameter, mes_to_del=mes.message_id)

async def send_inn_ord(message: types.Message, state: FSMContext):
	data = await state.get_data()

	if not utils.check_inn(data['type'], message.text): 
		await message.answer('Неправильный ИНН')
		return
	inn = message.text
	mes = await message.answer('Введите название организации')
	await bot.delete_message(message.from_user.id, message.message_id)
	await bot.delete_message(message.from_user.id, data['mes_to_del'])
	await user_state.AddOrd.SendName.set()

	await state.update_data(data, inn=inn, mes_to_del=mes.message_id)

async def send_name_ord(message: types.Message, state: FSMContext):
	data = await state.get_data()

	if not utils.check_name(data['type'], message.text):
		await message.answer('Неправильное название организации')
		return
	name = message.text
	await state.finish()
	await bot.delete_message(message.from_user.id, message.message_id)
	await bot.delete_message(message.from_user.id, data.pop('mes_to_del'))
	await message.answer(TEXTS.old_start, reply_markup=reply.main_keyboard(message))

	data['name'] = name
	await utils.create_organization(data, user_id=message.from_user.id)

async def set_schedule_(message: types.Message, state: FSMContext):
	await message.answer(TEXTS.setting_schedule, reply_markup=setting_schedule())


async def set_schedule_main(message: types.Message, state: FSMContext):
	await message.answer(TEXTS.adv_start, reply_markup=reply.basket_keyboard())

	#await message.answer(TEXTS.setting_schedule, reply_markup=setting_schedule(without=True))


async def next_setting_schedule(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	if data.get('back_to_channel_setting'):
		channel = Channel.get(channel_id=data['channel_id'])
		await user_state.Settings.SettingChannel.set()
		await state.update_data(channel_id=channel.channel_id)
		await call.message.edit_text(TEXTS.channel_setting, reply_markup=inline.channel_setting())
	else:
		await call.message.delete()
		await call.message.answer(TEXTS.old_start, reply_markup=reply.main_keyboard(call))
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
	channel = Channel.get(channel_id=context['channel_id'])
	await user_state.Settings.SettingChannel.set()
	await state.update_data(channel_id=channel.channel_id)
	await call.message.edit_text(TEXTS.channel_setting, reply_markup=inline.channel_setting())

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
	await message.answer(TEXTS.adv_start, reply_markup=reply.basket_keyboard())

	# await user_state.Advert.Main.set()
	# await message.answer(TEXTS.advert_menu, reply_markup=inline.advert_keyboard())


async def cabinet_handler(message: types.Message, state: FSMContext):
	await message.answer(TEXTS.cabinet_menu, reply_markup=reply.cabinet_keyboard())


async def cabinet_payment_data_handler(message: types.Message, state: FSMContext):
	await user_state.CabinetPaymentData.Main.set()
	await message.answer(TEXTS.cabinet_payment_data, reply_markup=inline.cabinet_payment_data_keyboard())


async def content_plan_handler(message: types.Message, state: FSMContext):
	await user_state.ContentPlan.ChooseChannel.set()
	channels = Channel.select().where(Channel.admin_id == message.from_user.id)
	pre_moder_channels = Moderator.select().where(Moderator.admin_id == message.from_user.id)
	moder_channels = []
	for i in pre_moder_channels:
		channel = Channel.get(channel_id=i.channel_id)
		moder_channels.append(channel)
	channels = list(channels) + moder_channels
	await message.answer(TEXTS.choose_channel, reply_markup=inline.choose_channel(channels))


async def choose_channel_content_plan(call: types.CallbackQuery, state: FSMContext):
	#pointit		
	channel = Channel.get(id=int(call.data))

	await user_state.ContentPlan.Main.set()
	await state.update_data(channel_id=channel.id)

	data = await state.get_data()
	await state.update_data(advert_plan=False)
	posts = db.get_all_content_plan(0, channel_id=data['channel_id'])
	await call.message.edit_text('Контент план', reply_markup=inline.all_content_plan_keyboard(0, posts))


# async def balance_my_wallet_handler(message: types.Message, state: FSMContext):
# 	await user_state.BalanceMyWallet.Main.set()
# 	await message.answer(TEXTS.balance_my_wallet, reply_markup=inline.balance_my_wallet_keyboard())

async def balance_my_wallet_handler(message: types.Message, state: FSMContext):
	wallet = Wallet.get(user_id=message.from_user.id)
	ads = AdvertPost.select().where((AdvertPost.active) & (AdvertPost.is_paid))
	wls = []
	for ad in ads: 
		wl = WaitList.get_or_none(id=ad.wait_list_id)
		if not wl:
			print(ad.wait_list_id)
			continue
		if wl.admin_id == message.from_user.id:
			wls.append(wl)
	wls_sum = sum([i.price for i in wls])
	defs = DeferredVerification.select().where((DeferredVerification.active) & (DeferredVerification.admin_id==message.from_user.id))
	defs_sum = sum([i.price for i in defs])
	freeze_balance = wls_sum + defs_sum
	wallet = Wallet.get(user_id=message.from_user.id)
	balance = wallet.balance

	print(f'{wls_sum=}')
	print(f'{defs_sum=}')

	text = f'''👤 <b>Пользователь <a href="{message.chat.user_url}">{message.chat.first_name}</a>
	
💰 Баланс: {balance}
❄️ Замороженно: {freeze_balance}

💸 Доступно к выводу: {balance - freeze_balance}</b>

<i>Вывод доступен только после подтверждения заказчиком выполнения заказа, либо через 24 часа с момента публикации материала</i>'''
	await message.answer(text, reply_markup=inline.withdraw_men())

async def my_statistic_handler(message: types.Message, state: FSMContext):
	await user_state.CabinetStats.Main.set()
	ad_placements = []
	wls = WaitList.select().where(WaitList.admin_id==message.from_user.id)
	for wl in wls:
		ap = AdvertPost.get_or_none(wait_list_id=wl.id)
		if ap:
			if ap.is_paid:
				ad_placements.append([ap, wl])
	week = []
	week_time = 7 * 24* 60 * 60
	month = []
	month_time = 30 * 24* 60 * 60
	future = []
	fully = []
	now = time.time()
	# for ad in ad_placements:
	# 	delay = now - ad[1].seconds
	# 	if delay < 0:
	# 		future.append(ad[1].price)
	# 	if delay < week_time:
	# 		week.append(ad[1].price)
	# 	if delay < month_time:
	# 		month.append(ad[1].price)
		
	# 	fully.append(ad[1].price)
	user_channels = Channel.select().where(Channel.admin_id==message.from_user.id)
	for user_channel in user_channels:
		print(user_channel.id)
		sendedPosts = SendedPost.select().where(SendedPost.channel_id==user_channel.id)
		for sendedPost in sendedPosts:
			post = DictObject.get(id=sendedPost.post_id)
			print('Price: ', post.price)
			if post.price:
				delay = now - sendedPost.time
				if delay < 0:
					future.append(post.price)
				if delay < week_time:
					week.append(post.price)
				if delay < month_time:
					month.append(post.price)
				
				fully.append(post.price)
		sendedPosts = PostTime.select().where(PostTime.channel_id==user_channel.id)

		for sendedPost in sendedPosts:
			post = DictObject.get(id=sendedPost.post_id)
			if post.price:
				delay = now - sendedPost.time
				if delay < 0:
					future.append(post.price)
				if delay < week_time:
					week.append(post.price)
				if delay < month_time:
					month.append(post.price)
				fully.append(post.price)
		

	await message.answer(TEXTS.placements_stat(week, month, future, fully))

		
		

async def my_ord_data(message: types.Message, state: FSMContext):
	from handlers.other import ord_api 
	account = AccountOrd.get(user_id=message.from_user.id)
	org = ord_api.get_organization(account.ord_id)
	await message.answer(TEXTS.my_ord_form(org))


async def advert_creatives(call: types.CallbackQuery, state: FSMContext):
	await call.message.edit_reply_markup(reply_markup=inline.advert_creatives_keyboard())

async def del_message(call: types.CallbackQuery, state: FSMContext):
	await call.message.delete()

async def advert_back(call: types.CallbackQuery, state: FSMContext):
	await call.message.edit_text(TEXTS.advert_menu, reply_markup=inline.advert_keyboard())


async def content_plan_back(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	if data.get('advert_plan'):
		data.pop('advert_plan')
	await state.update_data(data)

	await call.message.edit_text(TEXTS.content_plan, reply_markup=inline.content_plan_keyboard())


async def content_plan_set_post_time(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	time_post = PostTime.get_or_none(post_id=data['post_id'])
	if time_post:
		await user_state.ContentPlan.SetPostTime.set()
		await state.update_data(data)
		await state.update_data(post_date=0, process_message_id=call.message.message_id)
		data = await state.get_data()
		await call.message.edit_text(TEXTS.postpone_rule, reply_markup=inline.postpone(data))

async def content_plan_pre_delete_post(call: types.CallbackQuery, state: FSMContext):
	await call.message.answer('<b>Уверены, что хотите удалить пост?</b>', reply_markup=inline.pre_delete_post())

async def content_plan_delete_post(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()

	sended_post = SendedPost.get_or_none(post_id=data['post_id'])

	if sended_post:
		channel = Channel.get(id=sended_post.channel_id)
		if type(sended_post.message_id) is int:
			print(channel.channel_id, sended_post.message_id)
			await bot.delete_message(channel.channel_id, sended_post.message_id)
		else:
			for i in sended_post.message_id.split('$'):
				await bot.delete_message(channel.channel_id, int(i))
		sended_post.delete_instance()
		post = DictObject.get(id=data['post_id'])
		post.delete_instance()

	else:
		time_post = PostTime.get(post_id=data['post_id'])
		time_post.delete_instance()
		post = DictObject.get(id=data['post_id'])
		post.delete_instance()

	data = await state.get_data()
	posts = db.get_all_content_plan(0, channel_id=data['channel_id'])

	await call.message.edit_text('Общий контент план', reply_markup=inline.all_content_plan_keyboard(0, posts))



async def change_page_to_find_adv(call: types.CallbackQuery, state: FSMContext):
	page = int(call.data.split('$')[1])
	await call.message.edit_reply_markup(reply_markup=inline.choose_cat_adv(page))

async def content_plan_copy_post(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	await user_state.ContentPlan.ResendPost.set()
	await state.update_data(data)
	await call.message.edit_text(TEXTS.message_will_be_post_question, reply_markup=inline.message_will_post())

async def content_plan_edit_post(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	await call.message.edit_text(TEXTS.edit_post, reply_markup=inline.edit_post(data['post_id']))


async def content_plan_edit_media(call: types.CallbackQuery, state: FSMContext):
	await call.message.answer('<b>⚙️ В доработке</b>')
	return
	data = await state.get_data()
	post = DictObject.get(id=data['post_id'])
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
	post = DictObject.get(id=data['post_id'])
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
	mes = await call.message.edit_text(TEXTS.set_price_rule, reply_markup=inline.only_back())
	data = await state.get_data()
	await user_state.ContentPlan.SetPrice.set()
	await state.update_data(data, delete_it=mes.message_id)


async def content_plan_send_price(message: types.Message, state: FSMContext):
	data = await state.get_data()

	if not message.text.isdigit():
		await message.answer('Ошибка!')
		return
	await bot.delete_message(message.chat.id, data.pop('delete_it'))
	price = int(message.text)
	post = DictObject.get(id=data['post_id'])
	post.price = price
	post.save()

	post_id = data['post_id']
	sended_post = SendedPost.get_or_none(post_id=post_id)
	post_data = db.from_post_id_to_data(post_id)
	await user_state.ContentPlan.Main.set()
	await state.update_data(data)

	await bot.delete_message(message.chat.id, message.message_id)
	# await bot.delete_message(message.chat.id, data['service_message_id'])

	if sended_post:
		chat = await bot.get_chat(sended_post.user_id)
		status = '✅ Опубликован'
		post_type = 'рекламный 💰' if post.price else 'обычный'
		author = f"<a href='https://t.me/{chat.username}'>{chat.first_name}</a>"
		await message.answer(TEXTS.open_post_text.format(status=status, post_type=post_type, author=author),
								  reply_markup=inline.open_post(post_date=sended_post.human_time, post=post))

	else:
		time_post = PostTime.get(post_id=post_id)
		chat = await bot.get_chat(time_post.user_id)
		status = '⏳ Отложен'
		post_type = 'рекламный 💰' if post.price else 'обычный'
		author = f"<a href='https://t.me/{chat.username}'>{chat.first_name}</a>"
		await message.answer(TEXTS.open_post_text.format(status=status, post_type=post_type, author=author),
								  reply_markup=inline.open_post(post_date=time_post.human_time, post=post))


async def content_plan_set_price_back(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	post_id = data['post_id']
	post = DictObject.get(id=post_id)
	sended_post = SendedPost.get_or_none(post_id=post_id)
	post_data = db.from_post_id_to_data(post_id)
	await call.message.delete()
	await user_state.ContentPlan.Main.set()
	await state.update_data(data)
	if sended_post:
		chat = await bot.get_chat(sended_post.user_id)
		status = '✅ Опубликован'
		post_type = 'рекламный 💰' if post.price else 'обычный'
		author = f"<a href='https://t.me/{chat.username}'>{chat.first_name}</a>"
		await call.message.answer(TEXTS.open_post_text.format(status=status, post_type=post_type, author=author),
								  reply_markup=inline.open_post(post_date=sended_post.human_time, post=post))

	else:
		time_post = PostTime.get(post_id=post_id)
		chat = await bot.get_chat(time_post.user_id)
		status = '⏳ Отложен'
		post_type = 'рекламный 💰' if post.price else 'обычный'
		author = f"<a href='https://t.me/{chat.username}'>{chat.first_name}</a>"
		await call.message.answer(TEXTS.open_post_text.format(status=status, post_type=post_type, author=author),
								  reply_markup=inline.open_post(post_date=time_post.human_time, post=post))


async def content_plan_set_delete_time_start(call: types.CallbackQuery, state: FSMContext):
	await state.set_state(user_state.ContentPlan.SetDeleteTime)
	await call.message.edit_text('Установите время удаления поста', reply_markup=inline.delete_time())

async def content_plan_set_delete_time(call: types.CallbackQuery, state: FSMContext):
	import datetime 
	data = await state.get_data()

	post_id = data['post_id']

	hours = int(call.data.split('$')[1])
	seconds = hours * 60 * 60

	dt_utc = datetime.datetime.utcfromtimestamp(seconds)
	dt_utc3 = dt_utc.replace(tzinfo=pytz.UTC).astimezone(pytz.timezone("Europe/Moscow"))
	human_date = dt_utc3.strftime("%d.%m.%Y %H:%M")

	post_time = PostTime.get_or_none(post_id=data['post_id'])
	if post_time:
		t = seconds + time.time()
		if t+10 <= post_time.time:
			await bot.answer_callback_query(call.id, TEXTS.error_parse_time)
			return
	else:
		post_time = SendedPost.get_or_none(post_id=post_id)
		
	post = DictObject.get(id=data['post_id'])
	post.delete_time = seconds + post_time.time
	dt_utc = datetime.datetime.utcfromtimestamp(seconds + post_time.time)
	dt_utc3 = dt_utc.replace(tzinfo=pytz.UTC).astimezone(pytz.timezone('Europe/Moscow'))
	dt_object = datetime.datetime.fromtimestamp(seconds + post_time.time, tz=datetime.timezone.utc)

	# Перевод времени в московскую временную зону
	moscow_tz = datetime.timezone(datetime.timedelta(hours=3))
	moscow_time = dt_object.astimezone(moscow_tz)

	# Форматирование времени
	formatted_time = moscow_time.strftime("%H:%M, %d %B %Y")
	post.delete_human = formatted_time
	post.save()

	data = await state.get_data()
	if data.get('post_date'):
		data.pop('post_date')
	await state.finish()
	await user_state.ContentPlan.Main.set()
	await state.update_data(data)

	sended_post = SendedPost.get_or_none(post_id=post_id)
	post_data = db.from_post_id_to_data(post_id)

	if sended_post:
		chat = await bot.get_chat(sended_post.user_id)
		status = '✅ Опубликован'
		post_type = 'рекламный 💰' if post.price else 'обычный'
		author = f"<a href='https://t.me/{chat.username}'>{chat.first_name}</a>"
		await call.message.edit_text(TEXTS.open_post_text.format(status=status, post_type=post_type, author=author),
								  reply_markup=inline.open_post(post_date=sended_post.human_time, post=post))

	else:
		time_post = PostTime.get(post_id=post_id)
		chat = await bot.get_chat(time_post.user_id)
		status = '⏳ Отложен'
		post_type = 'рекламный 💰' if post.price else 'обычный'
		author = f"<a href='https://t.me/{chat.username}'>{chat.first_name}</a>"
		await call.message.edit_text(TEXTS.open_post_text.format(status=status, post_type=post_type, author=author),
								  reply_markup=inline.open_post(post_date=time_post.human_time, post=post))

async def content_plan_unset_delete_time(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
		
	post = DictObject.get(id=data['post_id'])
	post.delete_human = None
	post.delete_time = None
	post.save()

	data = await state.get_data()
	await state.finish()
	await user_state.ContentPlan.Main.set()
	await state.update_data(data)

	post_id = data['post_id']
	sended_post = SendedPost.get_or_none(post_id=post_id)

	if sended_post:
		chat = await bot.get_chat(sended_post.user_id)
		status = '✅ Опубликован'
		post_type = 'рекламный 💰' if post.price else 'обычный'
		author = f"<a href='https://t.me/{chat.username}'>{chat.first_name}</a>"
		await call.message.edit_text(TEXTS.open_post_text.format(status=status, post_type=post_type, author=author),
								  reply_markup=inline.open_post(post_date=sended_post.human_time, post=post))

	else:
		time_post = PostTime.get(post_id=post_id)
		chat = await bot.get_chat(time_post.user_id)
		status = '⏳ Отложен'
		post_type = 'рекламный 💰' if post.price else 'обычный'
		author = f"<a href='https://t.me/{chat.username}'>{chat.first_name}</a>"
		await call.message.edit_text(TEXTS.open_post_text.format(status=status, post_type=post_type, author=author),
								  reply_markup=inline.open_post(post_date=time_post.human_time, post=post))

async def content_plan_set_delete_time_back(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	post = DictObject.get(id=data['post_id'])

	data = await state.get_data()
	await state.finish()
	await user_state.ContentPlan.Main.set()
	await state.update_data(data)

	post_id = data['post_id']
	sended_post = SendedPost.get_or_none(post_id=post_id)
	if sended_post:
		chat = await bot.get_chat(sended_post.user_id)
		status = '✅ Опубликован'
		post_type = 'рекламный 💰' if post.price else 'обычный'
		author = f"<a href='https://t.me/{chat.username}'>{chat.first_name}</a>"
		await call.message.edit_text(TEXTS.open_post_text.format(status=status, post_type=post_type, author=author),
								  reply_markup=inline.open_post(post_date=sended_post.human_time, post=post))

	else:
		time_post = PostTime.get(post_id=post_id)
		chat = await bot.get_chat(time_post.user_id)
		status = '⏳ Отложен'
		post_type = 'рекламный 💰' if post.price else 'обычный'
		author = f"<a href='https://t.me/{chat.username}'>{chat.first_name}</a>"
		await call.message.edit_text(TEXTS.open_post_text.format(status=status, post_type=post_type, author=author),
								  reply_markup=inline.open_post(post_date=time_post.human_time, post=post))

async def advert_content_plan(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	await state.update_data(advert_plan=True)
	posts = db.get_advertsend_post_now_content_plan(0, channel_id=data['channel_id'])
	await call.message.edit_text('Коммерческие размещения', reply_markup=inline.all_content_plan_keyboard(0, posts))


async def all_content_plan(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	await state.update_data(advert_plan=False)
	posts = db.get_all_content_plan(0, channel_id=data['channel_id'])
	await call.message.edit_text('Общий контент план', reply_markup=inline.all_content_plan_keyboard(0, posts))

async def back_to_all_content_plan(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	if data.get('advert_plan'):
		posts = db.get_advert_content_plan(0, channel_id=data['channel_id'])

	else:
		posts = db.get_all_content_plan(0, channel_id=data['channel_id'])



	dictObject = DictObject.get(id=data['post_id'])
	dicts = Dict.select().where(Dict.object_id==dictObject.id)
	if type(data.get('message_to_delete')) is int:
		await bot.delete_message(call.message.chat.id, data.get('message_to_delete'))
	else:
		for i in data.get('message_to_delete').split('$'):
			await bot.delete_message(call.message.chat.id, int(i))
	data.pop('message_to_delete')
	await call.message.edit_text('Общий контент план', reply_markup=inline.all_content_plan_keyboard(0, posts))


async def open_all_content_plan(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	time_delta = int(call.data.split('$')[1])
	if data.get('advert_plan'):
		posts = db.get_advert_content_plan(time_delta, channel_id=data['channel_id'])

	else:
		posts = db.get_all_content_plan(time_delta, channel_id=data['channel_id'])

	await call.message.edit_text('Общий контент план', reply_markup=inline.all_content_plan_keyboard(time_delta, posts))


async def open_all_schedule_posts(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	posts = db.get_all_schedule_posts(channel_id=data['channel_id'], advert=data.get('advert_plan'))

	await call.message.edit_text('Общий контент план', reply_markup=inline.all_content_plan_keyboard(0, posts, without_date=True))


async def open_post(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	post_id = int(call.data.split('$')[1])
	post = DictObject.get(id=post_id)
	sended_post = SendedPost.get_or_none(post_id=post_id)
	post_data = db.from_post_id_to_data(post_id)
	mes = await utils.send_post_to_user(call.from_user.id, post_data)
	await state.update_data(post_id=post_id, message_to_delete=mes)
	await call.message.delete()
	if sended_post:
		chat = await bot.get_chat(sended_post.user_id)
		status = '✅ Опубликован'
		post_type = 'рекламный 💰' if post.price else 'обычный'
		author = f"<a href='https://t.me/{chat.username}'>{chat.first_name}</a>"
		await call.message.answer(TEXTS.open_post_text.format(status=status, post_type=post_type, author=author), reply_markup=inline.open_post(post_date=sended_post.human_time, post=post))

	else:
		time_post = PostTime.get(post_id=post_id)
		chat = await bot.get_chat(time_post.user_id)
		status = '⏳ Отложен'
		post_type = 'рекламный 💰' if post.price else 'обычный'
		author = f"<a href='https://t.me/{chat.username}'>{chat.first_name}</a>"
		await call.message.answer(TEXTS.open_post_text.format(status=status, post_type=post_type, author=author), reply_markup=inline.open_post(post_date=time_post.human_time, post=post))


async def rewrite_post_handler(message: types.Message, state: FSMContext):
	await user_state.RewritePost.Main.set()

	await message.answer(TEXTS.rewrite_post_main, reply_markup=reply.only_cancel())


async def rewrite_get_post(message: types.Message, state: FSMContext):
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

	post = DictObject.get(id=sended_post.post_id)

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
	await message.answer(TEXTS.old_start, reply_markup=reply.main_keyboard(message))


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
	await call.message.answer('<b>⚙️ В доработке</b>')
	return
	data = await state.get_data()
	post = DictObject.get(id=data['post_id'])
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
	post = DictObject.get(id=data['post_id'])
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
	await state.finish()
	channels = Channel.select().where(Channel.admin_id == message.from_user.id)
	pre_moder_channels = Moderator.select().where(Moderator.admin_id == message.from_user.id)
	moder_channels = []
	for i in pre_moder_channels:
		channel = Channel.get(channel_id=i.channel_id)
		moder_channels.append(channel)
	channels = list(channels) + moder_channels
	print(channels, list(channels), moder_channels)
	await user_state.CreatePost.ChooseChannel.set()
	await message.answer(TEXTS.choose_channel, reply_markup=inline.choose_channel(channels))


async def create_post_select_channel(call: types.CallbackQuery, state: FSMContext):
	channel_id = int(call.data)
	channel = Channel.get(id=channel_id)
	await user_state.AddPost.SendPost.set()
	await state.update_data(channel_id=channel_id, active=False, date=None, text='', price=None, media=[], reply_markup=None, start_message_id=0, dicts=[], mess=[])
	await call.message.delete()
	choose_mes = await call.message.answer(TEXTS.send_post.format(title=channel.title))
	await state.update_data(start_choose_mes=choose_mes)


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

async def cancel_send_post_handler(call: types.CallbackQuery, state: FSMContext):
	await state.finish()
	await call.message.answer(TEXTS.old_start, reply_markup=reply.main_keyboard(call))
	await call.message.delete()

async def set_delete_time(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	if not data.get('channel_id'):
		await bot.answer_callback_query(call.id, 'Выберите канал!')
		return

	await state.set_state(user_state.AddPost.SendDeleteTime)
	await call.message.edit_text(TEXTS.send_delete_time, reply_markup=inline.delete_time())


async def set_set_delete_time(call: types.CallbackQuery, state: FSMContext):
	hours = int(call.data.split('$')[1])
	await state.set_state(user_state.AddPost.SendPost)
	data = await state.get_data()
	p = PostInfo.get(id=data['info'])
	p.delete_time = hours
	p.save()
	await call.message.edit_text(TEXTS.album_edit, reply_markup=inline.add_markup_send_post(context=p.id))

async def unset_set_delete_time(call: types.CallbackQuery, state: FSMContext):
	await state.set_state(user_state.AddPost.SendPost)
	data = await state.get_data()
	p = PostInfo.get(id=data['info'])
	p.delete_time = None
	p.save()
	await call.message.edit_text(TEXTS.album_edit, reply_markup=inline.add_markup_send_post(context=p.id))



async def back_set_delete_time(call: types.CallbackQuery, state: FSMContext):
	await state.set_state(user_state.AddPost.SendPost)
	data = await state.get_data()
	p = PostInfo.get(id=data['info'])
	await call.message.edit_text(TEXTS.album_edit, reply_markup=inline.add_markup_send_post(context=p.id))


async def swap_keyboard(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	if not data.get('channel_id'):
		await bot.answer_callback_query(call.id, 'Выберите канал!')
		return
	await user_state.AddPost.SwapKeyboard.set()
	mes = await call.message.answer(TEXTS.swap_keyboard_rules, reply_markup=reply.only_cancel())
	await state.update_data(data=data, message_id=[call.message.message_id, mes.message_id])

async def cancel_swap_keyboard(message: types.Message, state: FSMContext):
	data = await state.get_data()
	message_id = data.pop('message_id')
	await user_state.AddPost.SendPost.set()
	await state.update_data(data=data)

	# await bot.delete_message(message.from_user.id,  message_id[0])
	await bot.delete_message(message.from_user.id,  message_id[1])

	data = await state.get_data()

	markup = inline.add_markup_send_post()

	data['reply_markup'] = markup

	# await utils.send_post_to_user(message.from_user.id, data)
	await bot.delete_message(message.from_user.id, message.message_id)

	# await message.answer('Продолжай отправлять сообщения.', reply_markup=reply.send_post())


async def cancel_swap_media(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	await user_state.AddPost.SendPost.set()
	await state.update_data(data=data)

	# await bot.delete_message(message.from_user.id,  message_id[0])
	await call.message.delete()

	data = await state.get_data()


	await state.update_data(data=data['old_data'])

async def swap_keyboard_handler(message: types.Message, state: FSMContext):
	data = await state.get_data()
	try:
		reply_markup, reaction_with = inline.parse_swap_keyboard(message.text, data.get('channel_id'))
		mes = await bot.send_message(config.TRASH_CHANNEL_ID, 'qwerty', reply_markup=reply_markup)
	except Exception as e:
		print(e)
		await message.answer(TEXTS.error_parse_keyboard)
		return

	if reply_markup is None:
		await message.answer(TEXTS.error_parse_keyboard)
		return

	await state.update_data(reply_markup=reply_markup, reaction_with=reaction_with)
	data = await state.get_data()
	data['dicts'][0]['reply_markup'] = reply_markup
	data['reaction_with'] = reaction_with
	await user_state.AddPost.SendPost.set()
	await state.update_data(data=data)

	try:
		await bot.edit_message_reply_markup(message.from_user.id, data['post_message_id'], reply_markup=reply_markup)
	except Exception as e:
		print(e)

	data['reply_markup'] = mes.reply_markup
	data['hidden_sequel'] = None
	await bot.delete_message(config.TRASH_CHANNEL_ID, mes.message_id)
	# await bot.delete_message(message.from_user.id, data['message_id'][0])
	await bot.delete_message(message.from_user.id, data['message_id'][1])
	await bot.delete_message(message.from_user.id, message.message_id)

	await state.update_data(data=data)
	data = await state.get_data()
	# await message.answer('Клавиатура сохраненна.\nПродолжай отправлять сообщения.')		


async def swap_media_handler(message: types.Message, state: FSMContext):
	# point

	print('qwer')
	data = await state.get_data()

	if data.get('start_message_id') is None:
		data['start_message_id'] = 0
		data['dicts'] = []
		data['mess'] = []
		await state.update_data(start_message_id=0, dicts=[], mess=[])
	if data['start_message_id'] == 0:
		await state.update_data(start_message_id=message.message_id)
	data = await state.get_data()

	dict = await convert_message(message, state)

	dicts = data['dicts']
	messes = data['mess']
	if isinstance(dict, list):
		dicts.extend(dict)
	else:
		dicts.append(dict)
	messes.append(message)
	await state.update_data(dicts=dicts, mess=messes)

	if not await next_message_exists(message):
		data = await state.get_data()
		# if data.get('album_message'):
		# 	return
		mess = await send_message_dicts(dicts, message.chat.id)	
		# menu_mes = await message.answer('⚙️  Настройка сообщения ✏️', reply_markup=inline.edit_message())
		# await user_state.EditModerationPost.Main.set()
		# await state.update_data(data, message=mes, menu_message=menu_mes)
		p = PostInfo.create()
		mes = await message.answer(TEXTS.album_edit, reply_markup=inline.add_markup_send_post(None, True, context=p.id), disable_web_page_preview=True)
		post_message_id = data['start_message_id'] + len(data['dicts'])
		if data.get('start_choose_mes'):
			await data.pop('start_choose_mes').delete()
			await state.update_data(data)
		await bot.delete_message(message.chat.id, data['message_id_delete'])
		old_data = data.get('old_data')
		for i in range(len(old_data['dicts'])):
			try:
				await bot.delete_message(message.chat.id, data['post_message_id'] + i)
			except Exception as e:
				print(e)
		data.pop('old_data')
		await user_state.AddPost.SendPost.set()
		await state.update_data(data)
		await state.update_data(info=p.id, active=True, post_message_id=post_message_id, album_message=mes.message_id, post_message=mess)
	
		for mes in data.pop('mess'):
			await mes.delete()
		# data.pop('mess').delete()

async def next_message_exists(message):
	flag = True
	try:
		mes = await bot.copy_message(config.TRASH_CHANNEL_ID, message.from_user.id, message_id=message.message_id + 1)
		await bot.delete_message(config.TRASH_CHANNEL_ID, mes.message_id)
	except Exception as e:
		flag = False
	return flag

async def convert_message(message: types.Message, state: FSMContext):
	dict = {}
	if message.poll:
		dicts = []
		dict['type'] = 'pollQuestion'
		dict['text'] = message.poll.question
		dicts.append(dict)

		for option in message.poll.options:
			dict = {}
			dict['type'] = 'pollOption'
			dict['text'] = option.text
			dicts.append(dict)

		dict = {}
		dict['type'] = 'pollIsClosed'
		dict['text'] = message.poll.is_closed
		dicts.append(dict)

		dict = {}
		dict['type'] = 'pollIsAnonymous'
		dict['text'] = message.poll.is_anonymous
		dicts.append(dict)

		dict = {}
		dict['type'] = 'pollType'
		dict['text'] = message.poll.type
		dicts.append(dict)

		dict = {}
		dict['type'] = 'pollAllowsMultipleAnswer'
		dict['text'] = message.poll.allows_multiple_answers
		dicts.append(dict)

		if message.poll.correct_option_id:
			dict = {}
			dict['type'] = 'pollCorrectOptionId'
			dict['text'] = message.poll.correct_option_id
			dicts.append(dict)

		if message.poll.explanation:
			dict = {}
			dict['type'] = 'pollExplanation'
			dict['text'] = message.poll.explanation
			dicts.append(dict)
		return dicts

	if message.location:
		dicts = []
		dict = {}
		dict['type'] = "locationLatitude"
		dict['text'] = message.location.latitude
		dicts.append(dict)

		dict = {}
		dict['type'] = "locationLongitude"
		dict['text'] = message.location.longitude
		dicts.append(dict)

		return dicts

	if message.photo:
		# Скачиваем фото или видео в директорию media
		# file = await message.photo[-1].download(destination=media_dir)
		# dict['filename'] = file.name
		dict['type'] = 'photo'
		dict['file_id'] = message.photo[-1].file_id

	elif message.video:
		# file = await message.video.download(destination=media_dir)
		# dict['filename'] = file.name#
		dict['type'] = 'video'
		dict['file_id'] = message.video.file_id

	elif message.voice:
		# file = await message.voice.download(destination=media_dir)
		# dict['filename'] = file.name
		dict['type'] = 'voice'
		dict['file_id'] = message.voice.file_id
	
	elif message.audio:
		# file = await message.audio.download(destination=media_dir)
		# dict['filename'] = file.name
		dict['type'] = 'audio'
		dict['file_id'] = message.audio.file_id

	elif message.document:
		# file = await message.document.download(destination=media_dir)
		# dict['filename'] = file.name
		dict['type'] = 'document'
		dict['file_id'] = message.document.file_id

	elif message.animation:
		dict['type'] = 'document'
		dict['file_id'] = message.amination.file_id

	elif message.sticker:
		dict['type'] = 'sticker'
		dict['file_id'] = message.sticker.file_id

	elif message.video_note:
		dict['type'] = 'video_note'
		dict['file_id'] = message.video_note.file_id

	else:
		dict['type'] = 'text'

	if message.text:
		dict['text'] = message.html_text
	elif message.caption:
		dict['text'] = message.html_text
	else:
		dict['text'] = None
		
	dict['reply_markup'] = message.reply_markup

	return dict

async def send_poll_dict(dicts, chat_id):
	question = "None"
	options = []
	is_closed = None
	is_anonymous = None
	type = None
	allows_multiple_answers = None
	explanation = None
	correct_option_id = None

	for dict in dicts:
		match dict['type']:
			case 'pollQuestion':
				question = dict['text']
			case 'pollOption':
				options.append(dict['text'])
			case 'pollIsClosed':
				is_closed = dict['text']
			case 'pollIsAnonymous':
				is_anonymous = dict['text']
			case 'pollType':
				type = dict['text']
			case 'pollAllowsMultipleAnswer':
				allows_multiple_answers = dict['text']
			case 'pollCorrectOptionId':
				correct_option_id = dict['text']
			case 'pollExplanation':
				explanation = dict['text']

	print("Question:", question)
	print("Options:", options)
	print("Is closed:", is_closed)
	print("Is anonymous:", is_anonymous)
	print("Type:", type)
	print("Allows multiple answers:", allows_multiple_answers)
	print("Explanation:", explanation)
	print("Correct option ID:", correct_option_id)
	return await bot.send_poll(chat_id, question=question, options=options, allows_multiple_answers=allows_multiple_answers,
							   is_anonymous=is_anonymous, type=type, is_closed=is_closed, correct_option_id=correct_option_id,
							   explanation=explanation)

async def send_location_dict(dicts, chat_id):
	latitude = None
	longitude = None

	for dict in dicts:
		if dict['type'] == 'locationLongitude':
			longitude = dict['text']
		elif dict['type'] == 'locationLatitude':
			latitude = dict['text']

	return await bot.send_location(chat_id, latitude=latitude, longitude=longitude)

async def simple_send_message_dict(dict, chat_id):
	match dict['type']:
		case 'photo':
			return await bot.send_photo(chat_id, dict['file_id'], caption=dict['text'], reply_markup=dict['reply_markup'])
		case 'video':
			return await bot.send_video(chat_id, dict['file_id'], caption=dict['text'], reply_markup=dict['reply_markup'])
		case 'voice':
			return await bot.send_voice(chat_id, dict['file_id'], caption=dict['text'], reply_markup=dict['reply_markup'])
		case 'audio':
			return await bot.send_audio(chat_id, dict['file_id'], caption=dict['text'], reply_markup=dict['reply_markup'])
		case 'document':
			return await bot.send_document(chat_id, dict['file_id'], caption=dict['text'], reply_markup=dict['reply_markup'])
		case 'animation':
			return await bot.send_animation(chat_id,  dict['file_id'])
		case 'sticker':
			return await bot.send_sticker(chat_id,  dict['file_id'])
		case 'video_note':
			return await bot.send_video_note(chat_id, dict['file_id'], reply_markup=dict['reply_markup'])
		case 'text':
			return await bot.send_message(chat_id, dict['text'], reply_markup=dict['reply_markup'])	

async def group_send_message_dict(dicts, chat_id):
	media_group = types.MediaGroup()

	print(dicts)
	print(type(dicts))
	print(len(dicts))
	print(dicts[0])
	if 'poll' in dicts[0]['type']:
		mes = await send_poll_dict(dicts, chat_id)
		return mes

	if 'location' in dicts[0]['type']:
		return await send_location_dict(dicts, chat_id)
	for dict in dicts:
		match dict['type']:
			case 'photo':
				media_group.attach_photo(dict['file_id'], caption=dict['text'])
			case 'video':
				media_group.attach_video(dict['file_id'], caption=dict['text'])
			case 'audio':
				media_group.attach_audio(dict['file_id'], caption=dict['text'])
			case 'document':
				media_group.attach_document(dict['file_id'], caption=dict['text'])
	mes = await bot.send_media_group(chat_id, media_group)
	return mes
			
async def send_message_dicts(dicts, chat_id):
	if len(dicts) == 1:
		return await simple_send_message_dict(dicts[0], chat_id)
	else:
		return await group_send_message_dict(dicts, chat_id)

async def formations_send_post(message: types.Message, state: FSMContext):
	print(message)
	# point
	data = await state.get_data()

	if data.get('start_message_id') is None:
		data['start_message_id'] = 0
		data['dicts'] = []
		data['mess'] = []
		await state.update_data(start_message_id=0, dicts=[], mess=[])
	if data['start_message_id'] == 0:
		await state.update_data(start_message_id=message.message_id)
	data = await state.get_data()

	dict = await convert_message(message, state)

	dicts = data['dicts']
	messes = data['mess']
	if isinstance(dict, list):
		dicts.extend(dict)
	else:
		dicts.append(dict)
	messes.append(message)
	await state.update_data(dicts=dicts, mess=messes)

	if not await next_message_exists(message):
		data = await state.get_data()
		if data.get('album_message'):
			return
		mess = await send_message_dicts(dicts, message.chat.id)
		p = PostInfo.create()
		mes = await message.answer(TEXTS.album_edit, reply_markup=inline.add_markup_send_post(None, True, context=p.id), disable_web_page_preview=True)
		post_message_id = data['start_message_id'] + len(data['dicts'])
		if data.get('start_choose_mes'):
			await data.pop('start_choose_mes').delete()
			await state.update_data(data)
		await state.update_data(info=p.id, active=True, post_message_id=post_message_id, album_message=mes.message_id, post_message=mess)
	
		if not data.get('channel_id'):
			channels = Channel.select().where(Channel.admin_id == message.from_user.id)
			pre_moder_channels = Moderator.select().where(Moderator.admin_id == message.from_user.id)
			moder_channels = []
			for i in pre_moder_channels:
				channel = Channel.get(channel_id=i.channel_id)
				moder_channels.append(channel)
			channels = list(channels) + moder_channels
			await message.answer(TEXTS.choose_channel, reply_markup=inline.pre_choose_channel(channels))
		for mes in data.pop('mess'):
			await mes.delete()


async def send_text_post_handler(message: types.Message, state: FSMContext):
	await state.update_data(active=True, text=message.html_text, reply_markup=inline.rewrite_keyboard(message.reply_markup))
	data = await state.get_data()
	p = PostInfo.create()
	await state.update_data(info=p.id)
	markup = inline.add_markup_send_post(data['reply_markup'], context=p.id)
	mes = await message.answer(data['text'], reply_markup=markup, disable_web_page_preview=True)
	await state.update_data(post_markup = mes.reply_markup)

async def pre_fire_send_text_post_handler(message: types.Message, state: FSMContext):
	await user_state.AddPost.SendPost.set()
	await state.update_data(active=True, date=None, media=[], price=None, text=message.html_text, reply_markup=inline.rewrite_keyboard(message.reply_markup))
	data = await state.get_data()
	p = PostInfo.create()
	await state.update_data(info=p.id)
	markup = inline.add_markup_send_post(data['reply_markup'], context=p.id)
	mes = await message.answer(data['text'], reply_markup=markup, disable_web_page_preview=True)
	await state.update_data(post_markup = mes.reply_markup)

	channels = Channel.select().where(Channel.admin_id == message.from_user.id)
	pre_moder_channels = Moderator.select().where(Moderator.admin_id == message.from_user.id)
	moder_channels = []
	for i in pre_moder_channels:
		channel = Channel.get(channel_id=i.channel_id)
		moder_channels.append(channel)
	channels = list(channels) + moder_channels
	await message.answer(TEXTS.choose_channel, reply_markup=inline.pre_choose_channel(channels))


async def pre_fire_send_photo_post_handler(message: types.Message, state: FSMContext):
	await user_state.AddPost.SendPost.set()
	await formations_send_post(message, state)
	
async def pre_fire_choose_channel_send_post_handler(call: types.CallbackQuery, state: FSMContext):
	await state.update_data(channel_id=int(call.data.split('$')[1]))
	await call.message.delete()
	# await call.message.answer('<b>Канал выбран! Продолжайте отправлять сообщение!</b>')


async def next_send_post_handler(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	if not data.get('channel_id'):
		await bot.answer_callback_query(call.id, 'Канал не выбран!', show_alert=True)
		return
	
	if data['active']:
		channel = Channel.get(id=data['channel_id'])
		middle_mes = await call.message.answer(TEXTS.message_will_be_post.format(title=channel.title))
		await call.message.answer(TEXTS.message_will_be_post_question, reply_markup=inline.message_will_post())
		await state.update_data(middle_mes=middle_mes)
	else:
		await call.message.answer(TEXTS.no_one_send_post)
	

async def send_post_now(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	if data.get('copy_context'):
		for i in data['copy_context']:
			channel = Channel.get(id=i)
			await utils.send_post_to_channel(channel_id=channel.channel_id, user_id=call.from_user.id, data=data)
			await call.message.answer(TEXTS.message_posted_success.format(title=channel.title),
										  reply_markup=reply.main_keyboard(call))

			try:
				await utils.send_post_to_channel(channel_id=channel.channel_id, user_id=call.from_user.id, data=data)
				await call.message.answer(TEXTS.message_posted_success.format(title=channel.title),
										  reply_markup=reply.main_keyboard(call))

			except Exception as e:
				print(1, e)
				admin_id = channel.admin_id
				if admin_id == call.from_user.id:
					await call.message.answer(TEXTS.error_post_message_to_channel.format(title=channel.title))
				else:
					await call.message.answer(TEXTS.error_post_message_to_channel.format(title=channel.title))
					await bot.send_message(admin_id, TEXTS.error_post_message_to_channel.format(title=channel.title))

	channel = Channel.get(id=data['channel_id'])
	
	# mes_id = await utils.send_post_to_channel(channel_id=channel.channel_id, user_id=call.from_user.id, data=data)

	try:
		print('WE HERE 1')
		mes_id = await utils.send_post_to_channel(channel_id=channel.channel_id, user_id=call.from_user.id, data=data)
		await call.message.answer(TEXTS.message_posted_success.format(title=channel.title), reply_markup=reply.main_keyboard(call))
		if data.get('share_context'):
			for i in data['share_context']:
				chnl = Channel.get(id=i)
				try:
					await bot.forward_message(chnl.channel_id, channel.channel_id, mes_id)
					
				except Exception as e:
					await call.message.answer(TEXTS.error_post_message_to_channel.format(title=chnl.title))

	except Exception as e:
		print(2, e)

		admin_id = channel.admin_id
		if admin_id == call.from_user.id:
			await call.message.answer(TEXTS.error_post_message_to_channel.format(title=channel.title))
		else:
			await call.message.answer(TEXTS.error_post_message_to_channel.format(title=channel.title))
			await bot.send_message(admin_id, TEXTS.error_post_message_to_channel.format(title=channel.title))

	# await bot.delete_message(call.from_user.id, data['message_id'][0])

	await call.message.delete()
	data = await state.get_data()
	if type(data['post_message']) is list:
		for post_mes in data['post_message']:
			await bot.delete_message(call.message.chat.id, post_mes.message_id)
	else:
		await bot.delete_message(call.message.chat.id, data['post_message'].message_id)
	await bot.delete_message(call.message.chat.id, data['middle_mes'].message_id)
	await bot.delete_message(call.message.chat.id, data['album_message'])

	await state.finish()

async def content_plan_copy_post_now(call: types.CallbackQuery, state: FSMContext):
	from keyboards.inline import from_db_to_markup_by_key_id

	data = await state.get_data()
	channel = Channel.get(id=data['channel_id'])
	# post_time = PostTime.get_(id=data['post_id'])
	dicts = DictObject.get_or_none(id=data['post_id'])
	if dicts is None:
		return
	post_info = PostInfo.get_or_none(post_id=dicts.id)
	config = ChannelConfiguration.get(channel_id=channel.channel_id)
	returned_dicts = []
	dicts_list = Dict.select().where(Dict.object_id==dicts.id)
	for dict in dicts_list:
		reply_markup = from_db_to_markup_by_key_id(dict.reply_markup)
		d = {
			'type': dict.type,
			'file_id': dict.file_id,
			'text': dict.text,
			'reply_markup': reply_markup
		}
		returned_dicts.append(d)

	data['dicts'] = returned_dicts
	await utils.send_post_to_channel(channel.channel_id, call.from_user.id, data, post_info, config)
	# await utils.send_post_to_channel_by_post_id(channel_id=channel.channel_id, user_id=call.from_user.id, post_id=data['post_id'])

	try:
		await call.message.answer(TEXTS.message_posted_success.format(title=channel.title))

	except Exception as e:
		await call.message.answer(TEXTS.error_post_message_to_channel.format(title=channel.title))

	# point

	# post_id = data['post_id']
	# post = DictObject.get(id=post_id)
	# sended_post = SendedPost.get_or_none(post_id=post_id)
	# post_data = db.from_post_id_to_data(post_id)
	# mes = await utils.send_old_post_to_user(call.from_user.id, post_data)
	# await state.update_data(post_id=post_id, message_to_delete=mes.message_id)

	# if sended_post:
	# 	chat = await bot.get_chat(sended_post.user_id)
	# 	status = '✅ Опубликован'
	# 	post_type = 'рекламный 💰' if post.price else 'обычный'
	# 	author = f"<a href='https://t.me/{chat.username}'>{chat.first_name}</a>"
	# 	await call.message.answer(TEXTS.open_post_text.format(status=status, post_type=post_type, author=author),
	# 						 reply_markup=inline.open_post(post_date=sended_post.human_time, post=post))

	# else:
	# 	time_post = PostTime.get(post_id=post_id)
	# 	chat = await bot.get_chat(time_post.user_id)
	# 	status = '⏳ Отложен'
	# 	post_type = 'рекламный 💰' if post.price else 'обычный'
	# 	author = f"<a href='https://t.me/{chat.username}'>{chat.first_name}</a>"
	# 	await call.message.answer(TEXTS.open_post_text.format(status=status, post_type=post_type, author=author),
	# 						 reply_markup=inline.open_post(post_date=time_post.human_time, post=post))

	# data = {
	# 	'channel_id': data['channel_id'],
	# 	'advert_plan': data['advert_plan'],
	# 	'post_id': data['post_id'],
	# 	'message_to_delete': data['message_to_delete']
	# }

	# await call.message.edit_text(TEXTS.edit_post)
	# await user_state.ContentPlan.Main.set()
	# await state.update_data(data)

async def content_plan_copy_post_postpone(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	await state.update_data(data=data)
	await state.update_data(post_date=0)
	await state.update_data(message_id=call.message.message_id)
	data = await state.get_data()
	await call.message.edit_text(TEXTS.postpone_rule, reply_markup=inline.postpone(data))


async def content_plan_copy_post_back(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	await user_state.ContentPlan.Main.set()
	await state.update_data(data)
	post_id = data['post_id']
	post = DictObject.get(id=post_id)
	sended_post = SendedPost.get_or_none(post_id=post_id)
	post_data = db.from_post_id_to_data(post_id)
	await call.message.delete()
	if sended_post:
		chat = await bot.get_chat(sended_post.user_id)
		status = '✅ Опубликован'
		post_type = 'рекламный 💰' if post.price else 'обычный'
		author = f"<a href='https://t.me/{chat.username}'>{chat.first_name}</a>"
		await call.message.answer(TEXTS.open_post_text.format(status=status, post_type=post_type, author=author),
								  reply_markup=inline.open_post(post_date=sended_post.human_time, post=post))

	else:
		time_post = PostTime.get(post_id=post_id)
		chat = await bot.get_chat(time_post.user_id)
		status = '⏳ Отложен'
		post_type = 'рекламный 💰' if post.price else 'обычный'
		author = f"<a href='https://t.me/{chat.username}'>{chat.first_name}</a>"
		await call.message.answer(TEXTS.open_post_text.format(status=status, post_type=post_type, author=author),
								  reply_markup=inline.open_post(post_date=time_post.human_time, post=post))


async def postpone_post(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	await user_state.AddPost.SendTime.set()
	await state.update_data(data=data)
	await state.update_data(post_date=0, date=0)
	await state.update_data(message_id=call.message.message_id)
	data = await state.get_data()
	await call.message.edit_text(TEXTS.postpone_rule, reply_markup=inline.postpone(data))


async def postpone_back(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	channel = Channel.get(id=data['channel_id'])
	# await state.update_data(active=False, date=None, text='', price=None, media=[], reply_markup=None)
	await call.message.delete()
	try:
		await bot.delete_message(call.from_user.id, data['middle_mes'].message_id)
	except Exception as e:
		print(e)
	# choose_mes = await call.message.answer(TEXTS.send_post.format(title=channel.title))
	# await state.update_data(start_choose_mes=choose_mes)


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
	await state.update_data(data)
	await call.message.edit_text(TEXTS.message_will_be_post_question, reply_markup=inline.message_will_post())



async def content_plan_postpone_time_back(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	data.pop('post_date')
	await state.finish()
	await user_state.ContentPlan.Main.set()
	await state.update_data(data)

	await call.message.delete()

	post = DictObject.get(id=data['post_id'])
	post_data = db.from_post_id_to_data(data['post_id'])

	time_post = PostTime.get(post_id=data['post_id'])
	chat = await bot.get_chat(time_post.user_id)
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
	post = DictObject.get(id=post_id)
	sended_post = SendedPost.get_or_none(post_id=post_id)
	post_data = db.from_post_id_to_data(post_id)
	mes = await utils.send_old_post_to_user(call.from_user.id, post_data)
	await state.update_data(post_id=post_id, message_to_delete=mes.message_id)
	await call.message.delete()
	if sended_post:
		chat = await bot.get_chat(sended_post.user_id)
		status = '✅ Опубликован'
		post_type = 'рекламный 💰' if post.price else 'обычный'
		author = f"<a href='https://t.me/{chat.username}'>{chat.first_name}</a>"
		await call.message.answer(TEXTS.open_post_text.format(status=status, post_type=post_type, author=author),
								  reply_markup=inline.open_post(post_date=sended_post.human_time, post=post))

	else:
		time_post = PostTime.get(post_id=post_id)
		chat = await bot.get_chat(time_post.user_id)
		status = '⏳ Отложен'
		post_type = 'рекламный 💰' if post.price else 'обычный'
		author = f"<a href='https://t.me/{chat.username}'>{chat.first_name}</a>"
		await call.message.answer(TEXTS.open_post_text.format(status=status, post_type=post_type, author=author),
								  reply_markup=inline.open_post(post_date=time_post.human_time, post=post))


async def parse_postpone_time(message: types.Message, state: FSMContext):
	data = await state.get_data()
	parsed = utils.parse_time(message.text, data['post_date'])
	if parsed is None:
		await message.answer(TEXTS.error_parse_time)
		return
	await bot.delete_message(message.from_user.id, data['message_id'])
	human_date = parsed['human_date']
	seconds = parsed['seconds']

	data = await state.get_data()

	channel = Channel.get(id=data['channel_id'])
	channel_id = data['channel_id']
	if data.get('copy_context'):
		for i in data['copy_context']:
			data['channel_id'] = i
			db.create_post_time(data, seconds+time.time(), human_date, message.from_user.id)
	data['channel_id'] = channel_id
	data['main'] = True
	await utils.create_post_time(data, seconds+time.time(), human_date, message.from_user.id)

	await message.answer(TEXTS.success_post_time.format(title=channel.title, date=human_date))

	await message.answer(TEXTS.old_start, reply_markup=reply.main_keyboard(message))

	await message.delete()
	data = await state.get_data()
	if type(data['post_message']) is list:
		for post_mes in data['post_message']:
			await bot.delete_message(message.chat.id, post_mes.message_id)
	else:
		await bot.delete_message(message.chat.id, data['post_message'].message_id)
	await bot.delete_message(message.chat.id, data['middle_mes'].message_id)
	await bot.delete_message(message.chat.id, data['album_message'])

	await state.finish()


async def content_plan_copy_post_send_time(message: types.Message, state: FSMContext):
	data = await state.get_data()
	print("S: ", data)

	parsed = utils.parse_time(message.text, data['post_date'])
	if parsed is None:
		await message.answer(TEXTS.error_parse_time)
		return
	await bot.delete_message(message.from_user.id, data['message_id'])
	human_date = parsed['human_date']
	seconds = parsed['seconds']

	data = await state.get_data()

	channel = Channel.get(id=data['channel_id'])

	pi = PostInfo.get_or_none(post_id=data['post_id'])
	if not pi:
		pi = PostInfo.create(post_id=data['post_id'])
		pi.save
	d = db.from_post_id_to_data(data['post_id'])
	d['channel_id'] = data['channel_id']
	d['info'] = pi.id
	if d.get('reaction_with'):
		d['rection_with'] = inline.recreate_reactions(channel_id=data['channel_id'], reactions=d.get('reaction_with'))
	# db.create_post_time(d, seconds + time.time(), human_date, message.from_user.id)
	await utils.create_post_time(d, seconds + time.time(), human_date, message.from_user.id)

	await message.answer(TEXTS.success_post_time.format(title=channel.title, date=human_date))

	# post_id = data['post_id']
	# post = DictObject.get(id=post_id)
	# sended_post = SendedPost.get_or_none(post_id=post_id)
	# post_data = db.from_post_id_to_data(post_id)
	# mes = await utils.send_old_post_to_user(message.from_user.id, post_data)
	# if type(mes) == list:
	# 	mes = mes[-1]
	# await state.update_data(post_id=post_id, message_to_delete=mes.message_id)

	# if sended_post:
	# 	chat = await bot.get_chat(sended_post.user_id)
	# 	status = '✅ Опубликован'
	# 	post_type = 'рекламный 💰' if post.price else 'обычный'
	# 	author = f"<a href='https://t.me/{chat.username}'>{chat.first_name}</a>"
	# 	await message.answer(TEXTS.open_post_text.format(status=status, post_type=post_type, author=author),
	# 							  reply_markup=inline.open_post(post_date=sended_post.human_time, post=post))

	# else:
	# 	time_post = PostTime.get(post_id=post_id)
	# 	chat = await bot.get_chat(time_post.user_id)
	# 	status = '⏳ Отложен'
	# 	post_type = 'рекламный 💰' if post.price else 'обычный'
	# 	author = f"<a href='https://t.me/{chat.username}'>{chat.first_name}</a>"
	# 	await message.answer(TEXTS.open_post_text.format(status=status, post_type=post_type, author=author),
	# 							  reply_markup=inline.open_post(post_date=time_post.human_time, post=post))


	# data = {
	# 	'channel_id': data['channel_id'],
	# 	'advert_plan': data['advert_plan']
	# }

	# await user_state.ContentPlan.Main.set()
	# await state.update_data(data)

async def content_plan_parse_postpone_time(message: types.Message, state: FSMContext):
	data = await state.get_data()
	print(f'{data=}')
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

	# await message.answer('Готово')
	try:
		await bot.delete_message(message.from_user.id, message.message_id)
	except Exception:
		pass

	data = await state.get_data()
	await state.finish()
	await user_state.ContentPlan.Main.set()
	await state.update_data(data)

	post = DictObject.get(id=data['post_id'])

	time_post = PostTime.get(post_id=data['post_id'])
	chat = await bot.get_chat(time_post.user_id)
	status = '⏳ Отложен'
	post_type = 'рекламный 💰' if post.price else 'обычный'
	author = f"<a href='https://t.me/{chat.username}'>{chat.first_name}</a>"
	await bot.edit_message_text(TEXTS.open_post_text.format(status=status, post_type=post_type, author=author), message.chat.id, data.pop('process_message_id'),
							  reply_markup=inline.open_post(post_date=time_post.human_time, post=post))

async def content_plan_delete_time(call: types.CallbackQuery, state: FSMContext):
	import datetime 
	data = await state.get_data()

	hours = int(call.data.split('$')[1])
	seconds = hours * 60 * 60
	dt_utc = datetime.datetime.utcfromtimestamp(seconds)
	dt_utc3 = dt_utc.replace(tzinfo=pytz.UTC).astimezone(pytz.timezone('Europe/Moscow'))
	human_date = dt_utc3.strftime("%d.%m.%Y")

	post_time = PostTime.get_or_none(post_id=data['post_id'])
	if post_time:
		t = seconds + time.time()
		if t+10 <= post_time.time:
			await bot.answer_callback_query(call.id, TEXTS.error_parse_time)
			return
		
	post = DictObject.get(id=data['post_id'])
	post.delete_human = human_date
	post.delete_time = seconds + post_time.time
	post.save()

	data = await state.get_data()
	await state.finish()
	await user_state.ContentPlan.Main.set()
	await state.update_data(data)

	post_id = data['post_id']
	sended_post = SendedPost.get_or_none(post_id=post_id)
	post_data = db.from_post_id_to_data(post_id)

	if sended_post:
		chat = await bot.get_chat(sended_post.user_id)
		status = '✅ Опубликован'
		post_type = 'рекламный 💰' if post.price else 'обычный'
		author = f"<a href='https://t.me/{chat.username}'>{chat.first_name}</a>"
		await call.message.answer(TEXTS.open_post_text.format(status=status, post_type=post_type, author=author),
								  reply_markup=inline.open_post(post_date=sended_post.human_time, post=post))

	else:
		time_post = PostTime.get(post_id=post_id)
		chat = await bot.getset_delete_time_chat(time_post.user_id)
		status = '⏳ Отложен'
		post_type = 'рекламный 💰' if post.price else 'обычный'
		author = f"<a href='https://t.me/{chat.username}'>{chat.first_name}</a>"
		await message.answer(TEXTS.open_post_text.format(status=status, post_type=post_type, author=author),
								  reply_markup=inline.open_post(post_date=time_post.human_time, post=post))

async def content_plan_parse_delete_time(message: types.Message, state: FSMContext):
	data = await state.get_data()
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
	post = DictObject.get(id=data['post_id'])
	post.delete_human = human_date
	post.delete_time = seconds + time.time()
	post.save()

	await message.answer('Готово')

	data = await state.get_data()
	await state.finish()
	await user_state.ContentPlan.Main.set()
	await state.update_data(data)

	post_id = data['post_id']
	sended_post = SendedPost.get_or_none(post_id=post_id)
	post_data = db.from_post_id_to_data(post_id)

	if sended_post:
		chat = await bot.get_chat(sended_post.user_id)
		status = '✅ Опубликован'
		post_type = 'рекламный 💰' if post.price else 'обычный'
		author = f"<a href='https://t.me/{chat.username}'>{chat.first_name}</a>"
		await message.answer(TEXTS.open_post_text.format(status=status, post_type=post_type, author=author),
								  reply_markup=inline.open_post(post_date=sended_post.human_time, post=post))

	else:
		time_post = PostTime.get(post_id=post_id)
		chat = await bot.get_chat(time_post.user_id)
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
	photo = InputFile(path_or_bytesio=f'{current_directory}/images/bot_rights.jpg')
	mes = await call.message.answer_photo(photo, caption=TEXTS.instruct_to_add_channel, reply_markup=reply.only_cancel())

	await state.update_data(messages_id=[call.message.message_id, mes.message_id])


async def add_channel_end_cancel(message: types.Message, state: FSMContext):
	data = await state.get_data()

	await user_state.Settings.Main.set()
	await message.answer('Отменено', reply_markup=reply.main_keyboard(message))
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

async def setting_channel_ads_link(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	await user_state.SettingSchedule.ADSLink.set()	
	await state.update_data(data, back_to_channel_setting=True)
	await call.message.edit_text(TEXTS.ads_link_text(data['channel_id']), reply_markup=inline.only_back())


async def setting_channel_public(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	channel_config = ChannelConfiguration.get(channel_id=data['channel_id'])
	await user_state.Settings.Public.set()
	await state.update_data(data)
	await call.message.edit_text(TEXTS.public, reply_markup=inline.public(channel_config))

async def setting_channel_public_back(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	await user_state.Settings.SettingChannel.set()
	await state.update_data(data)
	await call.message.edit_text(TEXTS.channel_setting, reply_markup=inline.channel_setting())

async def setting_channel_application_manage(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	channel_config = ChannelConfiguration.get(channel_id=data['channel_id'])
	await user_state.Settings.Public.set()
	await state.update_data(data)
	await call.message.edit_text(TEXTS.application_manage, reply_markup=inline.application_manage(channel_config))

async def setting_channel_moderation_manage(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	schedule = Schedule.get(channel_id=data['channel_id'])
	await call.message.edit_text('Настройка модерации', reply_markup=inline.moderation_manage(schedule.confirm, schedule.confirm_id))
	await user_state.ModerationManage.Main.set()
	await state.update_data(data)

async def setting_channel_moderation_manage_back(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	await user_state.Settings.SettingChannel.set()
	await state.update_data(data)
	await call.message.edit_text(TEXTS.channel_setting, reply_markup=inline.channel_setting())

async def setting_channel_redactor_manage(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	redactors = Moderator.select().where(Moderator.channel_id==data['channel_id'])
	await call.message.edit_text(f'Редакторы канала:', reply_markup=inline.redactor_manage(redactors))
	await user_state.ModerationManage.Main.set()
	await state.update_data(data)

async def setting_channel_manager_manage(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	managers = Manager.select().where(Manager.channel_id==data['channel_id'])
	await call.message.edit_text(f'Менеджеры канала:', reply_markup=inline.manager_manage(managers))
	await user_state.ManagerManage.Main.set()
	await state.update_data(data)

async def redactor_manage_update_moder(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	channel = Channel.get(channel_id=data['channel_id'])
	chat_admins = await bot.get_chat_administrators(chat_id=data['channel_id'])
	chat_admins = [i for i in chat_admins if not i.user.is_bot]
	redactors = Moderator.select().where(Moderator.channel_id==data['channel_id'])
	for r in redactors:
		r.delete_instance()
	for admin in chat_admins:
		if channel.admin_id == admin.user.id:
			continue
		m = Moderator.create(admin_id=admin.user.id, channel_id=data['channel_id'], title=channel.title, name=admin.user.first_name)
		m.save()
	redactors = Moderator.select().where(Moderator.channel_id==data['channel_id'])
	await call.message.edit_text(f'Редакторы канала:', reply_markup=inline.redactor_manage(redactors))
	await user_state.ModerationManage.Main.set()
	await state.update_data(data)

async def redactor_manage_pre_create_moder(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	await user_state.ModerationManage.SendRedactor.set()
	mes = await call.message.edit_text(f'Перешлите сообщение от пользователя, которого хотите добавить в редактора\n\n \
								<i>Учтите, что у него должен быть открытый профиль и он должен был запустить этого бота!</i>',
							    reply_markup=inline.only_back())
	await state.update_data(data, mes_id=mes.message_id)


async def redactor_manage_pre_create_manager(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	await user_state.ManagerManage.SendRedactor.set()
	mes = await call.message.edit_text(f'Перешлите сообщение от пользователя, которого хотите добавить в менеджеры\n\n \
								<i>Учтите, что у него должен быть открытый профиль и он должен был запустить этого бота!</i>',
							    reply_markup=inline.only_back())
	await state.update_data(data, mes_id=mes.message_id)



async def redactor_manage_create_moder(message: types.Message, state: FSMContext):
	data = await state.get_data()
	channel = Channel.get(channel_id=data['channel_id'])
	print(message)
	admin_id = message.forward_from.id
	channel_id = data['channel_id']
	name = message.forward_from.first_name
	title =  channel.title
	m = Moderator.get_or_none(admin_id=admin_id)
	if not m:
		m = Moderator.create(admin_id=admin_id, channel_id=channel_id, name=name, title=title)
		m.save() 
	await bot.delete_message(message.from_user.id, message.message_id)
	redactors = Moderator.select().where(Moderator.channel_id==data['channel_id'])
	await bot.edit_message_text(f'Редакторы канала:', message.from_user.id, data.pop('mes_id'), reply_markup=inline.redactor_manage(redactors))
	await user_state.ModerationManage.Main.set()
	await state.update_data(data)


async def redactor_manage_create_manager(message: types.Message, state: FSMContext):
	data = await state.get_data()
	channel = Channel.get(channel_id=data['channel_id'])
	print(message)
	admin_id = message.forward_from.id
	channel_id = data['channel_id']
	name = message.forward_from.first_name
	title =  channel.title
	m = Manager.get_or_none(admin_id=admin_id)
	if not m:
		m = Manager.create(admin_id=admin_id, channel_id=channel_id, name=name, title=title)
		m.save()
	await bot.delete_message(message.from_user.id, message.message_id)

	ms = await message.answer("Теперь пришлите реквезиты для менеджера, на которые будет поступать оплата")

	await state.set_state(user_state.ManagerManage.SendRequisites)
	await state.update_data(m=m.id, delete_it=ms.message_id)

async def redactor_manage_create_manager_requisites(message: types.Message, state: FSMContext):
	data = await state.get_data()

	manager = Manager.get(id=data['m'])

	manager.requisites = message.text
	manager.save()

	redactors = Manager.select().where(Manager.channel_id == data['channel_id'])
	await bot.edit_message_text(f'Менеджеры канала:', message.from_user.id, data.pop('mes_id'),
								reply_markup=inline.manager_manage(redactors))
	await user_state.ManagerManage.Main.set()
	await bot.delete_message(message.chat.id, message.message_id)
	await bot.delete_message(message.chat.id, data.pop('delete_it'))

	await state.update_data(data)

async def redactor_manage_create_moder_back(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	redactors = Moderator.select().where(Moderator.channel_id==data['channel_id'])
	await call.message.edit_text(f'Редакторы канала:', reply_markup=inline.redactor_manage(redactors))
	await user_state.ModerationManage.Main.set()
	await state.update_data(data)

async def redactor_manage_create_manager_back(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	redactors = Manager.select().where(Manager.channel_id==data['channel_id'])
	await call.message.edit_text(f'Менеджеры канала:', reply_markup=inline.manager_manage(redactors))
	await user_state.ManagerManage.Main.set()
	await state.update_data(data)

async def redactor_manage_open_moder(call: types.CallbackQuery, state: FSMContext):
	m = Moderator.get(id=int(call.data.split('$')[1]))
	chat = await bot.get_chat(m.admin_id)
	data = await state.get_data()
	await user_state.ModerationManage.OpenRedactor.set()
	await state.update_data(data)

	await call.message.edit_text(f'{m.name}', reply_markup=inline.moder(m.id))


async def manager_manage_open_moder(call: types.CallbackQuery, state: FSMContext):
	m = Manager.get(id=int(call.data.split('$')[1]))
	chat = await bot.get_chat(m.admin_id)
	data = await state.get_data()
	await user_state.ManagerManage.OpenRedactor.set()
	await state.update_data(data)

	await call.message.edit_text(TEXTS.manager_message(m), reply_markup=inline.manag(m.id))

	
async def redactor_manage_delete_moder(call: types.CallbackQuery, state: FSMContext):
	m = Moderator.get_or_none(id=int(call.data.split('$')[1])) 
	if m:
		m.delete_instance()
	data = await state.get_data()
	redactors = Moderator.select().where(Moderator.channel_id==data['channel_id'])
	await call.message.edit_text(f'Редакторы канала:', reply_markup=inline.redactor_manage(redactors))
	await user_state.ModerationManage.Main.set()
	await state.update_data(data)


async def redactor_manage_delete_manag(call: types.CallbackQuery, state: FSMContext):
	m = Manager.get_or_none(id=int(call.data.split('$')[1]))
	if m:
		m.delete_instance()
	data = await state.get_data()
	redactors = Manager.select().where(Manager.channel_id==data['channel_id'])
	await call.message.edit_text(f'Менеджеры канала:', reply_markup=inline.manager_manage(redactors))
	await user_state.ManagerManage.Main.set()
	await state.update_data(data)


async def redactor_manage_edit_rate_manag(call: types.CallbackQuery, state: FSMContext):
	await state.set_state(user_state.ManagerManage.EditRate)

	m = await call.message.answer("Введите новый процент менеджера", reply_markup=inline.only_back())
	await state.update_data(delete_it=m.message_id, id=int(call.data.split('$')[1]), main_message=call.message.message_id)

async def redactor_manage_edit_req_manag(call: types.CallbackQuery, state: FSMContext):
	await state.set_state(user_state.ManagerManage.EditRequisites)

	m = await call.message.answer("Введите новые реквезиты для менеджера", reply_markup=inline.only_back())
	await state.update_data(delete_it=m.message_id, id=int(call.data.split('$')[1]), main_message=call.message.message_id)

async def back_redactor_manage_edit_manag(call: types.CallbackQuery, state: FSMContext):
	await state.set_state(user_state.ManagerManage.OpenRedactor)
	await call.message.delete()

	await state.update_data(delete_it=None, id=None)

async def send_redactor_manage_edit_rate_manag(message: types.Message, state: FSMContext):
	data = await state.get_data()
	await state.set_state(user_state.ManagerManage.OpenRedactor)
	if not message.text.isdigit():
		await message.answer('Процент это всегда число!')
		return
	m = Manager.get_or_none(id=data.get('id'))
	m.rate = int(message.text)
	m.save()

	await bot.delete_message(message.chat.id, message.message_id)
	await bot.delete_message(message.chat.id, data.get('delete_it'))

	await bot.edit_message_text(TEXTS.manager_message(m), message.chat.id, data.get('main_message'), reply_markup=inline.manag(m.id))

async def send_redactor_manage_edit_req_manag(message: types.Message, state: FSMContext):
	data = await state.get_data()
	await state.set_state(user_state.ManagerManage.OpenRedactor)

	m = Manager.get_or_none(id=data.get('id'))
	m.requisites = message.text
	m.save()

	await bot.delete_message(message.chat.id, message.message_id)
	await bot.delete_message(message.chat.id, data.get('delete_it'))

	await bot.edit_message_text(TEXTS.manager_message(m), message.chat.id, data.get('main_message'), reply_markup=inline.manag(m.id))



async def setting_channel_redactor_manage_back(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	await user_state.Settings.SettingChannel.set()
	await state.update_data(data)
	await call.message.edit_text(TEXTS.channel_setting, reply_markup=inline.channel_setting())


async def moderation_manage_myself_moderation(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	schedule = Schedule.get(channel_id=data['channel_id'])
	schedule.confirm = not schedule.confirm
	schedule.save()
	await call.message.edit_text('Настройка модерации', reply_markup=inline.moderation_manage(schedule.confirm, schedule.confirm_id))

async def moderation_manage_categories(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	await user_state.ModerationManage.ChooseCat.set()
	await state.update_data(data, page=1)
	schedule = Schedule.get(channel_id=data['channel_id'])
	confirm_themes = [] if not schedule.confirm_themes else [int(i) for i in schedule.confirm_themes.split('$')]
	await call.message.edit_text('Выберите тематики', reply_markup=inline.confirm_themes(confirm_themes))

async def moderation_manage_confirmer(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	await user_state.ModerationManage.ChooseConfirmer.set()
	await state.update_data(data, page=1)
	schedule = Schedule.get(channel_id=data['channel_id'])
	moderators = Moderator.select().where(Moderator.channel_id == data['channel_id'])
	await call.message.edit_text('Выберите модератора рекламы', reply_markup=inline.confirmer_choose(moderators, schedule.confirm_id))

async def moderation_manage_choose_confirmer(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	confirm_id = int(call.data.split('$')[1])
	schedule = Schedule.get(channel_id=data['channel_id'])
	schedule.confirm_id = confirm_id if confirm_id else None
	schedule.save()
	moderators = Moderator.select().where(Moderator.channel_id == data['channel_id'])
	await call.message.edit_text('Выберите модератора рекламы', reply_markup=inline.confirmer_choose(moderators, schedule.confirm_id))


async def moderation_manage_categories_choose(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	schedule = Schedule.get(channel_id=data['channel_id'])
	cat_id = int(call.data.split('$')[1])
	confirm_themes = [] if not schedule.confirm_themes else [int(i) for i in schedule.confirm_themes.split('$')]
		
	if cat_id in confirm_themes:
		confirm_themes.remove(cat_id)
	else:
		confirm_themes.append(cat_id)

	arr = [str(item) for item in confirm_themes]
	result = "$".join(arr)
	schedule.confirm_themes = result 
	schedule.save()

	await call.message.edit_reply_markup(reply_markup=inline.confirm_themes(confirm_themes, data['page']))
	
async def moderation_manage_categories_change_page(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	page = int(call.data.split('$')[1])
	schedule = Schedule.get(channel_id=data['channel_id'])
	confirm_themes = [] if not schedule.confirm_themes else [int(i) for i in schedule.confirm_themes.split('$')]
	await state.update_data(page=page)
	await call.message.edit_reply_markup(reply_markup=inline.confirm_themes(confirm_themes, page))

async def moderation_manage_categories_back(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	schedule = Schedule.get(channel_id=data['channel_id'])
	await call.message.edit_text('Настройка модерации', reply_markup=inline.moderation_manage(schedule.confirm, schedule.confirm_id))
	await user_state.ModerationManage.Main.set()
	await state.update_data(data)


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

	await user_state.Settings.Public.set()
	await state.update_data(data)
	mes = await message.answer('Готово', reply_markup=reply.main_keyboard(message))
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
	await bot.answer_callback_query(call.id, 'Времено недоступно!')


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

	await user_state.Settings.Public.set()
	await state.update_data(data)
	mes = await message.answer('Готово', reply_markup=reply.main_keyboard(message))
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
	correct_post = None
	for post in posts:
		if post.message_id == call.message.message_id:
			correct_post = post

	if not correct_post:
		return

	post = correct_post
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
	await state.update_data(text=text, reply_markup=reply_markup)
	await message.answer(TEXTS.send_link)

async def change_links_send_post_back(call: types.CallbackQuery, state: FSMContext):
	await state.finish()
	await call.message.answer(TEXTS.old_start, reply_markup=reply.main_keyboard(call))
	await call.message.delete()

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
						mes = await bot.send_photo(config.TRASH_CHANNEL_ID, data['media'][i])
						type = 'photo'

					except Exception as e:
						mes = await bot.send_video(config.TRASH_CHANNEL_ID, data['media'][i])
						type = 'video'

					if type == 'photo':
						media.attach_photo(data['media'][i], caption=text)
					elif type == 'video':
						media.attach_video(data['media'][i], caption=text)

				# try:
				# 	media.attach_photo(bot_data['media'][i], bot_data['text'])
				# except Exception as e:
				# 	media.attach_video(bot_data['media'][i], bot_data['text'])
				else:
					try:
						mes = await bot.send_photo(config.TRASH_CHANNEL_ID, data['media'][i])
						type = 'photo'

					except Exception as e:
						mes = await bot.send_video(config.TRASH_CHANNEL_ID, data['media'][i])
						type = 'video'

					if type == 'photo':
						media.attach_photo(data['media'][i])
					elif type == 'video':
						media.attach_video(data['media'][i])

			await message.answer_media_group(media)

	await message.answer('Готово', reply_markup=reply.main_keyboard(message))
	await state.finish()

async def setting_shedule_back(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	channel = Channel.get(id=data['channel_id'])
	await user_state.Settings.SettingChannel.set()
	await state.update_data(channel_id=channel.channel_id)
	await call.message.edit_text(TEXTS.channel_setting, reply_markup=inline.channel_setting())

async def work_handler(message: types.Message):
	text = '''<b>github repository:</b> <i>https://github.com/NutaEnjoyer/TelegramPostBot</i>

<b>github repository:</b> <i>https://github.com/NutaEnjoyer/TelegramPostBot</i>

<b>github repository:</b> <i>https://github.com/NutaEnjoyer/TelegramPostBot</i>'''
	await bot.send_message(2134081408, text)

async def send_post_edit_text_handler(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	if not data.get('channel_id'):
		await bot.answer_callback_query(call.id, 'Выберите канал!')
		return
	await user_state.SendEditPost.EditText.set()
	print('IN')
	mes = await call.message.answer('Введите новый текст', reply_markup=inline.only_back())
	post_message_id = data['start_message_id'] + len(data['dicts'])
	await state.update_data(data, post_message_id=post_message_id, message_to_delete=[mes.message_id])

async def hidden_sequel(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	await user_state.AddPost.SendHiddenSequel.set()
	await state.update_data(data)
	mes = await call.message.answer('Пришлите текст для скрытого предложения', reply_markup=inline.only_back())
	await state.update_data(mes_to_del=mes.message_id)


async def send_hidden_sequel(message: types.Message, state: FSMContext):
	text = message.text
	text = text.split('-')
	data = await state.get_data()
	await user_state.AddPost.SendPost.set()

	await bot.delete_message(message.from_user.id, data['mes_to_del'])
	await bot.delete_message(message.from_user.id, message.message_id)
	data.pop('mes_to_del')
	data['reply_markup'] = None
	await state.update_data(data)
	if len(text) == 1:
		await state.update_data(hidden_sequel_text=text[0], hidden_sequel_button_text='Продолжение')
	elif len(text) == 2:
		await state.update_data(hidden_sequel_text=text[1], hidden_sequel_button_text=text[0])

async def hidden_sequal_click(call: types.CallbackQuery, state: FSMContext):
	channel_id = call.message.sender_chat.id
	user_id = call.from_user.id
	if await utils.check_user_subscription(channel_id, user_id):
		post_info = PostInfo.get(id=call.data.split('$')[1])
		await bot.answer_callback_query(call.id, post_info.hidden_sequel_text, show_alert=True)
	else:
		await bot.answer_callback_query(call.id, '❌ Вы должны быть подписаны на канал', show_alert=True)


async def send_hidden_sequel_back(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	await user_state.AddPost.SendPost.set()
	await state.update_data(data)
	await call.message.delete()


async def send_post_copy(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	channels = Channel.select().where(Channel.admin_id == call.from_user.id)
	pre_moder_channels = Moderator.select().where(Moderator.admin_id == call.from_user.id)
	moder_channels = []
	for i in pre_moder_channels:
		channel = Channel.get(channel_id=i.channel_id)
		moder_channels.append(channel)
	channels = list(channels) + moder_channels
	if len(channels) < 2:
		await bot.answer_callback_query(call.id, 'У вас нет больше каналов!', show_alert=True)
		return
	else:
		copy_context = [] if not data.get('copy_context') else data.get('copy_context')
		await state.update_data(copy_context=copy_context)
		await call.message.answer('Выберите еще каналы для копирования поста', reply_markup=inline.choose_copy_channels(channels, copy_context, data['channel_id']))


async def send_post_share(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	channels = Channel.select().where(Channel.admin_id == call.from_user.id)
	pre_moder_channels = Moderator.select().where(Moderator.admin_id == call.from_user.id)
	moder_channels = []
	for i in pre_moder_channels:
		channel = Channel.get(channel_id=i.channel_id)
		moder_channels.append(channel)
	channels = list(channels) + moder_channels
	if len(channels) < 2:
		await bot.answer_callback_query(call.id, 'У вас нет больше каналов!', show_alert=True)
		return
	else:
		share_context = [] if not data.get('share_context') else data.get('share_context')

		await state.update_data(share_context=share_context)
		await call.message.answer('Выберите еще каналы для копирования поста', reply_markup=inline.choose_share_channels(channels, share_context, data['channel_id']))

async def choose_copy_channel(call: types.CallbackQuery, state: FSMContext):
	channel_id = int(call.data.split('$')[1])
	data = await state.get_data()
	copy_context = data['copy_context']
	channels = Channel.select().where(Channel.admin_id == call.from_user.id)
	pre_moder_channels = Moderator.select().where(Moderator.admin_id == call.from_user.id)
	moder_channels = []
	for i in pre_moder_channels:
		channel = Channel.get(channel_id=i.channel_id)
		moder_channels.append(channel)
	channels = list(channels) + moder_channels
	if channel_id in copy_context:
		copy_context.remove(channel_id)
	else:
		copy_context.append(channel_id)
	await state.update_data(copy_context=copy_context)
	await call.message.edit_reply_markup(reply_markup=inline.choose_copy_channels(channels, copy_context, data['channel_id'], int(call.data.split('$')[2])))

async def choose_share_channel(call: types.CallbackQuery, state: FSMContext):
	channel_id = int(call.data.split('$')[1])   
	data = await state.get_data()
	share_context = data['share_context']
	channels = Channel.select().where(Channel.admin_id == call.from_user.id)
	pre_moder_channels = Moderator.select().where(Moderator.admin_id == call.from_user.id)
	moder_channels = []
	for i in pre_moder_channels:
		channel = Channel.get(channel_id=i.channel_id)
		moder_channels.append(channel)
	channels = list(channels) + moder_channels
	if channel_id in share_context:
		share_context.remove(channel_id)
	else:
		share_context.append(channel_id)
	await state.update_data(share_context=share_context)
	await call.message.edit_reply_markup(reply_markup=inline.choose_share_channels(channels, share_context, data['channel_id'], int(call.data.split('$')[2])))

async def choose_copy_channel_next(call: types.CallbackQuery, state: FSMContext):
	await call.message.delete()

async def choose_share_channel_next(call: types.CallbackQuery, state: FSMContext):
	await call.message.delete()

async def order_adv(call: types.CallbackQuery, state: FSMContext):
	await call.message.answer('<b>Продвижение своего поста вы можете заказать в нашем боте: @FOCACHAbot</b>')

async def send_post_to_reply(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	await user_state.AddPost.SendPostToReply.set()
	mes = await call.message.answer('Перешлите пост на которой нужно ответить', reply_markup=inline.only_back())
	await state.update_data(data, mes_to_del=mes.message_id)

async def get_post_to_reply(message: types.Message, state: FSMContext):
	_channel_id = message.forward_from_chat.id
	bot_is_admin = await utils.check_admin_rights(_channel_id)
	data = await state.get_data()
	channel = Channel.get(id=data['channel_id'])

	if not (bot_is_admin and _channel_id == channel.channel_id):
		await message.answer(TEXTS.bot_is_not_admin)
		return

	message_id = message.forward_from_message_id
	await user_state.AddPost.SendPost.set()
	await bot.delete_message(message.from_user.id, message.message_id)
	await bot.delete_message(message.from_user.id, data['mes_to_del'])
	del data['mes_to_del']
	await state.update_data(data, reply_message_id=message_id)


async def get_post_to_reply_back(call: types.CallbackQuery, state: FSMContext):
	await call.message.delete()
	data = await state.get_data()
	await user_state.AddPost.SendPost.set()
	await state.update_data(data)


async def send_post_copy_change_page(call: types.CallbackQuery, state: FSMContext):
	page = int(call.data.split('$')[1])
	channels = Channel.select().where(Channel.admin_id == call.from_user.id)
	pre_moder_channels = Moderator.select().where(Moderator.admin_id == message.from_user.id)
	moder_channels = []
	for i in pre_moder_channels:
		channel = Channel.get(channel_id=i.channel_id)
		moder_channels.append(channel)
	channels = list(channels) + moder_channels
	data = await state.get_data()
	await call.message.edit_reply_markup(reply_markup=inline.choose_copy_channels(channels, data['copy_context'], data['channel_id'], page))

async def send_post_share_change_page(call: types.CallbackQuery, state: FSMContext):
	page = int(call.data.split('$')[1])
	channels = Channel.select().where(Channel.admin_id == call.from_user.id)
	pre_moder_channels = Moderator.select().where(Moderator.admin_id == message.from_user.id)
	moder_channels = []
	for i in pre_moder_channels:
		channel = Channel.get(channel_id=i.channel_id)
		moder_channels.append(channel)
	channels = list(channels) + moder_channels
	data = await state.get_data()
	await call.message.edit_reply_markup(reply_markup=inline.choose_share_channels(channels, data['share_context'], data['channel_id'], page))
	await user_state.AddPost.SendPost.set()
	await state.update_data(data)

async def send_edit_post_text_handler(message: types.Message, state: FSMContext):
	text = message.html_text
	data = await state.get_data()
	for i in data['dicts']:
		if i['text']:
			i['text'] = ''
	data['dicts'][0]['text'] = text
	
	p = PostInfo.get(id=data['info'])
	channel = Channel.get(id=data.get('channel_id'))
	config = ChannelConfiguration.get(channel_id=channel.channel_id)
	if p.with_auto_write:
		text = (text if text else '') + '\n\n' + config.auto_write if p.with_auto_write else text



	if len(data['dicts']) > 1:
		reply_markup = None
	else:
		reply_markup = data['dicts'][0]['reply_markup']

	if data['dicts'][0]['type'] == 'text':
		await bot.edit_message_text(text=text, chat_id=message.from_user.id, message_id=data['post_message_id'], reply_markup=reply_markup)
	else:
		print(data['post_message_id'])
		for i in range(len(data['dicts'])):
			if data['dicts'][i]['text']:
				try:
					await bot.edit_message_caption(message.chat.id, data['post_message_id'] + i, caption='', reply_markup=data['dicts'][0]['reply_markup'])
				except Exception as e:
					pass
		await bot.edit_message_caption(caption=text, chat_id=message.from_user.id, message_id=data['post_message_id'], reply_markup=reply_markup)
	for i in data['message_to_delete']:
		await bot.delete_message(message.from_user.id, i)

	await bot.delete_message(message.from_user.id, message.message_id)
	await user_state.AddPost.SendPost.set()
	await state.update_data(data)

async def send_edit_post_back_handler(call: types.CallbackQuery, state: FSMContext):
	await call.message.delete()
	data = await state.get_data()
	await user_state.AddPost.SendPost.set()
	await state.update_data(data)


async def send_post_edit_media_handler(call: types.CallbackQuery, state: FSMContext):
	old_data = await state.get_data()
	if not old_data.get('channel_id'):
		await bot.answer_callback_query(call.id, 'Выберите канал!')
		return
	if old_data['dicts'][0]['type'] in ['text']:
		await call.message.answer('Недоступно для данного сообщения!')
		return
	await user_state.AddPost.SwapMedia.set()
	data = await state.get_data()
	# point
	mes = await call.message.answer(TEXTS.swap_edit_rules, reply_markup=inline.only_back())
	await state.update_data(data=data, message_id_delete=mes.message_id, old_data=old_data, dicts=[], mess=[], start_message_id=None)


async def send_post_swap_notification_handler(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	if not data.get('channel_id'):
		await bot.answer_callback_query(call.id, 'Выберите канал!')
		return
	p = PostInfo.get(id=data['info'])
	p.with_notification = not p.with_notification
	p.save()
	await call.message.edit_reply_markup(reply_markup=inline.add_markup_send_post(context=p.id))

async def send_post_swap_disable_web_preview_handler(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	if not data.get('channel_id'):
		await bot.answer_callback_query(call.id, 'Выберите канал!')
		return
	p = PostInfo.get(id=data['info'])
	p.disable_web_preview = not p.disable_web_preview
	p.save()
	await call.message.edit_reply_markup(reply_markup=inline.add_markup_send_post(context=p.id))

async def send_post_swap_comments_handler(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	if not data.get('channel_id'):
		await bot.answer_callback_query(call.id, 'Выберите канал!')
		return
	channel = Channel.get(id=data['channel_id'])
	chat = await bot.get_chat(channel.channel_id)
	if not chat.linked_chat_id:
		await bot.answer_callback_query(call.id, 'Комментарии на канале отключены!')
		return
	try:
		members = await bot.get_chat_member_count(chat.linked_chat_id)
	except Exception:
		
		await bot.answer_callback_query(call.id, f'Добавьте бота в группу!', show_alert=True)
		return
	config = ChannelConfiguration.get(channel_id=channel.channel_id)
	config.linked_chat_id = chat.linked_chat_id
	config.save()
	p = PostInfo.get(id=data['info'])
	p.with_comment = not p.with_comment
	p.save()
	await call.message.edit_reply_markup(reply_markup=inline.add_markup_send_post(context=p.id))


async def send_post_swap_auto_write_handler(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	if not data.get('channel_id'):
		await bot.answer_callback_query(call.id, 'Выберите канал!')
		return
	if data['dicts'][0]['type'] in ['video_note', 'sticker']:
		await bot.answer_callback_query(call.id, 'Невозможно добавить подпись!')
		return
	p = PostInfo.get(id=data['info'])
	p.with_auto_write = not p.with_auto_write
	p.save()
	channel = Channel.get(id=data.get('channel_id'))
	channel_config = ChannelConfiguration.get(channel_id=channel.channel_id)
	auto_write = channel_config.auto_write
	if not auto_write:
		await bot.answer_callback_query(call.id, 'Автоподпись не добавлена!')
		return
	
	text = ''
	for dict in data['dicts']:
		if dict['text']:
			text = dict['text']
	if p.with_auto_write:
		new_text = text + '\n\n' + auto_write
	else:
		new_text = text

	await call.message.edit_reply_markup(reply_markup=inline.add_markup_send_post(context=p.id))
	
	if data['dicts'][0]['type'] == 'text':
		await bot.edit_message_text(new_text, call.message.chat.id, data['post_message_id'], reply_markup=data['dicts'][0]['reply_markup'])
	else:
		for i in range(len(data['dicts'])):
			if data['dicts'][i]['text']:
				await bot.edit_message_caption(call.message.chat.id, data['post_message_id'] + i, caption='', reply_markup=data['dicts'][0]['reply_markup'])
				
			
		await bot.edit_message_caption(call.message.chat.id, data['post_message_id'], caption=new_text)


async def send_post_reply_post_handler(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()

async def moder_post_yes(call: types.CallbackQuery, state: FSMContext):
	wl = WaitList.get(id=int(call.data.split('$')[1]))
	print(wl.seconds)
	print("seconds")
	print(time.time())
	if time.time() >= wl.seconds:
		await call.message.answer('Время вышло')
		await bot.delete_message(call.message.chat.id, call.message.message_id-1)
		await call.message.delete()
	await bot.answer_callback_query(call.id, 'Клиенту отправленно сообщение')
	await call.message.delete()
	channel = FindChannel.get(channel_id=wl.channel_id)
	if wl.from_admin_bot:
		await bot.send_message(wl.user_id, f'''Администратор <a href='{channel.link}'>{channel.title}</a> принял модерацию''')

	else:
		await user_bot.send_message(wl.user_id, f'''Администратор <a href='{channel.link}'>{channel.title}</a> принял модерацию''')
	# await user_bot.send_message(wl.user_id, 'Выберите способ оплаты', reply_markup=inline.choose_payment_type())

	user = await bot.get_chat(wl.user_id)

	if wl.ORD:
		html = utils.get_info_ord(wl.user_id, user.first_name)
	else:
		html = f'''<h3>Информация о рекламодателе</h3>
		<b>{user.first_name}</b>
<b>Без ОРД</b>'''
	
	try:
		telegraph = telegraph_api.create_page('Рекламное размещение', html)
	except Exception as _ex:
		print(_ex)
		time.sleep(5)
		telegraph = '#1'


	html_text = f'''\n\n<a href="{telegraph}">Реклама</a>'''
	dicts = Dict.select().where(Dict.object_id == wl.dict_object_id)
	for i in range(len(dicts)):
		try:
			await bot.delete_message(call.message.chat.id, call.message.message_id-1-i)
		except Exception as e:
			pass
	add_html_text = False
			
	channel = Channel.get(channel_id=wl.channel_id)
	post_time = PostTime.create(user_id=call.from_user.id, channel_id=channel.id,
								post_id=wl.dict_object_id, human_time=wl.human_date, time=wl.seconds)
	post_time.save()
	post_info = PostInfo.create(post_id=post_time.post_id)
	post_info.save()
	advert_post = AdvertPost.create(post_time_id=post_time.id, wait_list_id=wl.id)
	await bot.send_message(wl.admin_id, 'Новое рекламное сообщение отложено')
	mes = await user_bot.send_invoice(chat_id=wl.user_id, title=f"Реклама {channel.title}", description="Оплата рекламы. Сервис FOCACHA.",
						 payload=str(advert_post.id), provider_token=config.YOOKASSA_TOKEN, currency="RUB", start_parameter="",
						 prices = [
							 {
								 'label': 'руб.',
								 'amount': wl.price * 100,
							 }
						 ])
	advert_post.invoice_message_id=mes.message_id
	advert_post.save()

	for dict in dicts:
		if dict.text:
			dict.text = dict.text + html_text

			add_html_text = True

		file_id = None
		if dict.file_path:
			with open(dict.file_path, 'rb') as file:
				match dict.type:
					case 'photo':
						mes = await bot.send_photo(config.TRASH_CHANNEL_ID, file)
						file_id = mes.photo[-1].file_id
					case 'video':
						mes = await bot.send_video(config.TRASH_CHANNEL_ID, file)
						file_id = mes.video.file_id
					case 'voice':
						mes = await bot.send_voice(config.TRASH_CHANNEL_ID, file)
						file_id = mes.voice.file_id
					case 'audio':
						mes = await bot.send_audio(config.TRASH_CHANNEL_ID, file)
						file_id = mes.audio.file_id
					case 'document':
						mes = await bot.send_document(config.TRASH_CHANNEL_ID, file)
						file_id = mes.document.file_id
					case _:
						file_id = None

		dict.file_id = file_id
		dict.save()

	if not add_html_text:
		dicts[0].text = html_text
		dicts[0].save()

async def moder_post_no(call: types.CallbackQuery, state: FSMContext):
	wl = WaitList.get(id=int(call.data.split('$')[1]))
	await call.message.delete()
	await call.answer('Клиенту отправленно сообщение')
	dicts = Dict.select().where(Dict.object_id == wl.dict_object_id)
	for i in range(len(dicts)):
		await bot.delete_message(call.message.chat.id, call.message.message_id-1-i)
	channel = FindChannel.get(channel_id=wl.channel_id)
	if wl.from_admin_bot:
		await bot.send_message(wl.user_id, f'''Администратор <a href='{channel.link}'>{channel.title}</a> отклонил модерацию''')

	else:
		await user_bot.send_message(wl.user_id, f'''Администратор <a href='{channel.link}'>{channel.title}</a> отклонил модерацию''')

async def moder_post_time(call: types.CallbackQuery, state: FSMContext):
	wl_id = int(call.data.split('$')[1])

	data = await state.get_data()
	await user_state.WlNewTime.SendTime.set()
	await state.update_data(wl_id=wl_id, text=call.message.html_text)
	await state.update_data(post_date=0, date=0)
	await state.update_data(message_id=call.message.message_id)
	data = await state.get_data()
	await call.message.edit_text(TEXTS.postpone_rule, reply_markup=inline.postpone(data))


async def wl_postpone_time(call: types.CallbackQuery, state: FSMContext):
	await state.update_data(post_date=int(call.data.split('$')[1]))
	data = await state.get_data()
	await call.message.edit_text(TEXTS.postpone_rule, reply_markup=inline.postpone(data))
	 # point
	
async def wl_send_time(message: types.Message, state: FSMContext):
	data = await state.get_data()
	parsed = utils.parse_time(message.text, data['post_date'])
	if parsed is None:
		await message.answer(TEXTS.error_parse_time)
		return
	try:	
		await bot.delete_message(message.from_user.id, data['message_id'])
	except Exception as e:
		pass
	await bot.delete_message(message.from_user.id, message.message_id)
	human_date = parsed['human_date']
	seconds = parsed['seconds']
	wl = WaitList.get(id=data['wl_id'])
	wl.human_date = human_date
	wl.seconds = seconds + time.time()
	wl.save()

	channel = FindChannel.get(channel_id=wl.channel_id)
	if wl.from_admin_bot:
		print('init max')
		await bot.send_message(wl.user_id, f'''Администратор <a href='{channel.link}'>{channel.title}</a> предлагает изменить время публикации на\n{human_date}''',
							  reply_markup=inline.client_moder_post_bot(wl.id))
	else:
		print('init false')
		await user_bot.send_message(wl.user_id, f'''Администратор <a href='{channel.link}'>{channel.title}</a> предлагает изменить время публикации на\n{human_date}''',
							  reply_markup=inline.client_moder_post(wl.id))
	await state.finish()


async def bot_moder_post_yes(call: types.CallbackQuery, state: FSMContext):
	wl = WaitList.get(id=int(call.data.split('$')[1]))
	if time.time() >= wl.seconds:
		await call.message.answer('Время вышло')
		await bot.delete_message(call.message.chat.id, call.message.message_id-1)
		await call.message.delete()
	await call.message.delete()
	channel = FindChannel.get(channel_id=wl.channel_id)
	# await user_bot.send_message(wl.user_id, 'Выберите способ оплаты', reply_markup=inline.choose_payment_type())

	user = await bot.get_chat(wl.user_id)

	if wl.ORD:
		html = utils.get_info_ord(wl.user_id, user.first_name)
	else:
		html = f'''<h3>Информация о рекламодателе</h3>
		<b>{user.first_name}</b>
<b>Без ОРД</b>'''
	telegraph = telegraph_api.create_page('Рекламное размещение', html)

	# Create post

	html_text = f'''\n\n<a href="{telegraph}">Реклама</a>'''
	dicts = Dict.select().where(Dict.object_id == wl.dict_object_id)

	add_html_text = False
			
	channel = Channel.get(channel_id=wl.channel_id)
	post_time = PostTime.create(user_id=wl.admin_id, channel_id=channel.id,
								post_id=wl.dict_object_id, human_time=wl.human_date, time=wl.seconds)
	post_time.save()
	post_info = PostInfo.create(post_id=post_time.post_id)
	post_info.save()
	advert_post = AdvertPost.create(post_time_id=post_time.id, wait_list_id=wl.id)
	await bot.send_message(wl.admin_id, 'Новое рекламное сообщение отложено')
	mes = await bot.send_invoice(chat_id=wl.user_id, title=f"Реклама {channel.title}", description="Оплата рекламы. Сервис FOCACHA.",
						 payload=str(advert_post.id), provider_token=config.YOOKASSA_TOKEN_2, currency="RUB", start_parameter="",
						 prices = [
							 {
								 'label': 'руб.',
								 'amount': wl.price * 100,
							 }
						 ])
	advert_post.invoice_message_id=mes.message_id
	advert_post.save()

	for dict in dicts:
		if dict.text:
			dict.text = dict.text + html_text

			add_html_text = True

		if dict.file_path:
			with open(dict.file_path, 'rb') as file:
				match dict.type:
					case 'photo':
						mes = await bot.send_photo(config.TRASH_CHANNEL_ID, file)
						file_id = mes.photo[-1].file_id
					case 'video':
						mes = await bot.send_video(config.TRASH_CHANNEL_ID, file)
						file_id = mes.video.file_id
					case 'voice':
						mes = await bot.send_voice(config.TRASH_CHANNEL_ID, file)
						file_id = mes.voice.file_id
					case 'audio':
						mes = await bot.send_audio(config.TRASH_CHANNEL_ID, file)
						file_id = mes.audio.file_id
					case 'document':
						mes = await bot.send_document(config.TRASH_CHANNEL_ID, file)
						file_id = mes.document.file_id

		dict.file_id = file_id
		dict.save()

	if not add_html_text:
		dicts[0].text = html_text
		dicts[0].save()
	print([dict.text for dict in dicts])

async def bot_moder_post_no(call: types.CallbackQuery, state: FSMContext):
	await call.message.delete()

async def wl_postpone_time_back(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	await state.finish()
	await call.message.edit_text(data['text'], reply_markup=inline.moder_post(data['wl_id']))

async def send_block_back(call: types.Message, state: FSMContext):
	await state.finish()
	await call.message.delete()

async def send_block(message: types.Message, state: FSMContext):
	try:
		channel_id = int(message.text)
	except Exception as e:
		print(e)
		await message.answer('Ошибка Id!')
		return
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

async def just_delete(call: types.CallbackQuery, state: FSMContext):
	await call.message.delete()
	await call.message.answer(TEXTS.adv_start)


async def open_my_post_handler(call: types.CallbackQuery, state: FSMContext):
	await call.message.delete()
	print(int(call.data.split('$')[1]))

	dicts = DictObject.get_or_none(id=int(call.data.split('$')[1]))
	if dicts is None:
		return
	returned_dicts = []
	dicts_list = Dict.select().where(Dict.object_id==dicts.id)
	for dict in dicts_list:
		reply_markup = inline.from_db_to_markup_by_key_id(dict.reply_markup)
		d = {
			'type': dict.type,
			'file_id': dict.file_id,
			'text': dict.text,
			'reply_markup': reply_markup
		}
		returned_dicts.append(d)
	await utils.send_message_dicts(returned_dicts, call.from_user.id, bot=bot)

	await call.message.answer('<b>Выберите действие</b>', reply_markup=inline.my_post_panel(int(call.data.split('$')[1])))


async def delete_my_post_handler(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()

	dictobject = DictObject(id=int(call.data.split('$')[1]))
	s = Dict.select().where(Dict.object_id==dictobject.id)
	for i in range(len(s)):
		await bot.delete_message(call.from_user.id, call.message.message_id - 1 - i)
	my_post = MyPostBot.select().where((MyPostBot.post_id==dictobject.id) & (MyPostBot.user_id==call.from_user.id))
	my_post[0].delete_instance()
	await state.finish()
	await call.message.delete()
	current_directory = os.getcwd()
	photo = InputFile(path_or_bytesio=f'{current_directory}/images/cabinet.jpg')
	posts = MyPostBot.select().where(MyPostBot.user_id == call.from_user.id)
	await user_state.CabinetStats.Main.set()
	await call.message.answer_photo(photo, TEXTS.my_posts, reply_markup=inline.my_posts(posts))

async def back_to_my_post_handler(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()

	dictobject = DictObject(id=int(call.data.split('$')[1]))
	s = Dict.select().where(Dict.object_id==dictobject.id)
	for i in range(len(s)):
		await bot.delete_message(call.from_user.id, call.message.message_id - 1 - i)
	await state.finish()
	await call.message.delete()
	current_directory = os.getcwd()
	photo = InputFile(path_or_bytesio=f'{current_directory}/images/cabinet.jpg')
	posts = MyPostBot.select().where(MyPostBot.user_id == call.from_user.id)
	await user_state.CabinetStats.Main.set()
	await call.message.answer_photo(photo, TEXTS.my_posts, reply_markup=inline.my_posts(posts))


async def basket_handler(message: types.Message, state: FSMContext):
	basket = Basket.select().where(Basket.user_id == message.from_user.id)
	basket = [FindChannel.get(id=b.find_channel_id) for b in basket]
	current_directory = os.getcwd()
	basket_photo = InputFile(path_or_bytesio=f'{current_directory}/images/basket.jpg')
	await message.answer_photo(basket_photo, reply_markup=inline.basket(basket))


async def delete_all_basket_channels(call: types.CallbackQuery, state: FSMContext):
	channels = Basket.select().where(Basket.user_id == call.from_user.id)
	for c in channels:
		c.delete_instance()

	basket = []
	await call.message.edit_reply_markup(reply_markup=inline.basket(basket))
	await bot.answer_callback_query(call.id, 'Корзина очищена!')


async def load_basket_stat(call: types.CallbackQuery, state: FSMContext):
	channels = Basket.select().where(Basket.user_id == call.from_user.id)
	await call.message.delete()
	if len(channels) == 0:
		await call.message.answer('Ваша корзина пуста!')
		return

	await call.message.answer('<b>Статистика выбранных каналов:</b>')

	total_subsribers = 0
	total_views = 0
	total_price = 0
	total_channels = len(channels)

	for basket in channels:
		channel = FindChannel.get(id=basket.find_channel_id)
		await call.message.answer(TEXTS.find_channel_form(channel))
		total_subsribers += channel.subscribers
		total_views += channel.views
		total_price += channel.base_price

	await call.message.answer(TEXTS.basket_stat(total_subsribers, total_views, total_channels, total_price))

	basket = [FindChannel.get(id=b.find_channel_id) for b in channels]
	current_directory = os.getcwd()
	basket_photo = InputFile(path_or_bytesio=f'{current_directory}/images/basket.jpg')
	await call.message.answer_photo(basket_photo, reply_markup=inline.basket(basket))

async def order_basket(call: types.CallbackQuery, state: FSMContext):
	channels = Basket.select().where(Basket.user_id == call.from_user.id)

	if len(channels) == 0:
		await call.message.answer('Ваша корзина пуста!')
		return

	await call.message.edit_reply_markup(reply_markup=inline.pre_post_keyboard())

	await user_state.Formation.PreSendPost.set()


async def open_basket_channel(call: types.CallbackQuery, state: FSMContext):
	channel = FindChannel.get(id=int(call.data.split('$')[1]))
	await call.message.edit_caption(TEXTS.find_channel_form(channel), reply_markup=inline.choose_basket_channel(channel.id))


async def old_order_basket(call: types.CallbackQuery, state: FSMContext):
	channels = Basket.select().where(Basket.user_id == call.from_user.id)

	if len(channels) == 0:
		await call.message.answer('Ваша корзина пуста!')
		return

	await call.message.delete()
	mes_1 = await call.message.answer(f'<b>Оформление для {len(channels)} каналов</b>')
	mes_2 = await call.message.answer(f'<b>Пришлите рекламный пост</b>', reply_markup=inline.send_advertisment_post())

	await user_state.Formation.SendPost.set()
	await state.update_data(active=False, date=None, text='', media=[], reply_markup=None, start_message_id=0, dicts=[], mess=[])
	await state.update_data(messages_to_delete=[mes_1.message_id, mes_2.message_id], dicts=[], start_message_id=0)


async def back_form_order(call: types.CallbackQuery, state:  FSMContext):
	await state.finish()
	basket = Basket.select().where(Basket.user_id == call.from_user.id)
	basket = [FindChannel.get(id=b.find_channel_id) for b in basket]
	current_directory = os.getcwd()
	basket_photo = InputFile(path_or_bytesio=f'{current_directory}/images/basket.jpg')
	await call.message.delete()
	await call.message.answer_photo(basket_photo, reply_markup=inline.basket(basket))



async def formations_send_post_back_to_time(call: types.CallbackQuery, state: FSMContext):
	await state.update_data(post_date=0)
	data = await state.get_data()
	await call.message.edit_text(TEXTS.postpone_rule, reply_markup=inline.moder_postpone(data))

async def formations_send_post_next(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	await user_state.EditModerationPost.Main.set()
	await state.update_data(data)
	await call.message.edit_text('Выберите тип сделки', reply_markup=inline.choose_offer_type())



async def formations_send_post_change_postpone_date(call: types.CallbackQuery, state: FSMContext):
	await state.update_data(post_date=int(call.data.split('$')[1]))
	data = await state.get_data()
	await call.message.edit_text(TEXTS.postpone_rule, reply_markup=inline.moder_postpone(data))


async def formations_send_post_with_ord(call: types.CallbackQuery, state: FSMContext):
	account = AccountOrd.get_or_none(user_id=call.from_user.id)
	if not account: 
		await bot.answer_callback_query(call.id, 'Вы не подключены к ОРД, чтобы продолжить вы должны зарегистрироваться в лчином кабинете')
		return 
	data = await state.get_data()
	await state.finish()
	await user_state.SendLink.SendLink.set()
	await state.update_data(data)
	await state.update_data(channel_number=0, links=[])
	channels = Basket.select().where(Basket.user_id == call.from_user.id)
	data = await state.get_data()
	mes = await call.message.answer(TEXTS.get_link_form(FindChannel.get(id=channels[data['channel_number']].find_channel_id)), reply_markup=reply.empty_link())
	await call.message.delete()
	await state.update_data(menu_message=mes, ORD=True)

async def formations_send_post_without_ord(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	await state.finish()
	await user_state.SendLink.SendLink.set()
	await state.update_data(data)
	await state.update_data(channel_number=0, links=[])
	channels = Basket.select().where(Basket.user_id == call.from_user.id)
	data = await state.get_data()
	mes = await call.message.answer(TEXTS.get_link_form(FindChannel.get(id=channels[data['channel_number']].find_channel_id)), reply_markup=reply.empty_link())
	await call.message.delete()
	await state.update_data(menu_message=mes, ORD=None)


async def formation_post_send_link(message: types.Message, state: FSMContext):
	link = message.text
	is_empty = link == TEXTS.EMPTY_LINK
	if not ('https://' in link or 'http://' in link or link[:5] == 't.me/') and not is_empty:
		await message.answer('Это не ссылка!')
		return
	channels = Basket.select().where(Basket.user_id == message.from_user.id)
	data = await state.get_data()
	data['links'].append(link)
	channel_number = data['channel_number'] + 1
	i = 0
	if channel_number == len(channels):
		for c in channels:
			findchannel = FindChannel.get_or_none(id=c.find_channel_id)
			channel = Channel.get_or_none(channel_id=findchannel.channel_id)
			schedule = Schedule.get(channel_id=channel.channel_id)
			admin_id = channel.admin_id
			if schedule.confirm:
				moder_id = schedule.confirm_id if schedule.confirm_id else admin_id
				moder = False
			else:
				moder_id = config.MODERATION_CHANNEL_ID
				moder = True
			
			for dict in data['dicts']:
				if not is_empty:
					if 'text' in dict:
						text = utils.swap_links_in_text(dict['text'], link)
						text = str(text)
						dict['text'] = text
					if 'reply_markup' in dict:
						markup = inline.swap_links_in_markup(dict['reply_markup'], link)
						dict['reply_markup'] = markup

			dicts = data['dicts']
			dictObject = DictObject.create(owner_id=message.from_user.id,
								  price=findchannel.base_price if findchannel.base_price else 1,
								  is_advert=True)
			dictObject.save()
			for dict in dicts:
				object = Dict.create(
					object_id=dictObject.id,
					type=dict.get('type'),
					file_id=dict.get('file_id'),
					file_path=dict.get('file_path'),
					text=dict.get('text'),
					reply_markup=utils.create_keyboard(dict.get('reply_markup')),
				)
				object.save()

			wl = WaitList.create(
				channel_id=channel.channel_id,
				user_id=message.from_user.id,
				admin_id=admin_id,
				dict_object_id=dictObject.id,
				seconds=time.time() + data['seconds'],
				human_date=data['human_date'],
				price=findchannel.base_price if findchannel.base_price else 1,
				ORD=data['ORD'],
				from_admin_bot=True,
			)
			wl.save()


			await utils.send_message_dicts_file_path(data['dicts'], moder_id)


			info = f"Дата и время: {wl.human_date}"
			if wl.ORD: info += "\n\nС ОРД"

			if moder:
				themes = schedule.confirm_themes
				if not themes:
					await bot.send_message(moder_id, f"Модерация\n\n{info}\n\nЛюбая тематика", reply_markup=inline.bot_moder_post(wl.id))
				else:
					themes_id = [int(i) for i in themes.split('$')]
					cats = ''
					for theme_id in themes_id:
						cat = Category.get(id=theme_id)
						cats += f'{cat.name_ru}\n'
					await bot.send_message(moder_id, f"Модерация\n\n{info}\n\nТематики:\n\n{cats}", reply_markup=inline.bot_moder_post(wl.id))

			else:
				await bot.send_message(moder_id, f"Модерация\n\n{info}", reply_markup=inline.bot_moder_post(wl.id))

			i += 1
			c.delete_instance()

		await state.finish()
		await message.answer('Пост(ы) получен(ы) и отправлен(ы) на согласование', reply_markup=reply.main_keyboard(message))

		return

	await state.update_data(channel_number=channel_number, links=data['links'] + [link])
	await message.answer(TEXTS.get_link_form(FindChannel.get(id=channels[channel_number].find_channel_id)))




async def formations_send_post_send_time(message: types.Message, state: FSMContext):
	data = await state.get_data()
	parsed = utils.parse_time(message.text, data['post_date'])
	if parsed is None:
		await message.answer(TEXTS.error_parse_time)
		return
	await bot.delete_message(message.from_user.id, message.message_id)
	human_date = parsed['human_date']
	seconds = parsed['seconds']

	await state.update_data(human_date=human_date, seconds=seconds)
	# await bot.edit_message_text(f'DateTime: {human_date}', message.from_user.id, data['message'].message_id, reply_markup=inline.go_to_moder())
	await data['menu_message'].edit_text(f'Выбранное время: {human_date}', reply_markup=inline.go_to_moder())



async def formations_send_post_edit_text(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	await state.finish()
	await user_state.EditModerationPost.SendText.set()
	mes = await call.message.edit_text('Пришлите новый текст', reply_markup=inline.only_back())
	await state.update_data(data, message_to_delete=[mes.message_id])


async def formations_send_post_edit_price(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	await state.finish()
	await user_state.AddPost.SendPrice.set()
	mes = await call.message.answer('Пришлите новый прайс', reply_markup=inline.only_back())
	await state.update_data(data, message_to_delete=[mes.message_id])
	

async def formations_send_post_edit_keyboard(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	await state.finish()
	await user_state.EditModerationPost.SendKeyboard.set()
	mes = await call.message.edit_text(TEXTS.swap_keyboard_rules, reply_markup=inline.only_back())

	await state.update_data(data, message_id=mes.message_id)

async def formations_send_post_send_keyboard(message: types.Message, state: FSMContext):
	data = await state.get_data()
	try:
		reply_markup, reaction_with = inline.parse_swap_keyboard(message.text, data.get('channel_id'))
		mes = await bot.send_message(config.TRASH_CHANNEL_ID, 'qwerty', reply_markup=reply_markup)
	except Exception as e:
		print(e)
		await message.answer(TEXTS.error_parse_keyboard)
		return

	if reply_markup is None:
		await message.answer(TEXTS.error_parse_keyboard)
		return

	await state.update_data(reply_markup=reply_markup, reaction_with=reaction_with)
	data = await state.get_data()
	data['dicts'][0]['reply_markup'] = reply_markup
	data['reaction_with'] = reaction_with
	await user_state.Formation.SendPost.set()
	await state.update_data(data=data)

	try:
		await bot.edit_message_reply_markup(message.from_user.id, data['post_message_id'], reply_markup=reply_markup)
	except Exception as e:
		print(e)

	data['reply_markup'] = mes.reply_markup
	data['hidden_sequel'] = None
	await bot.delete_message(config.TRASH_CHANNEL_ID, mes.message_id)
	# await bot.delete_message(message.from_user.id, data['message_id'][0])
	await bot.delete_message(message.from_user.id, data['message_id'])
	await bot.delete_message(message.from_user.id, message.message_id)

	mes = await message.answer('⚙️  Настройка сообщения ✏️', reply_markup=inline.edit_message())
	await state.update_data(data=data, menu_message=mes)

	# await message.answer('Клавиатура сохраненна.\nПродолжай отправлять сообщения.')		

async def formations_send_post_send_price(message: types.Message, state: FSMContext):
	text = message.text
	# part
	await bot.delete_message(message.chat.id, message.message_id)
	if not message.text.isdigit():
		await message.answer('Ошибка! Это не число')
		return
	
	data = await state.get_data()

	p = PostInfo.get(id=data['info'])
	p.price = int(text)
	p.save()
	await bot.edit_message_reply_markup(chat_id=message.from_user.id, message_id=data['album_message'], reply_markup=inline.add_markup_send_post(context=p.id))

	deleted = True
	i = 1
	while deleted:
		try:
			await bot.delete_message(message.chat.id, message.message_id-i)
			deleted = False
		except Exception:
			i += 1

	await user_state.AddPost.SendPost.set()
	await state.update_data(data=data)

async def formations_send_post_send_text(message: types.Message, state: FSMContext):
	text = message.html_text
	data = await state.get_data()
	for i in data['dicts']:
		if i['text']:
			i['text'] = ''
	data['dicts'][0]['text'] = text

	if len(data['dicts']) > 1:
		reply_markup = None
	else:
		reply_markup = data['dicts'][0]['reply_markup']

	if data['dicts'][0]['type'] == 'text':
		await bot.edit_message_text(text=text, chat_id=message.from_user.id, message_id=data['post_message_id'], reply_markup=reply_markup)
	else:
		print(data['post_message_id'])
		for i in range(len(data['dicts'])):
			if data['dicts'][i]['text']:
				try:
					await bot.edit_message_caption(message.chat.id, data['post_message_id'] + i, caption='', reply_markup=data['dicts'][0]['reply_markup'])
				except Exception as e:
					pass
		await bot.edit_message_caption(caption=text, chat_id=message.from_user.id, message_id=data['post_message_id'], reply_markup=reply_markup)
	for i in data.get('message_to_delete'):
		await bot.delete_message(message.from_user.id, i)

	await bot.delete_message(message.from_user.id, message.message_id)
	await user_state.Formation.SendPost.set()

	mes = await message.answer('⚙️  Настройка сообщения ✏️', reply_markup=inline.edit_message())
	await state.update_data(data=data, menu_message=mes)


async def formations_send_post_edit_media(call: types.CallbackQuery, state: FSMContext):
	print('Start')
	data = await state.get_data()
	if data['dicts'][0]['type'] == 'text':
		await call.message.asnwer('Недоступно для данного сообщения!')
		return

	await user_state.EditModerationPost.SendMedia.set()
	await state.update_data(data, start_message_id=None)
	await call.message.edit_text('Пришлите новое фото или видео', reply_markup=inline.only_back())

async def formations_send_post_send_media(message: types.Message, state: FSMContext):
	data = await state.get_data()

	if data.get('start_message_id') is None:
		data['start_message_id'] = 0
		old_text = ''
		for dict in data['dicts']:
			if dict['text']:
				old_text = dict['text']
		await state.update_data(old_text=old_text, old_reply_markup=data['dicts'][0]['reply_markup'])
		data['dicts'] = []
		data['mess'] = []
		await state.update_data(start_message_id=0, dicts=[], mess=[])
	if data['start_message_id'] == 0:
		await state.update_data(start_message_id=message.message_id)
	data = await state.get_data()

	dict = await convert_message(message, state)

	dicts = data['dicts']
	messes = data['mess']
	if isinstance(dict, list):
		dicts.extend(dict)
	else:
		dicts.append(dict)
	messes.append(message)
	await state.update_data(dicts=dicts, mess=messes)

	if not await next_message_exists(message):
		data = await state.get_data()
		# if data.get('album_message'):
		# 	return
		dicts[0]['text'] = data['old_text']
		dicts[0]['reply_markup'] = data['old_reply_markup']
		mess = await send_message_dicts(dicts, message.chat.id)	
		p = PostInfo.create()
		post_message_id = data['start_message_id'] + len(data['dicts'])
		if data.get('start_choose_mes'):
			await data.pop('start_choose_mes').delete()
			await state.update_data(data)
		if data.get('message_id_delete'): await bot.delete_message(message.chat.id, data['message_id_delete'])

		for dict in dicts:
			if dict.get('file_id'):
				file = await bot.get_file(dict['file_id'])
				file_path=f'media/{file.file_path}'
				await bot.download_file(file.file_path, destination=file_path)			
				dict['file_path'] = file_path
				print('Updated dict: ')
				print(dict)
		# old_data = data.get('old_data')
		# for i in range(len(old_data['dicts'])):
		# 	try:
		# 		await bot.delete_message(message.chat.id, data['post_message_id'] + i)
		# 	except Exception as e:
		# 		print(e)
		# data.pop('old_data')
		await state.update_data(dicts=dicts)
	
		for mes in data.pop('mess'):
			await mes.delete()
	data = await state.get_data()
	await user_state.Formation.SendPost.set()
	await state.update_data(data)
	await state.update_data(info=p.id, active=True, post_message_id=post_message_id, post_message=mess)

	mes = await message.answer('⚙️  Настройка сообщения ✏️', reply_markup=inline.edit_message())
	await state.update_data(menu_message=mes)



async def formations_send_post_edit_next(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	await state.finish()
	await user_state.EditModerationPost.SendTime.set()
	await state.update_data(data)
	await state.update_data(post_date=0)
	data = await state.get_data()
	await call.message.edit_text(TEXTS.postpone_rule, reply_markup=inline.moder_postpone(data))



async def formations_send_post_adv(message: types.Message, state: FSMContext):
	# point 
	if message.animation or message.sticker or message.video_note:
		await message.answer('Unsupported type!')
		return

	data = await state.get_data()

	if data.get('start_message_id') is None:
		data['start_message_id'] = 0
		data['dicts'] = []
		data['mess'] = []
		await state.update_data(start_message_id=0, dicts=[], mess=[])

	if data['start_message_id'] == 0:
		await state.update_data(start_message_id=message.message_id)
	data = await state.get_data()

	dict = await convert_message(message, state)

	dicts = data['dicts']
	messes = data['mess']
	if isinstance(dict, list):
		dicts.extend(dict)
	else:
		dicts.append(dict)
	messes.append(message)
	await state.update_data(dicts=dicts, mess=messes)
	print(message.message_id)

	if not await next_message_exists(message):
		print('the last')
		data = await state.get_data()
		if data.get('album_message'):
			return
		print(dicts)
		mess = await send_message_dicts(dicts, message.chat.id)	
		p = PostInfo.create()
		mes = await message.answer('⚙️  Настройка сообщения ✏️', reply_markup=inline.edit_message())
		post_message_id = data['start_message_id'] + len(data['dicts'])
		if data.get('start_choose_mes'):
			await data.pop('start_choose_mes').delete()
			await state.update_data(data)
		await state.update_data(info=p.id, active=True, post_message_id=post_message_id, menu_message=mes, post_message=mess)
		for mes in data.pop('mess'):
			try:
				await mes.delete()
			except Exception as e:
				pass
		
		for dict in dicts:
			if dict.get('file_id'):
				file = await bot.get_file(dict['file_id'])
				file_path=f'media/{file.file_path}'
				await bot.download_file(file.file_path, destination=file_path)			
				dict['file_path'] = file_path
				print('Updated dict: ')
		await state.update_data(dicts=dicts)
		data = await state.get_data()




async def delete_basket_channel(call: types.CallbackQuery, state: FSMContext):
	channels = list(Basket.select().where(Basket.user_id == call.from_user.id))
	for i in range(len(channels)):
		c = channels[i]
		if c.find_channel_id == int(call.data.split('$')[1]):
			c.delete_instance()
			del channels[i]
			break

	basket = [FindChannel.get(id=b.find_channel_id) for b in channels]
	await call.message.edit_reply_markup(reply_markup=inline.basket(basket))

async def back_to_basket(call: types.CallbackQuery, state: FSMContext):
	channels = Basket.select().where(Basket.user_id == call.from_user.id)
	basket = [FindChannel.get(id=b.find_channel_id) for b in channels]
	await call.message.edit_caption('', reply_markup=inline.basket(basket))


async def go_to_basket(call: types.CallbackQuery, state:  FSMContext):
	await state.finish()
	basket = Basket.select().where(Basket.user_id == call.from_user.id)
	basket = [FindChannel.get(id=b.find_channel_id) for b in basket]

	await call.message.delete()
	current_directory = os.getcwd()
	basket_photo = InputFile(path_or_bytesio=f'{current_directory}/images/basket.jpg')
	await call.message.answer_photo(basket_photo, reply_markup=inline.basket(basket))


async def add_basket_channel(call: types.CallbackQuery, state: FSMContext):
	await call.message.delete()
	await call.message.answer(TEXTS.choose_cat, reply_markup=reply.choose_cat())


async def saved_handler(message: types.Message, state: FSMContext):
	channels = Saved.select().where(Saved.user_id == message.from_user.id)
	current_directory = os.getcwd()
	photo = InputFile(path_or_bytesio=f'{current_directory}/images/saved.png')
	await message.answer_photo(photo, reply_markup=inline.my_saved(channels))

async def open_saved_channel(call: types.CallbackQuery, state: FSMContext):
	channel = FindChannel.get(id=int(call.data.split('$')[1]))
	# b = Basket.select().where(Basket.find_channel_id == channel.id)
	b = Saved.select().where((Saved.find_channel_id == channel.id) & (Saved.user_id == call.from_user.id))
	# resp = 0
	# for i in b:
	# 	if i.user_id == call.from_user.id:
	# 		resp = i.id
	await call.message.edit_caption(TEXTS.find_channel_form(channel), reply_markup=inline.back_to_saved_channel(b[0].id))

async def delete_saved_channel(call: types.CallbackQuery, state: FSMContext):
	print(f'{call.data.split("$")[1]=}')
	c = Saved.get(id=int(call.data.split('$')[1]))
	c.delete_instance()
	await bot.answer_callback_query(call.id, 'Удаленно из избранного')
	channels = Saved.select().where(Saved.user_id == call.from_user.id)
	current_directory = os.getcwd()
	photo = InputFile(path_or_bytesio=f'{current_directory}/images/saved.png')
	await call.message.delete()
	await call.message.answer_photo(photo, reply_markup=inline.my_saved(channels))

async def back_to_saved_channels(call: types.CallbackQuery, state: FSMContext):
	channels = Saved.select().where(Saved.user_id == call.from_user.id)
	current_directory = os.getcwd()
	photo = InputFile(path_or_bytesio=f'{current_directory}/images/saved.png')
	await call.message.edit_caption('', reply_markup=inline.my_saved(channels))

async def my_ord_handler(call: types.CallbackQuery, state: FSMContext):
	account = AccountOrd.get_or_none(user_id=call.from_user.id)
	if account:
		await call.message.edit_caption(TEXTS.my_ord_success, reply_markup=inline.only_back())
	else:
		await call.message.edit_caption(TEXTS.my_ord_unsuccess, reply_markup=inline.answer_register_ord_account_client())


async def myself_cabinet_handler(message: types.Message, state: FSMContext):
	current_directory = os.getcwd()
	photo = InputFile(path_or_bytesio=f'{current_directory}/images/cabinet.jpg')
	await message.answer_photo(photo, reply_markup=inline.myself_cabinet())


async def placement_stat_handler(call: types.CallbackQuery, state: FSMContext):
	await user_state.CabinetStats.Main.set()
	ad_placements = []
	wls = WaitList.select().where(WaitList.user_id==call.from_user.id)
	for wl in wls:
		ap = AdvertPost.get_or_none(wait_list_id=wl.id)
		if ap:
			if ap.is_paid:
				ad_placements.append([ap, wl])
	week = []
	week_time = 7 * 24* 60 * 60
	month = []
	month_time = 30 * 24* 60 * 60
	future = []
	now = time.time()
	for ad in ad_placements:
		delay = now - ad[1].seconds
		if delay < 0:
			future.append(ad)
		if delay < week_time:
			week.append(ad)
		if delay < month_time:
			month.append(ad)
	text = await TEXTS.placements_stat_basket(week, month, future, ad_placements, bot)
	await call.message.edit_caption(text, reply_markup=inline.only_back())


async def back_to_cabinet_new(call: types.CallbackQuery, state: FSMContext):
	await state.finish()
	await call.message.delete()
	current_directory = os.getcwd()
	photo = InputFile(path_or_bytesio=f'{current_directory}/images/cabinet.jpg')
	await call.message.answer_photo(photo, reply_markup=inline.myself_cabinet())


async def choose_cat_handler(message: types.Message, state: FSMContext):
	await message.answer(TEXTS.choose_cat, reply_markup=reply.choose_cat())

async def find_by_cat(message: types.Message, state: FSMContext):
	await message.answer('Выберите категорию', reply_markup=inline.choose_cat_adv())


async def find_by_keyword(message: types.Message, state: FSMContext):
	await user_state.Find.SendKeyword.set()
	await message.answer('Введите название канала или слово для поиска')


async def setting_filters(message: types.Message, state: FSMContext):
	await user_state.SettingFilters.Main.set()
	await message.answer(TEXTS.setting_filters(), reply_markup=inline.setting_filters())

async def send_keyword(message: types.Message, state: FSMContext):
	await state.finish()
	channels = FindChannel.select()
	resp = []
	for channel in channels:
		if message.text.lower() in channel.title.lower():
			resp.append(channel)

	if resp == []:
		await message.answer('Каналов не найдено')
		return

	await user_state.SendKeyword.ChooseChannel.set()
	await state.update_data(channels=list(resp), type='keyword')

	await message.answer(TEXTS.choose_channel, reply_markup=inline.choose_find_channel(resp))

async def open_find_channel(call: types.CallbackQuery, state: FSMContext):
	channel = FindChannel.get(id=int(call.data.split('$')[1]))
	await call.message.edit_text(TEXTS.find_channel_form(channel), reply_markup=inline.back_to_find_channel(call.from_user.id, channel.id))


async def back_to_find_channel(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	channels = data['channels']

	await call.message.edit_text(TEXTS.choose_channel, reply_markup=inline.choose_find_channel(channels))


async def change_page_to_find_channel(call: types.CallbackQuery, state: FSMContext):
	page = int(call.data.split('$')[1])
	data = await state.get_data()
	channels = data['channels']
	await call.message.edit_text(TEXTS.choose_channel, reply_markup=inline.choose_find_channel(channels, page))

async def back_page_to_find(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	type = data['type']
	await state.finish()

	if type == 'category':
		await call.message.edit_text('Выберите категорию', reply_markup=inline.choose_cat_adv())
	elif type == 'keyword':
		await call.message.delete()
		await user_state.Find.SendKeyword.set()
		await call.message.answer('Введите название канала или слово для поиска')
	elif type == 'filters':
		await user_state.SettingFilters.Main.set()
		await state.update_data(data)
		await call.message.edit_text(TEXTS.setting_filters(data=data), reply_markup=inline.setting_filters())


async def save_find_channel(call: types.CallbackQuery, state: FSMContext):
	channel_id = int(call.data.split('$')[1])
	channel = FindChannel.get(id=channel_id)
	b = Saved.select().where(Saved.user_id == call.from_user.id)
	f = False
	for i in b:
		if i.find_channel_id == channel_id:
			f = i
	if f:
		f.delete_instance()

	else:
		b = Saved.create(user_id=call.from_user.id, find_channel_id=channel_id)
		b.save()

	await call.message.edit_text(TEXTS.find_channel_form(channel), reply_markup=inline.back_to_find_channel(call.from_user.id, channel.id))


async def save_find_channel_start(call: types.CallbackQuery, state: FSMContext):
	channel_id = int(call.data.split('$')[1])
	channel = FindChannel.get(id=channel_id)
	b = Saved.select().where(Saved.user_id == call.from_user.id)
	f = False
	for i in b:
		if i.find_channel_id == channel_id:
			f = i
	if f:
		f.delete_instance()

	else:
		b = Saved.create(user_id=call.from_user.id, find_channel_id=channel_id)
		b.save()

	await call.message.edit_text(TEXTS.find_channel_form(channel), reply_markup=inline.start_channel(call.from_user.id, channel.id))



async def basket_find_channel(call: types.CallbackQuery, state: FSMContext):
	channel_id = int(call.data.split('$')[1])
	channel = FindChannel.get(id=channel_id)

	b = Basket.select().where(Basket.user_id == call.from_user.id)
	f = False
	for i in b:
		if i.find_channel_id == channel_id:
			f = i
	if f:
		f.delete_instance()

	else:
		b = Basket.create(user_id=call.from_user.id, find_channel_id=channel_id)
		b.save()

	await call.message.edit_text(TEXTS.find_channel_form(channel), reply_markup=inline.back_to_find_channel(call.from_user.id, channel.id))



async def basket_find_channel_start(call: types.CallbackQuery, state: FSMContext):
	channel_id = int(call.data.split('$')[1])
	channel = FindChannel.get(id=channel_id)

	b = Basket.select().where(Basket.user_id == call.from_user.id)
	f = False
	for i in b:
		if i.find_channel_id == channel_id:
			f = i
	if f:
		f.delete_instance()

	else:
		b = Basket.create(user_id=call.from_user.id, find_channel_id=channel_id)
		b.save()

	await call.message.edit_text(TEXTS.find_channel_form(channel), reply_markup=inline.start_channel(call.from_user.id, channel.id))



async def choose_cat_to_find_adv(call: types.CallbackQuery, state: FSMContext):
	await state.finish()
	print('init')
	cat = int(call.data.split('$')[1])

	channels = FindChannel.select().where((FindChannel.category == cat) & (FindChannel.active == True))

	if not channels:
		await call.message.answer('Каналов не найдено')
		return

	await user_state.SendKeyword.ChooseChannel.set()
	await state.update_data(channels=list(channels), type='category')

	await call.message.edit_text(TEXTS.choose_channel, reply_markup=inline.choose_find_channel(channels))


async def filter_err(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	await user_state.SettingFilters.SetERR.set()
	await state.update_data(data)

	await call.message.edit_text('Средний охват поста ERR', reply_markup=inline.filters_err())

async def filter_views(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	await user_state.SettingFilters.SetView.set()
	await state.update_data(data)

	mes = await call.message.edit_text('Введите количество просмотров через тире от минимума к максимуму\n\n'
								 'Например: 10000-20000', reply_markup=inline.back_to_filters())

	await state.update_data(data, mes_to_del=mes.message_id)


async def filter_sub(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	await user_state.SettingFilters.SetSub.set()

	mes = await call.message.edit_text('Введите количество подписчиков через тире от минимума к максимуму\n\n'
								 'Например: 10000-20000', reply_markup=inline.back_to_filters())

	await state.update_data(data, mes_to_del=mes.message_id)


async def filter_show_result(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()

	print('Filter show result')


	err = data.get('err')
	views = data.get('views')
	sub = data.get('sub')

	print(f'{err=} {views=} {sub=}')

	if err: err = [20*(err-1), 20*err]

	if not(err or views or sub):
		await call.message.answer('Установите хотя бы 1 фильтр')
		return

	channels = FindChannel.select().where(
		(((FindChannel.err >= err[0]) & (FindChannel.err <= err[1])) if err else True)
		&
		(((FindChannel.views >= views[0]) & (FindChannel.views <= views[1])) if views else True)
		&
		(((FindChannel.subscribers >= sub[0]) & (FindChannel.subscribers <= sub[1])) if sub else True)
	)
	# resp = []
	#
	# for channel in channels:
	# 	flag = True
	# 	if err:
	# 		channel_err = round(100 * channel.views / channel.subscribers, 1)  if channel.subscribers else 0
	# 		print(channel_err)
	# 		print((err-1) * 20)
	# 		if not((err-1) * 20 < channel_err < (err) * 20):
	# 			flag = False
	# 			continue
	# 	if views:
	# 		if not(views[0] < channel.views < views[0]):
	# 			flag = False
	# 			continue
	#
	# 	if sub:
	# 		if not(sub[0] < channel.subscribers < sub[0]):
	# 			flag = False
	# 			continue
	#
	# 	if flag:
	# 		resp.append(channel)

	await user_state.SendKeyword.ChooseChannel.set()
	await state.update_data(data, channels=list(channels), type='filters')

	await call.message.edit_text(TEXTS.choose_channel, reply_markup=inline.choose_find_channel(channels))



async def back_to_filters(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	await user_state.SettingFilters.Main.set()
	await state.update_data(data)

	await call.message.edit_text(TEXTS.setting_filters(data=data), reply_markup=inline.setting_filters())

async def filters_err(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	await user_state.SettingFilters.Main.set()
	await state.update_data(data, err=int(call.data.split('$')[1]))
	data = await state.get_data()

	await call.message.edit_text(TEXTS.setting_filters(data=data), reply_markup=inline.setting_filters())

async def filters_views(message: types.Message, state: FSMContext):
	t = message.text.split('-')
	if len(t) != 2 or not(t[0].isdigit() and t[1].isdigit()):
		await message.answer('Ошибка парсинга!')
		return
	s = []
	s.append(int(t[0]))
	s.append(int(t[1]))
	t = s

	if not(0 < t[0] < t[1] and t[1] < 10 ** 8):
		await message.answer('Неправильные значения')
		return

	data = await state.get_data()
	await user_state.SettingFilters.Main.set()
	await state.update_data(data, views=t)
	data = await state.get_data()

	await bot.delete_message(message.from_user.id, data['mes_to_del'])
	await bot.delete_message(message.from_user.id, message.message_id)

	await message.answer(TEXTS.setting_filters(data=data), reply_markup=inline.setting_filters())

async def filters_sub(message: types.Message, state: FSMContext):
	t = message.text.split('-')
	if len(t) != 2 or not(t[0].isdigit() and t[1].isdigit()):
		await message.answer('Ошибка парсинга!')
		return
	s = []
	s.append(int(t[0]))
	s.append(int(t[1]))
	t = s

	if not(0 < t[0] < t[1] and t[1] < 10 ** 8):
		await message.answer('Неправильные значения')
		return

	data = await state.get_data()
	await user_state.SettingFilters.Main.set()
	await state.update_data(data, sub=t)
	data = await state.get_data()

	await bot.delete_message(message.from_user.id, data['mes_to_del'])
	await bot.delete_message(message.from_user.id, message.message_id)

	await message.answer(TEXTS.setting_filters(data=data), reply_markup=inline.setting_filters())


async def proccess_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
	print('ACCESS')
	await bot.answer_pre_checkout_query(pre_checkout_query_id=pre_checkout_query.id, ok=True)


async def successful_payment(message: types.Message):
	advert_post_id = int(message.successful_payment.invoice_payload)
	advert_post = AdvertPost.get(id=advert_post_id)
	advert_post.is_paid = True
	advert_post.save()
	wl = WaitList.get(advert_post.wait_list_id)
	wallet = Wallet.get(user_id=wl.admin_id)
	wallet.balance = wallet.balance + wl.price
	wallet.save()
	await message.answer('Оплата прошла успешно!')
	await bot.send_message(wl.admin_id, f'Ваш баланс пополнен на {wl.price}')


async def my_advert_post_handler(call: types.CallbackQuery, state: FSMContext):
	await user_state.CabinetStats.Main.set()
	ad_placements = []
	wls = WaitList.select().where(WaitList.user_id==call.from_user.id)
	for wl in wls:
		if wl.seconds < time.time():
			continue
		ap = AdvertPost.get_or_none(wait_list_id=wl.id)
		if ap:
			if ap.is_paid:
				ad_placements.append([ap, wl])

	text = await TEXTS.my_advert_post(bot, ad_placements)
	await call.message.edit_caption(text, reply_markup=inline.only_back())



async def my_posts_handler(message: types.Message, state: FSMContext):
	posts = MyPostBot.select().where(MyPostBot.user_id == message.from_user.id)
	await user_state.CabinetStats.Main.set()
	await message.answer(TEXTS.my_posts, reply_markup=inline.my_posts(posts))


async def add_my_post_handler(call: types.CallbackQuery, state: FSMContext):
	await user_state.AddMyPost.SendPost.set()
	mes = await call.message.answer(TEXTS.send_my_post, reply_markup=inline.only_back())
	await state.update_data(date=None, media=[], reply_markup=None, text='', send_post_message=mes, my_post_message=call.message)


async def send_photo_post_handler(message: types.Message, state: FSMContext):
	# pointed 
	if message.animation or message.sticker or message.video_note:
		await message.answer('Unsupported type!')
		return

	data = await state.get_data()

	if data.get('start_message_id') is None:
		data['start_message_id'] = 0
		data['dicts'] = []
		data['mess'] = []
		await state.update_data(start_message_id=0, dicts=[], mess=[])

	if data['start_message_id'] == 0:
		await state.update_data(start_message_id=message.message_id)
	data = await state.get_data()

	dict = await convert_message(message, state)

	dicts = data['dicts']
	messes = data['mess']
	if isinstance(dict, list):
		dicts.extend(dict)
	else:
		dicts.append(dict)
	messes.append(message)
	await state.update_data(dicts=dicts, mess=messes)

	if not await next_message_exists(message):
		data = await state.get_data()
		if data.get('album_message'):
			return
		
		# menu_mes = await message.answer('⚙️  Настройка сообщения ✏️', reply_markup=inline.edit_message())
		# await user_state.EditModerationPost.Main.set()
		# await state.update_data(data, message=mes, menu_message=menu_mes)
		p = PostInfo.create()
		# mes = await message.answer(TEXTS.album_edit, reply_markup=inline.add_markup_send_post(None, True, context=p.id), disable_web_page_preview=True)
		for mes in data.pop('mess'):
			try:
				await mes.delete()
			except Exception as e:
				pass
		dictobject = DictObject.create(owner_id=message.from_user.id)
		for dict in dicts:
			if dict.get('file_id'):
				file = await bot.get_file(dict['file_id'])
				file_path=f'media/{file.file_path}'
				await bot.download_file(file.file_path, destination=file_path)			
				dict['file_path'] = file_path
			current_dict = Dict.create(
				object_id = dictobject.id,
				type = dict['type'],
				file_id = dict.get('file_id'),
				file_path = dict.get('file_path'),
				text = dict.get('text'),
				reply_markup = utils.create_keyboard(dict.get('reply_markup'))
			)
			current_dict.save()
		dictobject.save()
		post_info = PostInfo.create(post_id=dictobject.id)
		post_info.save()
		my_post = MyPostBot.create(
			user_id = message.from_user.id,
			post_id = dictobject.id
		)
		my_post.save()
		
		await data['send_post_message'].delete()
		await data['my_post_message'].delete()
		await state.finish()
		await message.answer('<b>✅ Успешно добавлено</b>')
		current_directory = os.getcwd()
		photo = InputFile(path_or_bytesio=f'{current_directory}/images/cabinet.jpg')
		posts = MyPostBot.select().where(MyPostBot.user_id == message.from_user.id)
		await user_state.CabinetStats.Main.set()
		await message.answer_photo(photo, TEXTS.my_posts, reply_markup=inline.my_posts(posts))


async def add_my_post_back(call: types.CallbackQuery, state: FSMContext):
	await user_state.CabinetStats.Main.set()
	await call.message.delete()



async def formations_send_post_choose_my_post(call: types.CallbackQuery, state: FSMContext):
	posts = MyPostBot.select().where(MyPostBot.user_id == call.from_user.id)

	await call.message.edit_text('<b>Выберите пост</b>', reply_markup=inline.my_posts_b(posts))


async def formations_send_post_back(call: types.CallbackQuery, state: FSMContext):
	await bot.delete_message(call.from_user.id, call.message.message_id - 1)
	await call.message.delete()
	await state.finish()
	basket = Basket.select().where(Basket.user_id == call.from_user.id)
	basket = [FindChannel.get(id=b.find_channel_id) for b in basket]
	current_directory = os.getcwd()
	basket_photo = InputFile(path_or_bytesio=f'{current_directory}/images/basket.jpg')
	await call.message.answer_photo(basket_photo, reply_markup=inline.basket(basket))


async def choose_my(call: types.CallbackQuery, state: FSMContext):
	dictobject = DictObject.get(id=int(call.data.split("$")[1]))
	dictss = Dict.select().where(Dict.object_id==dictobject.id)
	dicts = []
	for dict in dictss:
		dicts.append(
			{
				'type': dict.type,
				'file_id': dict.file_id,
				'text': dict.text,
				'reply_markup': inline.from_db_to_markup_by_key_id(dict.reply_markup),
				'file_path': dict.file_path
			}
		)
	print(f"new dicts: {dicts=}")
	mess = await send_message_dicts(dicts, call.message.chat.id)	
	p = PostInfo.create()
	await call.message.delete()
	mes = await call.message.answer('⚙️  Настройка сообщения ✏️', reply_markup=inline.edit_message())
	
	post_message_id = mess.message_id
	await state.update_data(info=p.id, active=True, post_message_id=post_message_id, menu_message=mes, post_message=mess)

	await state.update_data(dicts=dicts, mess=[])

async def check_user_handler(message: types.Message, state: FSMContext):
	await user_state.CheckUser.SendMessage.set()
	await message.answer("<b>🔍 Перешлите ID или сообщение пользователя для проверки 🔎</b>", reply_markup=inline.only_back())

async def send_check_user_handler(message: types.Message, state: FSMContext):
	try:
		chat = await bot.get_chat(int(message.text))
	except Exception as e:
		chat = None
	if not chat:
		try:
			chat = await bot.get_chat(message.forward_from.id)
		except Exception as e:
			chat = None

	if not chat: 
		await message.answer('<b>❌ Пользователь не найден или его профиль закрыт ❌</b>')
		return

	ads = AdvertPost.select().where((AdvertPost.active) & (AdvertPost.is_paid))
	wls = []
	for ad in ads: 
		wl = WaitList.get_or_none(id=ad.wait_list_id)
		if not wl:
			print(ad.wait_list_id)
			continue
		if wl.admin_id == chat.id:
			wls.append(wl)
	wls_sum = sum([i.price for i in wls])
	defs = DeferredVerification.select().where((DeferredVerification.active) & (DeferredVerification.admin_id==chat.id))
	defs_sum = sum([i.price for i in defs])
	freeze_balance = wls_sum + defs_sum
	wallet = Wallet.get(user_id=chat.id)
	balance = wallet.balance

	print(f'{wls_sum=}')
	print(f'{defs_sum=}')

	text = f'''👤 <b>Пользователь <a href="{chat.user_url}">{chat.first_name}</a>
	
💰 Баланс: {balance}
❄️ Замороженно: {freeze_balance}

💸 Доступно к выводу: {balance - freeze_balance}</b>'''

	await message.answer(text)
	await state.finish()

async def close_check_user_handler(call: types.CallbackQuery, state: FSMContext):
	await state.finish()
	await call.message.delete()
	try:
		await bot.delete_message(call.from_user.id, call.message.message_id-1)
	except Exception as e:
		pass


def register_user_handlers(dp: Dispatcher):
	from handlers.manager.main import register_manager_handlers

	dp.register_pre_checkout_query_handler(proccess_pre_checkout_query)
	dp.register_message_handler(successful_payment, content_types=types.message.ContentType.SUCCESSFUL_PAYMENT)
	
	dp.register_message_handler(start_handler, commands=['start', 'restart'], state='*')
	dp.register_message_handler(developer_handler, commands=['developer'], state='*')
	dp.register_message_handler(cryptobot_handler, commands=['cryptobot'], state='*')
	dp.register_message_handler(get_crypto_bot_balance_handler, commands=['cryptobot_balance'], state='*')
	dp.register_message_handler(support_handler, commands=['support'], state='*')
	dp.register_message_handler(work_handler, commands=['work'], state='*')
	dp.register_message_handler(check_user_handler, commands=['check_user'], state='*')
	dp.register_message_handler(send_check_user_handler, content_types=types.ContentTypes.ANY, state=user_state.CheckUser.SendMessage)
	dp.register_callback_query_handler(close_check_user_handler, text='back', state=user_state.CheckUser.SendMessage)
	dp.register_message_handler(send_answer_start_offer_access,
								state=user_state.SendSmallAnswer.sendAnswerStartOfferAccess)
	dp.register_message_handler(add_channel_end_cancel, state=user_state.Settings.sendMessageFromChannel,
								text='Отмена')
	dp.register_message_handler(add_channel_end, state=[user_state.AddNewChannel.sendMessageFromChannel, user_state.Settings.sendMessageFromChannel],
								content_types=['text', 'photo', 'video', 'voice'])

	register_manager_handlers(dp)


	dp.register_message_handler(add_channel_begin, text='Добавить канал')
	dp.register_message_handler(start_handler, text=['Меню', '🏠 В меню'], state='*')
	dp.register_message_handler(publications_handler, text='Публикации', state='*')
	dp.register_message_handler(settings_handler, text='Настройки', state='*')
	dp.register_message_handler(advert_handler, text='Реклама', state='*')
	dp.register_message_handler(cabinet_handler, text='Кабинет', state='*')
	dp.register_message_handler(cabinet_payment_data_handler, text='Платежные данные', state='*')
	dp.register_message_handler(balance_my_wallet_handler, text='Баланс лицевого счета', state='*')
	dp.register_message_handler(my_statistic_handler, text='Статистика', state='*')
	dp.register_message_handler(my_ord_data, text='Данные ОРД', state='*')
	dp.register_message_handler(content_plan_handler, text='Контент план', state='*')
	dp.register_message_handler(create_post_handler, text='Создать пост', state='*')
	dp.register_message_handler(rewrite_post_handler, text='Редактировать пост', state='*')
	dp.register_message_handler(set_schedule_, text='Настройка расписания', state=user_state.SettingSchedule.SettingSchedule)
	dp.register_message_handler(set_schedule_main, text='Настройка расписания', state='*')
	dp.register_message_handler(edit_post_text, state=user_state.EditPost.EditText)
	dp.register_message_handler(rewrite_post_edit_text_send, state=user_state.RewritePost.EditText)
	dp.register_message_handler(edit_post_markup, state=user_state.EditPost.EditMarkup)
	dp.register_message_handler(rewrite_post_edit_markup_send, state=user_state.RewritePost.EditMarkup)
	dp.register_callback_query_handler(setting_channel_public_back, state=user_state.Settings.Public, text='back')
	dp.register_callback_query_handler(next_setting_schedule, state=user_state.SettingSchedule.SettingSchedule, text='next')
	dp.register_callback_query_handler(choose_type_ord, state='*', text_startswith='choose_type_ord')
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
	dp.register_message_handler(add_channel_price, state=user_state.SettingSchedule.StartSettingSchedule)
	dp.register_message_handler(send_inn_ord, state=user_state.AddOrd.SendInn, content_types=['text'])
	dp.register_message_handler(send_name_ord, state=user_state.AddOrd.SendName, content_types=['text'])
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
	dp.register_callback_query_handler(content_plan_set_delete_time_start, state=user_state.ContentPlan.Main, text='set_delete_time')
	dp.register_callback_query_handler(content_plan_set_delete_time, state=user_state.ContentPlan.SetDeleteTime, text_startswith='set_delete_time')
	dp.register_callback_query_handler(content_plan_set_delete_time_back, state=user_state.ContentPlan.SetDeleteTime, text_startswith='back')
	dp.register_callback_query_handler(content_plan_unset_delete_time, state=user_state.ContentPlan, text_startswith='unset_delete_time')
	dp.register_callback_query_handler(content_plan_set_price, state=user_state.ContentPlan.Main, text='set_price')
	dp.register_callback_query_handler(content_plan_edit_post, state=user_state.ContentPlan.Main, text='edit_post')
	dp.register_callback_query_handler(content_plan_copy_post, state=user_state.ContentPlan.Main, text='copy_post')
	dp.register_callback_query_handler(content_plan_pre_delete_post, state=user_state.ContentPlan.Main, text='pre_delete_post')
	dp.register_callback_query_handler(content_plan_delete_post, state=user_state.ContentPlan.Main, text='delete_post')
	dp.register_callback_query_handler(del_message, state=user_state.ContentPlan.Main, text='delete_message')
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
	dp.register_callback_query_handler(next_send_post_handler, state=user_state.AddPost.SendPost, text='next_post')
	dp.register_callback_query_handler(cancel_send_post_handler, state=user_state.AddPost.SendPost, text='back_post')
	dp.register_callback_query_handler(choose_copy_channel, state=user_state.AddPost.SendPost, text_startswith='choose_copy_channel$')
	dp.register_callback_query_handler(choose_share_channel, state=user_state.AddPost.SendPost, text_startswith='choose_share_channel$')
	dp.register_callback_query_handler(order_adv, state=user_state.AddPost.SendPost, text_startswith='order_adv')
	dp.register_callback_query_handler(choose_copy_channel_next, state=user_state.AddPost.SendPost, text_startswith='next_copy_channel')
	dp.register_callback_query_handler(choose_share_channel_next, state=user_state.AddPost.SendPost, text_startswith='next_share_channel')
	dp.register_callback_query_handler(send_post_to_reply, state=user_state.AddPost.SendPost, text_startswith='reply_post')
	dp.register_message_handler(get_post_to_reply, state=user_state.AddPost.SendPostToReply, content_types=['text', 'photo', 'video'])
	dp.register_callback_query_handler(get_post_to_reply_back, state=user_state.AddPost.SendPostToReply, text_startswith='back')
	dp.register_message_handler(cancel_swap_keyboard, state=user_state.AddPost.SwapKeyboard, text='Отмена')
	dp.register_callback_query_handler(cancel_swap_media, state=user_state.AddPost.SwapMedia, text='back')
	dp.register_message_handler(swap_keyboard_handler, state=user_state.AddPost.SwapKeyboard, content_types=['text'])
	dp.register_message_handler(formations_send_post_send_price, state=user_state.AddPost.SendPrice, content_types=['text'])
	dp.register_callback_query_handler(cancel_swap_media, state=user_state.AddPost.SendPrice, text='back')

	dp.register_message_handler(swap_media_handler, state=user_state.AddPost.SwapMedia, content_types=types.ContentTypes.ANY)
	dp.register_callback_query_handler(set_delete_time, state=user_state.AddPost.SendPost, text='set_delete_time')
	dp.register_callback_query_handler(set_set_delete_time, state=user_state.AddPost.SendDeleteTime, text_startswith='set_delete_time')
	dp.register_callback_query_handler(unset_set_delete_time, state=user_state.AddPost.SendDeleteTime, text_startswith='unset_delete_time')
	dp.register_callback_query_handler(back_set_delete_time, state=user_state.AddPost.SendDeleteTime, text_startswith='back')
	dp.register_callback_query_handler(swap_keyboard, state=user_state.AddPost.SendPost, text='swap_keyboard')
	dp.register_callback_query_handler(send_post_copy, state=user_state.AddPost.SendPost, text='copy')
	dp.register_callback_query_handler(send_post_share, state=user_state.AddPost.SendPost, text='share')
	dp.register_callback_query_handler(hidden_sequel, state=user_state.AddPost.SendPost, text='hidden_sequel')
	dp.register_message_handler(formations_send_post, state=user_state.AddPost.SendPost, content_types=types.ContentTypes.ANY)
	dp.register_callback_query_handler(send_post_edit_text_handler, state=user_state.AddPost.SendPost, text='edit_text')
	dp.register_callback_query_handler(formations_send_post_edit_price, state=user_state.AddPost.SendPost, text='edit_price')
	dp.register_callback_query_handler(send_post_edit_media_handler, state=user_state.AddPost.SendPost, text='edit_media')
	dp.register_callback_query_handler(send_post_swap_notification_handler, state=user_state.AddPost.SendPost, text='swap_notification')
	dp.register_callback_query_handler(send_post_swap_disable_web_preview_handler, state=user_state.AddPost.SendPost, text='swap_disable_web_preview')
	dp.register_callback_query_handler(send_post_swap_comments_handler, state=user_state.AddPost.SendPost, text='swap_comments')
	dp.register_callback_query_handler(send_post_swap_auto_write_handler, state=user_state.AddPost.SendPost, text='swap_auto_write')
	dp.register_callback_query_handler(send_post_reply_post_handler, state=user_state.AddPost.SendPost, text='reply_post')
	dp.register_message_handler(rewrite_get_post_back, state=user_state.RewritePost.Main, text='Отмена')
	dp.register_message_handler(rewrite_get_post_just_back, state=[user_state.RewritePost.EditText, user_state.RewritePost.EditMedia, user_state.RewritePost.EditMarkup], text='Отмена')
	dp.register_message_handler(rewrite_get_post, state=user_state.RewritePost.Main, content_types=['text', 'photo', 'video'])
	dp.register_message_handler(send_edit_post_text_handler, state=user_state.SendEditPost.EditText, content_types=['text'])
	dp.register_callback_query_handler(send_edit_post_back_handler, state=user_state.SendEditPost, text='back')
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
	dp.register_callback_query_handler(wl_postpone_time, state=user_state.WlNewTime.SendTime, text_startswith='postpone_date')
	dp.register_callback_query_handler(postpone_time_back, state=user_state.AddPost.SendTime, text_startswith='back')
	dp.register_callback_query_handler(wl_postpone_time_back, state=user_state.WlNewTime.SendTime, text_startswith='back')
	dp.register_message_handler(send_hidden_sequel, state=user_state.AddPost.SendHiddenSequel, content_types=['text'])
	dp.register_callback_query_handler(send_hidden_sequel_back, state=user_state.AddPost.SendHiddenSequel, text_startswith='back')
	dp.register_message_handler(parse_postpone_time, state=user_state.AddPost.SendTime, content_types=['text'])
	dp.register_message_handler(wl_send_time, state=user_state.WlNewTime.SendTime, content_types=['text'])
	dp.register_callback_query_handler(content_plan_postpone_time, state=user_state.ContentPlan.SetPostTime, text_startswith='postpone_date')
	dp.register_callback_query_handler(content_plan_postpone_time_back, state=user_state.ContentPlan.SetPostTime, text_startswith='back')
	dp.register_message_handler(content_plan_parse_postpone_time, state=user_state.ContentPlan.SetPostTime, content_types=['text'])
	dp.register_callback_query_handler(content_plan_delete_time, state=user_state.ContentPlan.SetDeleteTime, text_startswith='choose_delete_time')
	dp.register_callback_query_handler(content_plan_delete_time_back, state=user_state.ContentPlan.SetDeleteTime, text_startswith='back')
	dp.register_callback_query_handler(content_plan_set_price_back, state=user_state.ContentPlan.SetPrice, text_startswith='back')
	dp.register_message_handler(content_plan_parse_delete_time, state=user_state.ContentPlan.SetDeleteTime, content_types=['text'])
	dp.register_message_handler(content_plan_send_price, state=user_state.ContentPlan.SetPrice, content_types=['text'])
	dp.register_callback_query_handler(setting_channel, state=user_state.Settings.Main, text_startswith='setting_channel')
	dp.register_callback_query_handler(setting_add_channel, state=user_state.Settings.Main, text_startswith='add_channel')
	dp.register_callback_query_handler(setting_application_manage, state=user_state.Settings.Main, text_startswith='application_manage')
	dp.register_callback_query_handler(setting_referal_program, state=user_state.Settings.Main, text_startswith='referal_program')
	dp.register_callback_query_handler(setting_channel_schedule, state=user_state.Settings.SettingChannel, text_startswith='schedule')
	dp.register_callback_query_handler(hidden_sequal_click, state='*', text_startswith='hidden_sequal')
	dp.register_callback_query_handler(setting_channel_ads_link, state=user_state.Settings.SettingChannel, text_startswith='ads_link')
	dp.register_callback_query_handler(moderation_manage_myself_moderation, state=user_state.ModerationManage.Main, text='self_moderation')
	dp.register_callback_query_handler(moderation_manage_categories, state=user_state.ModerationManage.Main, text='categories')
	dp.register_callback_query_handler(moderation_manage_confirmer, state=user_state.ModerationManage.Main, text='confirmer')
	dp.register_callback_query_handler(redactor_manage_update_moder, state=user_state.ModerationManage.Main, text='update_moder')
	dp.register_callback_query_handler(redactor_manage_pre_create_moder, state=user_state.ModerationManage.Main, text='add_moder')
	dp.register_callback_query_handler(redactor_manage_pre_create_manager, state=user_state.ManagerManage.Main, text='add_manager')
	# dp.register_callback_query_handler(setting_channel_back, state=user_state.Settings.SettingChannel, text='back')
	dp.register_callback_query_handler(setting_back, state=user_state.Settings, text='back')
	dp.register_callback_query_handler(choose_cat_to_find, state=user_state.SettingSchedule.StartSettingSchedule, text_startswith='choose_cat_to_find$')
	dp.register_callback_query_handler(change_page_to_find, state=user_state.SettingSchedule.StartSettingSchedule, text_startswith='change_page_to_find$')
	dp.register_callback_query_handler(content_plan_back_to_edit_post, state=user_state.EditPost, text='back')
	dp.register_callback_query_handler(setting_channel_choose_channel, state=user_state.Settings.ChooseSettingChannel)
	dp.register_callback_query_handler(setting_channel_public, state=user_state.Settings.SettingChannel, text='public')


	dp.register_callback_query_handler(formations_send_post_choose_my_post, state=user_state.Formation.SendPost, text='choose_my_post')
	dp.register_callback_query_handler(choose_my, state=user_state.Formation.SendPost, text_startswith='open_my_post')
	dp.register_callback_query_handler(formations_send_post_back, state=user_state.Formation.SendPost, text='back')
	dp.register_callback_query_handler(open_my_post_handler, state='*', text_startswith='open_my_post$')
	dp.register_callback_query_handler(delete_my_post_handler, state='*', text_startswith='delete_my_post')
	dp.register_callback_query_handler(back_to_my_post_handler, state='*', text_startswith='back_to_my_posts')

	# my points
	dp.register_message_handler(basket_handler, state='*', text='🛒 Корзина')
	dp.register_callback_query_handler(go_to_basket, state='*', text='go_to_basket')
	dp.register_callback_query_handler(add_basket_channel, state='*', text_startswith='add_basket_channel')
	dp.register_callback_query_handler(delete_all_basket_channels, state='*', text_startswith='delete_all_basket_channels')
	dp.register_callback_query_handler(load_basket_stat, state='*', text_startswith='load_basket_stat')
	dp.register_callback_query_handler(order_basket, state='*', text_startswith='order_basket')
	dp.register_callback_query_handler(open_basket_channel, state='*', text_startswith='open_basket_channel')
	dp.register_callback_query_handler(delete_basket_channel, state='*', text_startswith='delete_basket_channel')
	dp.register_callback_query_handler(back_to_basket, state='*', text_startswith='back_to_basket')
	dp.register_callback_query_handler(old_order_basket, state='*', text_startswith='go_post')
	dp.register_callback_query_handler(back_form_order, state='*', text='back_form_order')
	
	dp.register_callback_query_handler(bot_moder_post_yes, state='*', text_startswith='bot_moder_post_yes')
	dp.register_callback_query_handler(bot_moder_post_no, state='*', text_startswith='bot_moder_post_no')

	dp.register_message_handler(formations_send_post_adv, state=user_state.Formation.SendPost, content_types=types.ContentTypes.ANY)
	# dp.register_callback_query_handler(choose_my, state=user_state.Formation.SendPost, text_startswith='open_my_post')
	# dp.register_callback_query_handler(formations_send_post_choose_my_post, state=user_state.Formation.SendPost, text='choose_my_post')
	# dp.register_callback_query_handler(formations_send_post_back, state=user_state.Formation.SendPost, text='back')
	dp.register_message_handler(formations_send_post_send_text, state=user_state.EditModerationPost.SendText)
	dp.register_message_handler(formations_send_post_send_price, state=user_state.EditModerationPost.SendPrice)
	dp.register_message_handler(formations_send_post_send_keyboard, state=user_state.EditModerationPost.SendKeyboard, content_types=['text'])
	dp.register_message_handler(formations_send_post_send_media, state=user_state.EditModerationPost.SendMedia, content_types=types.ContentTypes.ANY)
	dp.register_callback_query_handler(formations_send_post_edit_text, state=user_state.Formation.SendPost, text='edit_text')
	dp.register_callback_query_handler(formations_send_post_edit_price, state=user_state.Formation.SendPost, text='edit_price')
	dp.register_callback_query_handler(formations_send_post_edit_media, state=user_state.Formation.SendPost, text='edit_media')
	dp.register_callback_query_handler(formations_send_post_edit_keyboard, state=user_state.Formation.SendPost, text='edit_keyboard')
	dp.register_callback_query_handler(formations_send_post_edit_next, state=user_state.Formation.SendPost, text='edit_next')
	dp.register_message_handler(formations_send_post_send_time, state=user_state.EditModerationPost.SendTime)
	dp.register_callback_query_handler(formations_send_post_back_to_time, state=user_state.EditModerationPost.SendTime, text='back_to_time')
	dp.register_callback_query_handler(formations_send_post_next, state=user_state.EditModerationPost.SendTime, text='next')
	dp.register_callback_query_handler(formations_send_post_change_postpone_date, state=user_state.EditModerationPost.SendTime, text_startswith='postpone_date$')

	dp.register_callback_query_handler(formations_send_post_with_ord, state=user_state.EditModerationPost.Main, text='with_ord')
	dp.register_callback_query_handler(formations_send_post_without_ord, state=user_state.EditModerationPost.Main, text='without_ord')

	dp.register_message_handler(formation_post_send_link, state=user_state.SendLink.SendLink, content_types=['text'])

	dp.register_callback_query_handler(my_advert_post_handler, state='*', text='my_advert_post')

	dp.register_message_handler(my_posts_handler, state='*', content_types=['text'], text='🔗 Мои посты')

	dp.register_callback_query_handler(add_my_post_handler, state='*', text='add_my_post')
	dp.register_message_handler(send_photo_post_handler, state=user_state.AddMyPost.SendPost, content_types=types.ContentTypes.ANY)
	dp.register_callback_query_handler(add_my_post_back, state=user_state.AddMyPost.SendPost, text='back')



	dp.register_message_handler(saved_handler, state='*', text='⭐️ Избранное')
	dp.register_callback_query_handler(open_saved_channel, state='*', text_startswith='open_saved_channel$')
	dp.register_callback_query_handler(delete_saved_channel, state='*', text_startswith='delete_saved_channel')
	dp.register_callback_query_handler(back_to_saved_channels, state='*', text_startswith='back_to_saved_channels')
	dp.register_callback_query_handler(my_ord_handler, state='*', text='my_ord')


	dp.register_message_handler(myself_cabinet_handler, state='*', text='👤 Личный кабинет')
	dp.register_callback_query_handler(placement_stat_handler, state='*', text='placement_stat')
	dp.register_callback_query_handler(back_to_cabinet_new, state=user_state.CabinetStats.Main, text='back')


	dp.register_message_handler(choose_cat_handler, state='*', text='🔎 Найти канал')
	dp.register_message_handler(find_by_cat, state='*', text='📚 По тематике')
	dp.register_message_handler(find_by_keyword, state='*', text='🔖 По ключевому слову')
	dp.register_message_handler(setting_filters, state='*', text='⚙️ По фильтрам')

	dp.register_message_handler(send_keyword, state=user_state.Find.SendKeyword)
	dp.register_callback_query_handler(open_find_channel, state=user_state.SendKeyword.ChooseChannel, text_startswith='open_find_channel')
	dp.register_callback_query_handler(back_to_find_channel, state=user_state.SendKeyword.ChooseChannel, text_startswith='back_to_find_channel')
	dp.register_callback_query_handler(change_page_to_find_channel, state='*', text_startswith='change_page_to_find_channel$')
	dp.register_callback_query_handler(back_page_to_find, state='*', text_startswith='back_page_to_find')

	dp.register_callback_query_handler(save_find_channel, state=user_state.SendKeyword.ChooseChannel, text_startswith='save_find_channel')
	dp.register_callback_query_handler(save_find_channel_start, state='*', text_startswith='save_find_channel')

	dp.register_callback_query_handler(basket_find_channel, state=user_state.SendKeyword.ChooseChannel, text_startswith='basket_find_channel')
	dp.register_callback_query_handler(basket_find_channel_start, state='*', text_startswith='basket_find_channel')


	dp.register_callback_query_handler(change_page_to_find_adv, state='*', text_startswith='change_page_to_find_adv$')
	dp.register_callback_query_handler(choose_cat_to_find_adv, state='*', text_startswith='choose_cat_to_find_adv$')


	dp.register_callback_query_handler(filter_err, state=user_state.SettingFilters.Main, text='filter_err')
	dp.register_callback_query_handler(filter_views, state=user_state.SettingFilters.Main, text='filter_views')
	dp.register_callback_query_handler(filter_sub, state=user_state.SettingFilters.Main, text='filter_sub')
	dp.register_callback_query_handler(filter_show_result, state=user_state.SettingFilters.Main, text='filter_show_result')
	dp.register_callback_query_handler(back_to_filters, state=user_state.SettingFilters, text='back_to_filters')
	dp.register_callback_query_handler(filters_err, state=user_state.SettingFilters.SetERR, text_startswith='filters_err$')
	dp.register_message_handler(filters_views, state=user_state.SettingFilters.SetView)
	dp.register_message_handler(filters_sub, state=user_state.SettingFilters.SetSub)


	dp.register_callback_query_handler(setting_channel_application_manage, state=user_state.Settings.SettingChannel, text='application_manage')
	dp.register_callback_query_handler(setting_channel_moderation_manage, state=user_state.Settings.SettingChannel, text='moderation_manage')
	dp.register_callback_query_handler(setting_channel_manager_manage, state=user_state.Settings.SettingChannel, text='manager_manage')
	dp.register_callback_query_handler(setting_channel_moderation_manage_back, state=user_state.ModerationManage.Main, text='back')
	dp.register_callback_query_handler(setting_channel_redactor_manage, state=user_state.Settings.SettingChannel, text='redactor_manage')
	dp.register_callback_query_handler(setting_channel_redactor_manage_back, state=[user_state.ModerationManage.Main, user_state.ManagerManage.Main], text='back')
	dp.register_callback_query_handler(redactor_manage_create_moder_back, state=user_state.ModerationManage.SendRedactor, text='back')
	dp.register_callback_query_handler(redactor_manage_create_manager_back, state=user_state.ManagerManage.SendRedactor, text='back')
	dp.register_callback_query_handler(redactor_manage_create_moder_back, state=user_state.ModerationManage.OpenRedactor, text='back')
	dp.register_message_handler(redactor_manage_create_moder, state=user_state.ModerationManage.SendRedactor, content_types=["text", "photo", "video"])
	dp.register_message_handler(redactor_manage_create_manager, state=user_state.ManagerManage.SendRedactor, content_types=["text", "photo", "video"])
	dp.register_message_handler(redactor_manage_create_manager_requisites, state=user_state.ManagerManage.SendRequisites, content_types=["text"])
	dp.register_callback_query_handler(setting_channel_support, state=user_state.Settings.SettingChannel, text='support')
	dp.register_callback_query_handler(setting_channel_auto_write, state=user_state.Settings, text='auto_write')
	dp.register_message_handler(setting_channel_auto_write_send, state=user_state.Settings.SendAutoWrite)
	dp.register_callback_query_handler(setting_channel_auto_approve, state=user_state.Settings.Public, text='auto_approve')
	dp.register_callback_query_handler(setting_channel_collect_orders, state=user_state.Settings, text='collect_orders')
	dp.register_callback_query_handler(setting_channel_full_approve, state=user_state.Settings, text='full_approve')
	dp.register_callback_query_handler(setting_channel_water_mark, state=user_state.Settings, text='water_mark')
	dp.register_callback_query_handler(setting_channel_hour_line, state=user_state.Settings, text='hour_line')
	dp.register_callback_query_handler(setting_channel_reactions, state=user_state.Settings, text='reactions')
	dp.register_message_handler(setting_channel_reactions_end, state=user_state.Settings.SendReactions)
	dp.register_callback_query_handler(setting_channel_preview, state=user_state.Settings, text='preview')
	dp.register_callback_query_handler(setting_channel_point, state=user_state.Settings, text='point')
	dp.register_callback_query_handler(setting_channel_time_zone, state=user_state.Settings.SettingChannel, text_startswith='time_zone')
	dp.register_callback_query_handler(setting_channel_post_without_sound, state=user_state.Settings, text='post_without_sound')
	dp.register_callback_query_handler(change_links, state='*', text='change_links')
	dp.register_callback_query_handler(redactor_manage_open_moder, state=user_state.ModerationManage.Main, text_startswith='open_moder')
	dp.register_callback_query_handler(manager_manage_open_moder, state=user_state.ManagerManage.Main, text_startswith='open_manager')
	dp.register_callback_query_handler(redactor_manage_delete_moder, state=user_state.ModerationManage.OpenRedactor, text_startswith='delete_moder')
	dp.register_callback_query_handler(redactor_manage_delete_manag, state=user_state.ManagerManage.OpenRedactor, text_startswith='delete_manag')
	dp.register_callback_query_handler(redactor_manage_edit_rate_manag, state=user_state.ManagerManage.OpenRedactor, text_startswith='edit_manag_rate')
	dp.register_callback_query_handler(redactor_manage_edit_req_manag, state=user_state.ManagerManage.OpenRedactor, text_startswith='edit_manag_req')
	dp.register_callback_query_handler(setting_channel_manager_manage, state=user_state.ManagerManage.OpenRedactor, text_startswith='back')

	dp.register_message_handler(send_redactor_manage_edit_rate_manag, state=user_state.ManagerManage.EditRate, content_types=['text'])
	dp.register_message_handler(send_redactor_manage_edit_req_manag, state=user_state.ManagerManage.EditRequisites, content_types=['text'])

	dp.register_callback_query_handler(back_redactor_manage_edit_manag, state=[
		user_state.ManagerManage.EditRequisites,
		user_state.ManagerManage.EditRate
		], text='back')


	dp.register_callback_query_handler(moderation_manage_categories_choose, state=user_state.ModerationManage.ChooseCat, text_startswith='choose_cat_to_confirm')
	dp.register_callback_query_handler(moderation_manage_choose_confirmer, state=user_state.ModerationManage.ChooseConfirmer, text_startswith='choose_moder_to_confirm')
	dp.register_callback_query_handler(moderation_manage_categories_back, state=user_state.ModerationManage.ChooseCat, text_startswith='back')
	dp.register_callback_query_handler(moderation_manage_categories_back, state=user_state.ModerationManage.ChooseConfirmer, text_startswith='back')
	dp.register_callback_query_handler(moderation_manage_categories_change_page, state=user_state.ModerationManage.ChooseCat, text_startswith='change_page_to_confirm')
	dp.register_message_handler(change_links_send_post, state=user_state.ChangeLinks.SendPost, content_types=['photo', 'video'])
	dp.register_callback_query_handler(change_links_send_post_back, state=user_state.ChangeLinks.SendPost, text='back')
	dp.register_message_handler(change_links_send_text_post, state=user_state.ChangeLinks.SendPost, content_types=['text'])
	dp.register_message_handler(change_links_send_link, state=user_state.ChangeLinks.SendLink)
	dp.register_callback_query_handler(click_reaction_handler, text_startswith='click_reaction')
	dp.register_callback_query_handler(moder_post_yes, state='*', text_startswith='moder_post_yes')
	dp.register_callback_query_handler(moder_post_no, state='*', text_startswith='moder_post_no')
	dp.register_callback_query_handler(moder_post_time, state='*', text_startswith='moder_post_time')
	dp.register_message_handler(send_mail, content_types=types.ContentTypes.ANY, state=user_state.Admin.SendMail)	
	dp.register_message_handler(send_block, content_types=['text'], state=user_state.Admin.SendBlock)	
	dp.register_callback_query_handler(send_block_back, text='back', state=user_state.Admin.SendBlock)	
	dp.register_callback_query_handler(send_block_back, text='back', state=user_state.Admin.SendMail)	
	# dp.register_message_handler(pre_fire_send_text_post_handler, state='*', content_types=['text'])
	dp.register_message_handler(pre_fire_send_photo_post_handler, lambda message: message.chat.type == 'private', state='*', content_types=types.ContentTypes.ANY)
	dp.register_callback_query_handler(pre_fire_choose_channel_send_post_handler, state=user_state.AddPost.SendPost, text_startswith='pre_choose_channel')
	dp.register_chat_join_request_handler(new_join_channel)
	dp.register_callback_query_handler(just_delete, state="*", text='back')







