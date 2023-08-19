import os

import petrovna
from aiogram.dispatcher import FSMContext

from aiogram import types
from aiogram.types import InputFile

import tinkoff.main
from bot.start_semi_bot import bot
from bot.start_bot import bot as admin_bot
from bot_data import config
from db.models import *
from keyboards import inline
from keyboards_admin import reply
from states import admin as admin_state
from states import user as user_state

from handlers.admin import TEXTS
from handlers.user import utils as user_utils
from handlers.admin import utils as admin_utils

from keyboards.reply import start_offer_access

from db import functions as db

ADMIN_IDS = [2134081408, 5899041406]

async def start_handler(message: types.Message, state: FSMContext):
	pam = message.text.split()
	await state.finish()
	if len(pam) == 2:
		pam = pam[1][1:]
		channel_code = ChannelCode.get(code=pam)
		channel_id = channel_code.channel_id
		print(channel_id)
		channel = FindChannel.get(channel_id=channel_id)
		await message.answer(TEXTS.find_channel_form(channel),
										reply_markup=inline.start_channel(message.from_user.id, channel.id))
		return

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
	await message.answer(TEXTS.choose_cat, reply_markup=reply.choose_cat())


async def all_price_handler(message: types.Message, state: FSMContext):
	pass


async def saved_handler(message: types.Message, state: FSMContext):
	channels = Saved.select().where(Saved.user_id == message.from_user.id)
	current_directory = os.getcwd()
	photo = InputFile(path_or_bytesio=f'{current_directory}/images/saved.png')
	await message.answer_photo(photo, reply_markup=inline.my_saved(channels))


async def myself_cabinet_handler(message: types.Message, state: FSMContext):
	current_directory = os.getcwd()
	photo = InputFile(path_or_bytesio=f'{current_directory}/images/cabinet.jpg')
	await message.answer_photo(photo, reply_markup=inline.myself_cabinet())


async def swap_links(message: types.Message, state: FSMContext):
	await message.answer(TEXTS.change_links_start, reply_markup=inline.only_back())
	await user_state.ChangeLinks.SendPost.set()


async def basket_handler(message: types.Message, state: FSMContext):
	basket = Basket.select().where(Basket.user_id == message.from_user.id)
	basket = [FindChannel.get(id=b.find_channel_id) for b in basket]
	current_directory = os.getcwd()
	basket_photo = InputFile(path_or_bytesio=f'{current_directory}/images/basket.jpg')
	await message.answer_photo(basket_photo, reply_markup=inline.basket(basket))

async def go_to_basket(call: types.CallbackQuery, state:  FSMContext):
	await state.finish()
	basket = Basket.select().where(Basket.user_id == call.from_user.id)
	basket = [FindChannel.get(id=b.find_channel_id) for b in basket]

	await call.message.delete()
	current_directory = os.getcwd()
	basket_photo = InputFile(path_or_bytesio=f'{current_directory}/images/basket.jpg')
	await call.message.answer_photo(basket_photo, reply_markup=inline.basket(basket))

async def back_form_order(call: types.CallbackQuery, state:  FSMContext):
	await state.finish()
	basket = Basket.select().where(Basket.user_id == call.from_user.id)
	basket = [FindChannel.get(id=b.find_channel_id) for b in basket]
	current_directory = os.getcwd()
	basket_photo = InputFile(path_or_bytesio=f'{current_directory}/images/basket.jpg')
	await call.message.delete()
	await call.message.answer_photo(basket_photo, reply_markup=inline.basket(basket))


async def back_handler(call: types.CallbackQuery, state: FSMContext):
	await call.message.delete()
	await call.message.answer(TEXTS.old_start, reply_markup=reply.main_keyboard())


async def find_by_cat(message: types.Message, state: FSMContext):
	await message.answer('Выберите категорию', reply_markup=inline.choose_cat())


async def find_by_keyword(message: types.Message, state: FSMContext):
	await user_state.Find.SendKeyword.set()
	await message.answer('Введите название канала или слово для поиска')


async def choose_cat_to_find(call: types.CallbackQuery, state: FSMContext):
	await state.finish()
	cat = int(call.data.split('$')[1])

	channels = FindChannel.select().where(FindChannel.category == cat)

	if not channels:
		await call.message.answer('Каналов не найдено')
		return

	await user_state.SendKeyword.ChooseChannel.set()
	await state.update_data(channels=list(channels), type='category')

	await call.message.edit_text(TEXTS.choose_channel, reply_markup=inline.choose_find_channel(channels))


async def change_page_to_find(call: types.CallbackQuery, state: FSMContext):
	page = int(call.data.split('$')[1])
	await call.message.edit_reply_markup(reply_markup=inline.choose_cat(page))


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
		await call.message.edit_text('Выберите категорию', reply_markup=inline.choose_cat())
	elif type == 'keyword':
		await call.message.delete()
		await user_state.Find.SendKeyword.set()
		await call.message.answer('Введите название канала или слово для поиска')
	elif type == 'filters':
		await user_state.SettingFilters.Main.set()
		await state.update_data(data)
		await call.message.edit_text(TEXTS.setting_filters(data=data), reply_markup=inline.setting_filters())


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

async def setting_filters(message: types.Message, state: FSMContext):
	await user_state.SettingFilters.Main.set()
	await message.answer(TEXTS.setting_filters(), reply_markup=inline.setting_filters())

async def go_to_ordering(message: types.Message, state: FSMContext):
	channels = Basket.select().where(Basket.user_id == message.from_user.id)

	if len(channels) == 0:
		await message.answer('Ваша корзина пуста!')
		return

	await message.answer(f'Оформление для {len(channels)} каналов')
	await message.answer(f'Пришлите рекламный пост')

	await user_state.Formation.SendPost.set()

async def formation_send_post(message: types.Message, state: FSMContext):
	await state.finish()
	await user_state.SendLink.SendLink.set()
	await state.update_data(post_id=message.message_id, channel_number=0, links=[])
	channels = Basket.select().where(Basket.user_id == message.from_user.id)
	data = await state.get_data()
	await message.answer(TEXTS.get_link_form(FindChannel.get(id=channels[data['channel_number']].find_channel_id)))

async def formation_post_send_link(message: types.Message, state: FSMContext):
	link = message.text
	if not ('https://' in link or 'http://' in link):
		await message.answer('Это не ссылка!')
		return
	channels = Basket.select().where(Basket.user_id == message.from_user.id)
	data = await state.get_data()
	data['links'].append(link)
	channel_number = data['channel_number'] + 1
	i = 0
	if channel_number == len(channels):
		for c in channels:
			channel = Channel.get_or_none(channel_id=c.find_channel_id)
			try:
				if channel:
					await admin_bot.send_message(channel.admin_id, f"<b>Здесь будет пост</b>\n\nСсылка: <code>{data['links'][i]}</code>")
					await admin_bot.send_message(channel.admin_id, f"Модерация", reply_markup=inline.moder_post())
				else:
					await admin_bot.send_message(2134081408, f"<b>Здесь будет пост</b>\n\nСсылка: <code>{data['links'][i]}</code>")
					await admin_bot.send_message(2134081408, f"Модерация", reply_markup=inline.moder_post())
			except Exception as e:
				print(e)
			i += 1
		await state.finish()
		await message.answer('Пост получен и отправлен на согласование')
		await message.answer('Выберите способ оплаты', reply_markup=inline.choose_payment_type())
		print(data['links'])
		return

	await state.update_data(channel_number=channel_number, links=data['links'] + [link])
	await message.answer(TEXTS.get_link_form(FindChannel.get(id=channels[channel_number].find_channel_id)))


async def old_formation_send_post(message: types.Message, state: FSMContext):
	await state.finish()
	await message.answer('Пост получен и отправлен на согласование')
	await message.answer('Выберите способ оплаты', reply_markup=inline.choose_payment_type())

async def load_stat_choosen_channels(message: types.Message, state: FSMContext):
	channels = Basket.select().where(Basket.user_id == message.from_user.id)
	if len(channels) == 0:
		await message.answer('Ваша корзина пуста!')
		return

	await message.answer('<b>Статистика выбранных каналов:</b>')
	for basket in channels:
		channel = FindChannel.get(id=basket.find_channel_id)
		await message.answer(TEXTS.find_channel_form(channel))

async def add_some_channels(message: types.Message, state: FSMContext):
	pass

async def change_links(message: types.Message, state: FSMContext):
	await message.answer(TEXTS.change_links_start, reply_markup=inline.only_back())
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
	await message.answer(TEXTS.send_link, reply_markup=reply.only_home())

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
	link = message.html_text
	if link == '🏠 В меню':
		await start_handler(message, state)
		return
	if not('https://t.me/' in link):
		await message.answer('Это не ссылка!')
		return
	data = await state.get_data()

	text = user_utils.swap_links_in_text(data.get('text'), link)
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
				# 	media.attach_photo(bot_data['media'][i], bot_data['text'])
				# except Exception as e:
				# 	media.attach_video(bot_data['media'][i], bot_data['text'])
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

async def open_find_channel(call: types.CallbackQuery, state: FSMContext):
	channel = FindChannel.get(id=int(call.data.split('$')[1]))
	await call.message.edit_text(TEXTS.find_channel_form(channel), reply_markup=inline.back_to_find_channel(call.from_user.id, channel.id))

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


async def back_to_find_channel(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	channels = data['channels']

	await call.message.edit_text(TEXTS.choose_channel, reply_markup=inline.choose_find_channel(channels))

async def open_saved_channel(call: types.CallbackQuery, state: FSMContext):
	channel = FindChannel.get(id=int(call.data.split('$')[1]))
	b = Basket.select().where(Basket.find_channel_id == channel.id)
	resp = 0
	for i in b:
		if i.user_id == call.from_user.id:
			resp = i.id
	await call.message.edit_caption(TEXTS.find_channel_form(channel), reply_markup=inline.back_to_saved_channel(resp))

async def delete_saved_channel(call: types.CallbackQuery, state: FSMContext):
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

async def payments_card(call: types.CallbackQuery, state: FSMContext):
	saved = Basket.select().where(Basket.user_id == call.from_user.id)
	amount = 0
	for i in saved:
		c = FindChannel.get(id=i.find_channel_id)
		amount += c.base_price

	order = tinkoff.main.create_order(amount=amount)

	t = TinkoffOrder.create(user_id=call.from_user.id, order_id=order['OrderId'], payment_id=order['PaymentId'])
	t.save()
	await call.message.edit_text(TEXTS.card_message, reply_markup=inline.order_keyboard(order['PaymentURL']))

async def payments_bill(call: types.CallbackQuery, state: FSMContext):
	await user_state.Payments.SendINN.set()
	await call.message.delete()
	await call.message.answer('Введите ИНН')

async def payments_send_inn(message: types.Message, state: FSMContext):
	if petrovna.validate_inn(message.text):
		await state.finish()
		await message.answer('Успешно добавлено!\n\nПосле одобрение администраторами вам прийдет счет')
		for i in ADMIN_IDS:
			await bot.send_message(i, f'Требуется подтверждение\n\nИНН: {message.text}', reply_markup=inline.valid_inn(message.from_user.id))
	else:
		await message.answer('Невалидный ИНН')


async def valid_inn(call: types.CallbackQuery, state: FSMContext):
	user_id = int(call.data.split('$')[1])
	saved = Basket.select().where(Basket.user_id == user_id)
	amount = 0
	for i in saved:
		c = FindChannel.get(id=i.find_channel_id)
		amount += c.base_price

	order = tinkoff.main.create_order(amount=amount)

	t = TinkoffOrder.create(user_id=user_id, order_id=order['OrderId'], payment_id=order['PaymentId'])
	t.save()
	await call.message.edit_text(TEXTS.card_message, reply_markup=inline.order_keyboard(order['PaymentURL']))

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

	err = data.get('err')
	views = data.get('views')
	sub = data.get('sub')

	if not(err or views or sub):
		await call.message.answer('Установите хотя бы 1 фильтр')
		return

	channels = FindChannel.select()
	resp = []

	for channel in channels:
		flag = True
		if err:
			channel_err = round(100 * channel.views / channel.subscribers, 1)
			print(channel_err)
			print((err-1) * 20)
			if not((err-1) * 20 < channel_err < (err) * 20):
				flag = False
				continue
		if views:
			if not(views[0] < channel.views < views[0]):
				flag = False
				continue

		if sub:
			if not(sub[0] < channel.subscribers < sub[0]):
				flag = False
				continue

		if flag:
			resp.append(channel)

	await user_state.SendKeyword.ChooseChannel.set()
	await state.update_data(data, channels=list(resp), type='filters')

	await call.message.edit_text(TEXTS.choose_channel, reply_markup=inline.choose_find_channel(resp))



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

async def add_basket_channel(call: types.CallbackQuery, state: FSMContext):
	await call.message.delete()
	await call.message.answer(TEXTS.choose_cat, reply_markup=reply.choose_cat())


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
	for basket in channels:
		channel = FindChannel.get(id=basket.find_channel_id)
		await call.message.answer(TEXTS.find_channel_form(channel))

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

async def old_order_basket(call: types.CallbackQuery, state: FSMContext):
	channels = Basket.select().where(Basket.user_id == call.from_user.id)

	if len(channels) == 0:
		await call.message.answer('Ваша корзина пуста!')
		return

	await call.message.delete()
	await call.message.answer(f'<b>Оформление для {len(channels)} каналов</b>')
	await call.message.answer(f'<b>Пришлите рекламный пост</b>')

	await user_state.Formation.SendPost.set()

async def change_basket_page(call: types.CallbackQuery, state: FSMContext):
	page = int(call.data.split('$')[1])
	channels = Basket.select().where(Basket.user_id == call.from_user.id)
	await call.message.edit_reply_markup(reply_markup=inline.basket(channels, page))

async def open_basket_channel(call: types.CallbackQuery, state: FSMContext):
	channel = FindChannel.get(id=int(call.data.split('$')[1]))
	await call.message.edit_caption(TEXTS.find_channel_form(channel), reply_markup=inline.choose_basket_channel(channel.id))

async def back_to_basket(call: types.CallbackQuery, state: FSMContext):
	channels = Basket.select().where(Basket.user_id == call.from_user.id)
	basket = [FindChannel.get(id=b.find_channel_id) for b in channels]
	await call.message.edit_caption('', reply_markup=inline.basket(basket))

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

async def update_stat(message: types.Message, state: FSMContext):
	channels = FindChannel.select()
	for c in channels:
		chat = await bot.get_chat(c.link)
		print(chat)

async def time_handler(message: types.Message, state: FSMContext):
	from bs4 import BeautifulSoup
	import random
	soup = BeautifulSoup(message.html_text, 'html.parser')

	a = soup.find('a')
	if not a:
		return
	link = a['href']
	name = message.text.split('Токен')[1].split('Описание')[0].strip()
	creater = message.text.split('Автор:')[1].split('🔹 Блокчейн')[0].strip()
	blockchain = message.text.split('Блокчейн: ')[1].split('💸 Цена')[0].strip()
	price = (int(round(float(message.text.split('Цена: ')[1].split('$')[0].strip()))) % 1000) + random.choice([0, 1000])
	await message.answer(f'{name}-{creater}-{blockchain}-{link}-{price}')
	print(name, creater, blockchain, price, link)
	print(name)
	print(message.html_text)

async def update_tg_stat(message: types.Message, state: FSMContext):
	admin_utils.update_tg_stat()
	await message.answer('Готово!')

async def my_posts_handler(call: types.CallbackQuery, state: FSMContext):
	posts = MyPost.select().where(MyPost.user_id == call.from_user.id)
	await user_state.CabinetStats.Main.set()
	await call.message.edit_caption(TEXTS.my_posts, reply_markup=inline.my_posts(posts))


async def add_my_post_handler(call: types.CallbackQuery, state: FSMContext):
	await user_state.AddMyPost.SendPost.set()
	await state.update_data(date=None, media=[], reply_markup=None, text='')
	await call.message.answer(TEXTS.send_my_post, reply_markup=inline.only_back())

async def add_my_post_back(call: types.CallbackQuery, state: FSMContext):
	await user_state.CabinetStats.Main.set()
	await call.message.delete()


async def placement_stat_handler(call: types.CallbackQuery, state: FSMContext):
	placements = Placement.select().where(Placement.user_id == call.from_user.id)
	await user_state.CabinetStats.Main.set()
	await call.message.edit_caption(TEXTS.placements_stat(placements), reply_markup=inline.only_back())


async def payment_data_handler(call: types.CallbackQuery, state: FSMContext):
	await user_state.CabinetPaymentData.Main.set()
	await call.message.edit_reply_markup(reply_markup=inline.cabinet_payment_data_keyboard())


async def phys_person(call: types.CallbackQuery, state: FSMContext):
	await user_state.SelfPerson.Main.set()
	await call.message.edit_reply_markup(reply_markup=inline.add_card_number())


async def self_employed(call: types.CallbackQuery, state: FSMContext):
	await user_state.SelfPerson.Main.set()
	await call.message.edit_reply_markup(reply_markup=inline.add_card_number_ORD())


async def IPOOO(call: types.CallbackQuery, state: FSMContext):
	await user_state.SelfPerson.Main.set()
	await call.message.edit_reply_markup(reply_markup=inline.add_INN_ORD())

async def self_person_add_card(call: types.CallbackQuery, state: FSMContext):
	await user_state.SelfPerson.SendCardNumber.set()
	print('UPDATE_STATE')
	await call.message.answer(TEXTS.send_card_number, reply_markup=inline.only_back())

async def self_person_back(call: types.CallbackQuery, state: FSMContext):
	print('LOGGER')
	print(f'STATE: {state.get_state()}')
	await user_state.CabinetPaymentData.Main.set()
	await call.message.edit_reply_markup(reply_markup=inline.cabinet_payment_data_keyboard())

async def self_person_send_card_back(call: types.CallbackQuery, state: FSMContext):
	await user_state.CabinetPaymentData.Main.set()
	await call.message.delete()

async def self_person_send_card(message: types.Message, state: FSMContext):
	await message.answer('Готово')
	await user_state.CabinetPaymentData.Main.set()
	db.update_admin(admin_id=message.from_user.id, card_number=message.text)
	await user_state.CabinetPaymentData.Main.set()
	current_directory = os.getcwd()
	photo = InputFile(path_or_bytesio=f'{current_directory}/images/cabinet.jpg')
	await message.answer_photo(photo, reply_markup=inline.myself_cabinet())

async def self_person_add_ORD(call: types.CallbackQuery, state: FSMContext):
	pass

async def self_person_send_ORD(message: types.Message, state: FSMContext):
	pass

async def self_person_add_INN(call: types.CallbackQuery, state: FSMContext):
	pass

async def self_person_send_INN(message: types.Message, state: FSMContext):
	pass

async def back_to_cabinet(call: types.CallbackQuery, state: FSMContext):
	await state.finish()
	await call.message.edit_reply_markup(reply_markup=inline.myself_cabinet())

async def back_to_cabinet_new(call: types.CallbackQuery, state: FSMContext):
	await state.finish()
	await call.message.delete()
	current_directory = os.getcwd()
	photo = InputFile(path_or_bytesio=f'{current_directory}/images/cabinet.jpg')
	await call.message.answer_photo(photo, reply_markup=inline.myself_cabinet())


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
			pass
			# try:
			# 	await message.answer_photo(data['media'][0], caption=data['text'], reply_markup=markup)
			# except Exception as e:
			# 	await message.answer_video(data['media'][0], caption=data['text'], reply_markup=markup)

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
					# 	media.attach_photo(bot_data['media'][i], bot_data['text'])
					# except Exception as e:
					# 	media.attach_video(bot_data['media'][i], bot_data['text'])
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
					# 	media.attach_photo(bot_data['media'][i])
					# except Exception as e:
					# 	media.attach_video(bot_data['media'][i])

			print('SEND')

			# await message.answer_media_group(media)
		post_media = ''
		for i in data['media']:
			post_media += f'{i}$'
		post_media = post_media[:-1]
		post = Post.create()
		post.owner_id = message.from_user.id
		post.media = post_media
		post.text = data['text']
		post.keyboard_id = user_utils.create_keyboard(data['reply_markup']) if data['reply_markup'] else None
		post.save()
		my_post = MyPost.create(user_id=message.from_user.id, post_id=post.id)
		my_post.save()
		await message.answer('Готово')
		await state.finish()
		current_directory = os.getcwd()
		photo = InputFile(path_or_bytesio=f'{current_directory}/images/cabinet.jpg')
		posts = MyPost.select().where(MyPost.user_id == message.from_user.id)
		await user_state.CabinetStats.Main.set()
		await message.answer_photo(photo, TEXTS.my_posts, reply_markup=inline.my_posts(posts))
		#await message.answer(TEXTS.album_edit, disable_web_page_preview=True)

async def send_text_post_handler(message: types.Message, state: FSMContext):
	await state.update_data(active=True, text=message.html_text, reply_markup=inline.rewrite_keyboard(message.reply_markup))
	data = await state.get_data()
	post = Post.create()
	post.owner_id = message.from_user.id
	post.text = data['text']
	post.keyboard_id = user_utils.create_keyboard(data['reply_markup']) if data['reply_markup'] else None
	post.save()
	my_post = MyPost.create(user_id=message.from_user.id, post_id=post.id)
	my_post.save()
	await message.answer('Готово')
	await state.finish()
	current_directory = os.getcwd()
	photo = InputFile(path_or_bytesio=f'{current_directory}/images/cabinet.jpg')
	posts = MyPost.select().where(MyPost.user_id == message.from_user.id)
	await user_state.CabinetStats.Main.set()
	await message.answer_photo(photo, TEXTS.my_posts, reply_markup=inline.my_posts(posts))
	# markup = inline.add_markup_send_post(data['reply_markup'])
	# await message.answer(data['text'], reply_markup=markup, disable_web_page_preview=True)

async def open_my_post_handler(call: types.CallbackQuery, state: FSMContext):
	await call.message.delete()
	my_post = MyPost.get(id=int(call.data.split('$')[1]))
	post = Post.get(id=my_post.post_id)
	media = post.media.split('$') if post.media else None
	markup = inline.from_db_to_markup_by_key_id(post.keyboard_id)
	if media:
		if len(media) == 1:
			try:
				mes_2 = await call.message.answer_photo(media[0], caption=post.text, reply_markup=markup)
			except Exception as e:
				mes_2 = await call.message.answer_video(media[0], caption=post.text, reply_markup=markup)
			await state.update_data(messages_to_delete=[mes_2.message_id])


		else:
			data_media = media
			media = types.MediaGroup()
			for i in range(len(data_media)):
				if i == len(data_media) - 1:
					try:
						print('photo is')
						mes = await bot.send_photo(config.TRASH_CHANNEL_ID, data_media[i])
						type = 'photo'

					except Exception as e:
						print('Except')
						mes = await bot.send_video(config.TRASH_CHANNEL_ID, data_media[i])
						type = 'video'

					if type == 'photo':
						media.attach_photo(data_media[i], caption=post.text)
					elif type == 'video':
						media.attach_video(data_media[i], caption=post.text)

				# try:
				# 	media.attach_photo(bot_data['media'][i], bot_data['text'])
				# except Exception as e:
				# 	media.attach_video(bot_data['media'][i], bot_data['text'])
				else:
					try:
						print('photo is')
						mes = await bot.send_photo(config.TRASH_CHANNEL_ID, data_media[i])
						type = 'photo'

					except Exception as e:
						print('Except')
						mes = await bot.send_video(config.TRASH_CHANNEL_ID, data_media[i])
						type = 'video'

					if type == 'photo':
						media.attach_photo(data_media[i])
					elif type == 'video':
						media.attach_video(data_media[i])

			mes_1 = await call.message.answer_media_group(media)
			await state.update_data(messages_to_delete=[mes_1[0].message_id, len(data_media)])
	else:
		mes_1 = await call.message.answer(post.text, reply_markup=markup)
		await state.update_data(messages_to_delete=[mes_1.message_id])

	await call.message.answer('myPostPanel', reply_markup=inline.my_post_panel(my_post.id))


async def delete_my_post_handler(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()

	my_post = MyPost.get(id=int(call.data.split('$')[1]))
	my_post.delete_instance()

	if len(data['messages_to_delete']) == 1:
		try:
			await bot.delete_message(call.from_user.id, data['messages_to_delete'][0])
		except Exception as e:
			pass
	else:
		for i in range(data['messages_to_delete'][1]):
			try:
				await bot.delete_message(call.from_user.id, data['messages_to_delete'][0] - i)
			except Exception as e:
				pass
	await state.finish()
	await call.message.delete()
	current_directory = os.getcwd()
	photo = InputFile(path_or_bytesio=f'{current_directory}/images/cabinet.jpg')
	posts = MyPost.select().where(MyPost.user_id == call.from_user.id)
	await user_state.CabinetStats.Main.set()
	await call.message.answer_photo(photo, TEXTS.my_posts, reply_markup=inline.my_posts(posts))

async def back_to_my_post_handler(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()

	if len(data['messages_to_delete']) == 1:
		try:
			await bot.delete_message(call.from_user.id, data['messages_to_delete'][0])
		except Exception as e:
			pass
	else:
		for i in range(data['messages_to_delete'][1]):
			try:
				await bot.delete_message(call.from_user.id, data['messages_to_delete'][0]-i)
			except Exception as e:
				pass
	await state.finish()
	await call.message.delete()
	current_directory = os.getcwd()
	photo = InputFile(path_or_bytesio=f'{current_directory}/images/cabinet.jpg')
	posts = MyPost.select().where(MyPost.user_id == call.from_user.id)
	await user_state.CabinetStats.Main.set()
	await call.message.answer_photo(photo, TEXTS.my_posts, reply_markup=inline.my_posts(posts))

def register_admin_handlers(dp):
	# dp.register_message_handler(time_handler, state='*')
	dp.register_message_handler(start_handler, commands=['start', 'restart'], state='*')
	dp.register_message_handler(update_tg_stat, commands=['update_tg_stat', 'updatetgstat'], state='*')
	dp.register_message_handler(update_stat, commands=['stat', 'restart'], state='*')
	dp.register_message_handler(send_answer_start_offer_access,
								state=admin_state.SendSmallAnswer.sendAnswerStartOfferAccess)
	dp.register_message_handler(change_links, state='*', text='change_links')
	dp.register_message_handler(change_links_send_post, state=user_state.ChangeLinks.SendPost,
								content_types=['photo', 'video'])
	dp.register_callback_query_handler(change_links_send_post_back, state=user_state.ChangeLinks.SendPost, text='back')
	dp.register_message_handler(change_links_send_text_post, state=user_state.ChangeLinks.SendPost,
								content_types=['text'])
	dp.register_message_handler(formation_post_send_link, state=user_state.SendLink.SendLink,
								content_types=['text'])
	dp.register_message_handler(change_links_send_link, state=user_state.ChangeLinks.SendLink)
	dp.register_message_handler(write_support, state='*', text='👩‍💻 Написать нам')
	dp.register_message_handler(choose_cat_handler, state='*', text='🔎 Найти канал')
	dp.register_message_handler(all_price_handler, state='*', text='ВЕСЬ ПРАЙС')
	dp.register_message_handler(saved_handler, state='*', text='⭐️ Избранное')
	dp.register_message_handler(myself_cabinet_handler, state='*', text='👤 Личный кабинет')
	dp.register_message_handler(swap_links, state='*', text='🔗 Замена ссылок')
	dp.register_message_handler(basket_handler, state='*', text='🛒 Корзина')
	dp.register_message_handler(start_handler, state='*', text=['В меню', '🏠 В меню'])
	dp.register_message_handler(find_by_cat, state='*', text='📚 По тематике')
	dp.register_message_handler(find_by_keyword, state='*', text='🔖 По ключевому слову')
	dp.register_message_handler(setting_filters, state='*', text='⚙️ По фильтрам')
	dp.register_message_handler(go_to_ordering, state='*', text='Перейти к оформлению')
	dp.register_message_handler(load_stat_choosen_channels, state='*', text='Загрузить статистику выбранных каналов')
	dp.register_message_handler(choose_cat_handler, state='*', text='Добавить еще каналы')
	dp.register_message_handler(send_keyword, state=user_state.Find.SendKeyword)
	dp.register_message_handler(formation_send_post, state=user_state.Formation.SendPost)
	dp.register_message_handler(payments_send_inn, state=user_state.Payments.SendINN)
	dp.register_callback_query_handler(payment_data_handler, state='*', text='payment_data')
	dp.register_callback_query_handler(my_posts_handler, state='*', text='my_posts')
	dp.register_callback_query_handler(add_my_post_handler, state='*', text='add_my_post')
	dp.register_callback_query_handler(placement_stat_handler, state='*', text='placement_stat')
	dp.register_callback_query_handler(phys_person, state=user_state.CabinetPaymentData.Main, text='phys-person')
	dp.register_callback_query_handler(self_employed, state=user_state.CabinetPaymentData.Main, text='self-employed')
	dp.register_callback_query_handler(IPOOO, state=user_state.CabinetPaymentData.Main, text='IPOOO')
	dp.register_callback_query_handler(back_to_cabinet, state=user_state.CabinetPaymentData.Main, text='back')
	dp.register_callback_query_handler(back_to_cabinet_new, state=user_state.CabinetStats.Main, text='back')
	dp.register_callback_query_handler(add_my_post_back, state=user_state.AddMyPost.SendPost, text='back')
	dp.register_callback_query_handler(self_person_send_card_back, state=user_state.SelfPerson.SendCardNumber, text='back')
	dp.register_callback_query_handler(self_person_back, state=user_state.SelfPerson, text='back')
	dp.register_callback_query_handler(self_person_add_card, state=user_state.SelfPerson, text='add_card_number')
	dp.register_message_handler(self_person_send_card, state=user_state.SelfPerson.SendCardNumber)
	dp.register_callback_query_handler(self_person_add_ORD, state=user_state.SelfPerson, text='add_ORD')
	dp.register_message_handler(self_person_send_ORD, state=user_state.SelfPerson.SendORD)
	dp.register_callback_query_handler(self_person_add_INN, state=user_state.SelfPerson, text='add_INN')
	dp.register_callback_query_handler(back_handler, state='*', text='back')
	dp.register_callback_query_handler(go_to_basket, state='*', text='go_to_basket')
	dp.register_callback_query_handler(back_form_order, state='*', text='back_form_order')
	dp.register_callback_query_handler(save_find_channel, state=user_state.SendKeyword.ChooseChannel, text_startswith='save_find_channel')
	dp.register_callback_query_handler(basket_find_channel, state=user_state.SendKeyword.ChooseChannel, text_startswith='basket_find_channel')
	dp.register_callback_query_handler(save_find_channel_start, state='*', text_startswith='save_find_channel')
	dp.register_callback_query_handler(basket_find_channel_start, state='*', text_startswith='basket_find_channel')
	dp.register_callback_query_handler(open_find_channel, state=user_state.SendKeyword.ChooseChannel, text_startswith='open_find_channel')
	dp.register_callback_query_handler(back_to_find_channel, state=user_state.SendKeyword.ChooseChannel, text_startswith='back_to_find_channel')
	dp.register_callback_query_handler(open_saved_channel, state='*', text_startswith='open_saved_channel$')
	dp.register_callback_query_handler(delete_saved_channel, state='*', text_startswith='delete_saved_channel')
	dp.register_callback_query_handler(back_to_saved_channels, state='*', text_startswith='back_to_saved_channels')
	dp.register_callback_query_handler(payments_card, state='*', text_startswith='payments_card')
	dp.register_callback_query_handler(payments_bill, state='*', text_startswith='payments_bill')
	dp.register_callback_query_handler(choose_cat_to_find, state='*', text_startswith='choose_cat_to_find$')
	dp.register_callback_query_handler(change_page_to_find, state='*', text_startswith='change_page_to_find$')
	dp.register_callback_query_handler(change_page_to_find_channel, state='*', text_startswith='change_page_to_find_channel$')
	dp.register_callback_query_handler(back_page_to_find, state='*', text_startswith='back_page_to_find')
	dp.register_callback_query_handler(add_basket_channel, state='*', text_startswith='add_basket_channel')
	dp.register_callback_query_handler(delete_all_basket_channels, state='*', text_startswith='delete_all_basket_channels')
	dp.register_callback_query_handler(load_basket_stat, state='*', text_startswith='load_basket_stat')
	dp.register_callback_query_handler(order_basket, state='*', text_startswith='order_basket')
	dp.register_callback_query_handler(old_order_basket, state='*', text_startswith='go_post')
	dp.register_callback_query_handler(open_basket_channel, state='*', text_startswith='open_basket_channel')
	dp.register_callback_query_handler(delete_basket_channel, state='*', text_startswith='delete_basket_channel')
	dp.register_callback_query_handler(back_to_basket, state='*', text_startswith='back_to_basket')
	dp.register_callback_query_handler(valid_inn, state='*', text_startswith='valid_inn')
	dp.register_callback_query_handler(filter_err, state=user_state.SettingFilters.Main, text='filter_err')
	dp.register_callback_query_handler(filter_views, state=user_state.SettingFilters.Main, text='filter_views')
	dp.register_callback_query_handler(filter_sub, state=user_state.SettingFilters.Main, text='filter_sub')
	dp.register_callback_query_handler(filter_show_result, state=user_state.SettingFilters.Main, text='filter_show_result')
	dp.register_callback_query_handler(back_to_filters, state=user_state.SettingFilters, text='back_to_filters')
	dp.register_callback_query_handler(filters_err, state=user_state.SettingFilters.SetERR, text_startswith='filters_err$')
	dp.register_message_handler(filters_views, state=user_state.SettingFilters.SetView)
	dp.register_message_handler(filters_sub, state=user_state.SettingFilters.SetSub)
	dp.register_message_handler(send_photo_post_handler, state=user_state.AddMyPost.SendPost, content_types=['photo', 'video'])
	dp.register_message_handler(send_text_post_handler, state=user_state.AddMyPost.SendPost, content_types=['text'])
	dp.register_callback_query_handler(open_my_post_handler, state='*', text_startswith='open_my_post$')
	dp.register_callback_query_handler(delete_my_post_handler, state='*', text_startswith='delete_my_post')
	dp.register_callback_query_handler(back_to_my_post_handler, state='*', text_startswith='back_to_my_posts')
