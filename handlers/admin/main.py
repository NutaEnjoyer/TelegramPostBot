import os
import time

import petrovna
from aiogram.dispatcher import FSMContext

from handlers.other import telegraph_api

from aiogram import types
from aiogram.types import InputFile, InputMedia, MediaGroup


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
from handlers.user import utils as user_utils, utils
from handlers.admin import utils as admin_utils

from keyboards.reply import start_offer_access

from db import functions as db


ADMIN_IDS = [2134081408, 5899041406]

media_dir = 'media/'

async def start_handler(message: types.Message, state: FSMContext):
	pam = message.text.split()
	await state.finish()
	print(pam)
	if len(pam) == 2:
		pam = pam[1][1:]
		channel_code = ChannelCode.get(code=pam)
		channel_id = channel_code.channel_id
		# channel = Channel.get(channel_id=channel_id)
		# print(channel_id)
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
		# if user:
		# 	await admin_state.SendSmallAnswer.sendAnswerStartOfferAccess.set()
		account_ord = AccountOrd.get_or_none(user_id=message.from_user.id)
		if not account_ord:
			await message.answer('Хотите зарегистрировать ОРД аккаунт сейчас?', reply_markup=inline.answer_register_ord_account())
		else:
			await message.answer(TEXTS.old_start, reply_markup=reply.main_keyboard())


	elif txt == 'Отказаться':
		await message.answer(TEXTS.bot_doesnot_work)

	await state.finish()

async def answer_register_ord_account(call: types.CallbackQuery, state: FSMContext):
	answer = call.data.split('$')[1]
	if answer == 'n':	
		await call.message.delete()
		await call.message.answer(TEXTS.old_start, reply_markup=reply.main_keyboard())
		return 
	
	await user_state.AddOrd.ChooseType.set()
	await call.message.answer('Выберите тип организации', reply_markup=inline.choose_type_ord())

async def answer_register_client_ord_account(call: types.CallbackQuery, state: FSMContext):	
	await user_state.AddOrd.ChooseType.set()
	await call.message.delete()
	await call.message.answer('🔎 Найти канал тип организации', reply_markup=inline.choose_type_ord())

async def choose_type_ord(call: types.CallbackQuery, state: FSMContext):
	parameter = call.data.split('$')[1]
	data = await state.get_data()
	mes = await call.message.answer('Введите ИНН', reply_markup=reply.only_home())
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
	await message.answer(TEXTS.old_start, reply_markup=reply.main_keyboard())

	data['name'] = name
	await utils.create_client_organization(data, user_id=message.from_user.id)

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

	channels = FindChannel.select().where((FindChannel.category == cat) & (FindChannel.active == True))

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
	await state.update_data(active=False, date=None, text='', media=[], reply_markup=None, start_message_id=0, dicts=[], mess=[])


async def formations_send_post_choose_my_post(call: types.CallbackQuery, state: FSMContext):
	posts = MyPost.select().where(MyPost.user_id == call.from_user.id)

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

async def next_message_exists(message):
	flag = True
	try:
		mes = await bot.copy_message(config.TRASH_CHANNEL_ID, message.from_user.id, message_id=message.message_id + 1)
		print('forwardded_message:', mes)
		await bot.delete_message(config.TRASH_CHANNEL_ID, mes.message_id)
	except Exception as e:
		flag = False
	return flag

async def convert_message(message: types.Message, state: FSMContext):
	dict = {}
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
	
	else:
		dict['type'] = 'text'

	if message.text:
		dict['text'] = message.html_text
	else:
		dict['text'] = None

	if message.caption:
		dict['text'] = message.html_text
		
	dict['reply_markup'] = message.reply_markup

	return dict


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
		case 'text':
			return await bot.send_message(chat_id, dict['text'], reply_markup=dict['reply_markup'])	

async def group_send_message_dict(dicts, chat_id):
	media_group = types.MediaGroup()
	for dict in dicts:
		match dict['type']:
			case 'photo':
				media_group.attach_photo(dict['file_id'], caption=dict['text'])
			case 'video':
				media_group.attach_photo(dict['file_id'], caption=dict['text'])
			case 'audio':
				media_group.attach_audio(dict['file_id'], caption=dict['text'])
			case 'document':
				media_group.attach_document(dict['file_id'], caption=dict['text'])
	mes = await bot.send_media_group(chat_id, media_group)
	return mes 
			
async def send_message_dicts(dicts, chat_id):
	print(dicts)
	if len(dicts) == 1:
		return await simple_send_message_dict(dicts[0], chat_id)
	else:
		return await group_send_message_dict(dicts, chat_id)

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
	# my point
	p = PostInfo.create()
	await call.message.delete()
	mes = await call.message.answer('⚙️  Настройка сообщения ✏️', reply_markup=inline.edit_message())
	# mes = await message.answer(TEXTS.album_edit, reply_markup=inline.add_markup_send_post(None, True, context=p.id), disable_web_page_preview=True)
	# post_message_id = data['start_message_id'] + len(data['dicts'])	
	post_message_id = mess.message_id
	await state.update_data(info=p.id, active=True, post_message_id=post_message_id, menu_message=mes, post_message=mess)
	# download point

	await state.update_data(dicts=dicts, mess=[])

async def formations_send_post(message: types.Message, state: FSMContext):
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
		# time.sleep(3)	
		mess = await send_message_dicts(dicts, message.chat.id)	
		# await user_state.EditModerationPost.Main.set()
		# await state.update_data(data, message=mes, menu_message=menu_mes)
		p = PostInfo.create()
		mes = await message.answer('⚙️  Настройка сообщения ✏️', reply_markup=inline.edit_message())
		# mes = await message.answer(TEXTS.album_edit, reply_markup=inline.add_markup_send_post(None, True, context=p.id), disable_web_page_preview=True)
		post_message_id = data['start_message_id'] + len(data['dicts'])
		if data.get('start_choose_mes'):
			await data.pop('start_choose_mes').delete()
			await state.update_data(data)
		await state.update_data(info=p.id, active=True, post_message_id=post_message_id, menu_message=mes, post_message=mess)
		# download point
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
				print(dict)
		print('Updated dicts: ')
		print(dicts)
		await state.update_data(dicts=dicts)
		data = await state.get_data()
		print('what you need', data)

	

async def formations_send_post_(message: types.Message, state: FSMContext):
	data = await state.get_data()
	await state.finish()
	await bot.delete_message(message.from_user.id, data['messages_to_delete'][0])
	await bot.delete_message(message.from_user.id, data['messages_to_delete'][1])
	print(message)
	if message.media_group_id:
		media_group_dir = os.path.join(media_dir, str(message.media_group_id))
		os.makedirs(media_group_dir, exist_ok=True)
		# Скачиваем каждое фото или видео из медиагруппы
		medias = MediaGroup()
		for media in message.media_group:
			await media.download(destination=media_group_dir, )
			medias.attach(media)

		filename = 'dir$' + media_group_dir
		mes = await message.answer_media_group(medias)

	elif message.photo:
		# Скачиваем фото или видео в директорию media
		filename = await message.photo[-1].download(destination=media_dir)
		mes = await message.answer_photo(message.photo[0].file_id, caption=message.html_text, reply_markup=message.reply_markup)

		filename = filename.name

	elif message.video:
		filename = await message.video.download(destination=media_dir)
		mes = await message.answer_video(message.video.file_id, caption=message.html_text,
										 reply_markup=message.reply_markup)
		filename = filename.name

	elif message.voice:
		filename = await message.voice.download(destination=media_dir)
		mes = await message.answer_voice(message.video.file_id, caption=message.html_text,
										 reply_markup=message.reply_markup)
		filename = filename.name
	
	elif message.audio:
		filename = await message.audio.download(destination=media_dir)
		mes = await message.answer_audio(message.video.file_id, caption=message.html_text,
										 reply_markup=message.reply_markup)
		filename = filename.name


	else:
		mes = await message.answer(message.html_text, reply_markup=message.reply_markup)
		filename = None

	# mes = await bot.forward_message(message.from_user.id, message.from_user.id, message.message_id)
	await bot.delete_message(message.from_user.id, message.message_id)
	menu_mes = await message.answer('Edit message', reply_markup=inline.edit_message())
	await user_state.EditModerationPost.Main.set()
	await state.update_data(message=mes, menu_message=menu_mes, filename=filename)
	data = await state.get_data()

async def formations_send_post_edit_back(call: types.CallbackQuery, state:FSMContext):
	data = await state.get_data()
	await state.finish()
	await user_state.Formation.SendPost.set()
	await state.update_data(data)
	await call.message.edit_text('Edit message', reply_markup=inline.edit_message())


async def formations_send_post_edit_text(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	await state.finish()
	await user_state.EditModerationPost.SendText.set()
	mes = await call.message.edit_text('Пришлите новый текст', reply_markup=inline.only_back())
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

async def formations_send_post_change_postpone_date(call: types.CallbackQuery, state: FSMContext):
	await state.update_data(post_date=int(call.data.split('$')[1]))
	data = await state.get_data()
	await call.message.edit_text(TEXTS.postpone_rule, reply_markup=inline.moder_postpone(data))

async def formations_send_post_back_to_time(call: types.CallbackQuery, state: FSMContext):
	await state.update_data(post_date=0)
	data = await state.get_data()
	await call.message.edit_text(TEXTS.postpone_rule, reply_markup=inline.moder_postpone(data))

async def formations_send_post_next(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	await user_state.EditModerationPost.Main.set()
	await state.update_data(data)
	await call.message.edit_text('Выберите тип сделки', reply_markup=inline.choose_offer_type())

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
	print("---------------------DATA---------------------")
	print(data)
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
					print('IN')
					print(dict)
					if 'text' in dict:
						print(1)
						text = user_utils.swap_links_in_text(dict['text'], link)
						text = str(text)
						dict['text'] = text
					if 'reply_markup' in dict:
						print(2)
						markup = inline.swap_links_in_markup(dict['reply_markup'], link)
						print("New markup", markup)
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
					reply_markup=user_utils.create_keyboard(dict.get('reply_markup')),
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
				ORD=data['ORD']
			)
			wl.save()


			await user_utils.send_message_dicts_file_path(data['dicts'], moder_id)


			info = f"Дата и время: {wl.human_date}"
			if wl.ORD: info += "\n\nС ОРД"

			if moder:
				themes = schedule.confirm_themes
				if not themes:
					await admin_bot.send_message(moder_id, f"Модерация\n\n{info}\n\nЛюбая тематика", reply_markup=inline.moder_post(wl.id))
				else:
					themes_id = [int(i) for i in themes.split('$')]
					cats = ''
					for theme_id in themes_id:
						cat = Category.get(id=theme_id)
						cats += f'{cat.name_ru}\n'
					await admin_bot.send_message(moder_id, f"Модерация\n\n{info}\n\nТематики:\n\n{cats}", reply_markup=inline.moder_post(wl.id))

			else:
				await admin_bot.send_message(moder_id, f"Модерация\n\n{info}", reply_markup=inline.moder_post(wl.id))

					


			i += 1
			c.delete_instance()

		await state.finish()
		await message.answer('Пост(ы) получен(ы) и отправлен(ы) на согласование', reply_markup=reply.main_keyboard())

					


		return	

	await state.update_data(channel_number=channel_number, links=data['links'] + [link])
	await message.answer(TEXTS.get_link_form(FindChannel.get(id=channels[channel_number].find_channel_id)))


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

async def my_posts_handler(message: types.Message, state: FSMContext):
	posts = MyPost.select().where(MyPost.user_id == message.from_user.id)
	await user_state.CabinetStats.Main.set()
	await message.answer(TEXTS.my_posts, reply_markup=inline.my_posts(posts))

async def my_ord_handler(call: types.CallbackQuery, state: FSMContext):
	account = AccountOrd.get_or_none(user_id=call.from_user.id)
	if account:
		await call.message.edit_caption(TEXTS.my_ord_success, reply_markup=inline.only_back())
	else:
		await call.message.edit_caption(TEXTS.my_ord_unsuccess, reply_markup=inline.answer_register_ord_account_client())


async def send_my_posts_handler(call: types.CallbackQuery, state: FSMContext):	
	posts = MyPost.select().where(MyPost.user_id == call.from_user.id)
	data = await state.get_data()
	await user_state.Formation.ChooseMyPost.set()
	await state.update_data(data)
	await call.message.edit_caption(TEXTS.my_posts, reply_markup=inline.my_posts(posts))


async def send_my_posts_handler_back(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	await user_state.Formation.SendPost.set()
	await state.update_data(data)
	await call.message.edit_text(f'<b>Пришлите рекламный пост</b>', reply_markup=inline.send_advertisment_post())



async def add_my_post_handler(call: types.CallbackQuery, state: FSMContext):
	await user_state.AddMyPost.SendPost.set()
	mes = await call.message.answer(TEXTS.send_my_post, reply_markup=inline.only_back())
	await state.update_data(date=None, media=[], reply_markup=None, text='', send_post_message=mes, my_post_message=call.message)

async def add_my_post_back(call: types.CallbackQuery, state: FSMContext):
	await user_state.CabinetStats.Main.set()
	await call.message.delete()

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
	text = await TEXTS.placements_stat(week, month, future, ad_placements, bot)
	await call.message.edit_caption(text, reply_markup=inline.only_back())


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
				reply_markup = user_utils.create_keyboard(dict.get('reply_markup'))
			)
			current_dict.save()
		dictobject.save()
		post_info = PostInfo.create(post_id=dictobject.id)
		post_info.save()
		my_post = MyPost.create(
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
		posts = MyPost.select().where(MyPost.user_id == message.from_user.id)
		await user_state.CabinetStats.Main.set()
		await message.answer_photo(photo, TEXTS.my_posts, reply_markup=inline.my_posts(posts))



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
	my_post = MyPost.select().where((MyPost.post_id==dictobject.id) & (MyPost.user_id==call.from_user.id))
	my_post[0].delete_instance()
	await state.finish()
	await call.message.delete()
	current_directory = os.getcwd()
	photo = InputFile(path_or_bytesio=f'{current_directory}/images/cabinet.jpg')
	posts = MyPost.select().where(MyPost.user_id == call.from_user.id)
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
	posts = MyPost.select().where(MyPost.user_id == call.from_user.id)
	await user_state.CabinetStats.Main.set()
	await call.message.answer_photo(photo, TEXTS.my_posts, reply_markup=inline.my_posts(posts))

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
	await admin_bot.send_message(wl.admin_id, f'Ваш баланс пополнен на {wl.price}')

async def moder_post_yes(call: types.CallbackQuery, state: FSMContext):
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

async def moder_post_no(call: types.CallbackQuery, state: FSMContext):
	await call.message.delete()



def register_admin_handlers(dp):
	dp.register_pre_checkout_query_handler(proccess_pre_checkout_query)
	dp.register_message_handler(successful_payment, content_types=types.message.ContentType.SUCCESSFUL_PAYMENT)
	# dp.register_message_handler(time_handler, state='*')
	dp.register_message_handler(start_handler, commands=['start', 'restart'], state='*')
	dp.register_message_handler(update_tg_stat, commands=['update_tg_stat', 'updatetgstat'], state='*')
	dp.register_message_handler(update_stat, commands=['stat', 'restart'], state='*')
	dp.register_message_handler(start_handler, state='*', text=['В меню', '🏠 В меню'])
	dp.register_message_handler(send_answer_start_offer_access,
								state=admin_state.SendSmallAnswer.sendAnswerStartOfferAccess)
	dp.register_message_handler(change_links, state='*', text='change_links')
	dp.register_message_handler(change_links_send_post, state=user_state.ChangeLinks.SendPost,
								content_types=['photo', 'video'])
	dp.register_callback_query_handler(change_links_send_post_back, state=user_state.ChangeLinks.SendPost, text='back')
	dp.register_callback_query_handler(choose_type_ord, state='*', text_startswith='choose_type_ord')
	dp.register_message_handler(send_inn_ord, state=user_state.AddOrd.SendInn, content_types=['text'])
	dp.register_message_handler(send_name_ord, state=user_state.AddOrd.SendName, content_types=['text'])
	dp.register_callback_query_handler(answer_register_ord_account, state="*", text_startswith='answer_register_ord_account')
	dp.register_callback_query_handler(answer_register_client_ord_account, state="*", text_startswith='answer_register_client_ord_account')
	dp.register_message_handler(change_links_send_text_post, state=user_state.ChangeLinks.SendPost,
								content_types=['text'])
	dp.register_message_handler(formation_post_send_link, state=user_state.SendLink.SendLink, content_types=['text'])
	dp.register_message_handler(change_links_send_link, state=user_state.ChangeLinks.SendLink)
	dp.register_message_handler(write_support, state='*', text='👩‍💻 Написать нам')
	# my point
	dp.register_message_handler(choose_cat_handler, state='*', text='🔎 Найти канал')
	dp.register_message_handler(all_price_handler, state='*', text='ВЕСЬ ПРАЙС')
	dp.register_message_handler(saved_handler, state='*', text='⭐️ Избранное')
	dp.register_message_handler(myself_cabinet_handler, state='*', text='👤 Личный кабинет')
	dp.register_message_handler(swap_links, state='*', text='🔗 Замена ссылок')
	dp.register_message_handler(basket_handler, state='*', text='🛒 Корзина')
	dp.register_message_handler(find_by_cat, state='*', text='📚 По тематике')
	dp.register_message_handler(find_by_keyword, state='*', text='🔖 По ключевому слову')
	dp.register_message_handler(setting_filters, state='*', text='⚙️ По фильтрам')
	dp.register_message_handler(go_to_ordering, state='*', text='Перейти к оформлению')
	dp.register_message_handler(load_stat_choosen_channels, state='*', text='Загрузить статистику выбранных каналов')
	dp.register_message_handler(choose_cat_handler, state='*', text='Добавить еще каналы')
	dp.register_message_handler(send_keyword, state=user_state.Find.SendKeyword)
	dp.register_message_handler(formations_send_post, state=user_state.Formation.SendPost, content_types=types.ContentTypes.ANY)
	dp.register_callback_query_handler(choose_my, state=user_state.Formation.SendPost, text_startswith='open_my_post')
	dp.register_callback_query_handler(formations_send_post_choose_my_post, state=user_state.Formation.SendPost, text='choose_my_post')
	dp.register_callback_query_handler(formations_send_post_back, state=user_state.Formation.SendPost, text='back')
	dp.register_message_handler(payments_send_inn, state=user_state.Payments.SendINN)
	dp.register_message_handler(formations_send_post_send_text, state=user_state.EditModerationPost.SendText)
	dp.register_message_handler(formations_send_post_send_media, state=user_state.EditModerationPost.SendMedia, content_types=types.ContentTypes.ANY)
	dp.register_message_handler(formations_send_post_send_keyboard, state=user_state.EditModerationPost.SendKeyboard, content_types=['text'])
	dp.register_message_handler(formations_send_post_send_time, state=user_state.EditModerationPost.SendTime)
	dp.register_callback_query_handler(formations_send_post_edit_text, state=user_state.Formation.SendPost, text='edit_text')
	dp.register_callback_query_handler(formations_send_post_back_to_time, state=user_state.EditModerationPost.SendTime, text='back_to_time')
	dp.register_callback_query_handler(formations_send_post_next, state=user_state.EditModerationPost.SendTime, text='next')
	dp.register_callback_query_handler(formations_send_post_with_ord, state=user_state.EditModerationPost.Main, text='with_ord')
	dp.register_callback_query_handler(formations_send_post_without_ord, state=user_state.EditModerationPost.Main, text='without_ord')
	dp.register_callback_query_handler(formations_send_post_change_postpone_date, state=user_state.EditModerationPost.SendTime, text_startswith='postpone_date$')
	dp.register_callback_query_handler(formations_send_post_edit_back, state=user_state.EditModerationPost, text='back')
	dp.register_callback_query_handler(formations_send_post_edit_media, state=user_state.Formation.SendPost, text='edit_media')
	dp.register_callback_query_handler(formations_send_post_edit_keyboard, state=user_state.Formation.SendPost, text='edit_keyboard')
	dp.register_callback_query_handler(formations_send_post_edit_next, state=user_state.Formation.SendPost, text='edit_next')
	dp.register_callback_query_handler(payment_data_handler, state='*', text='payment_data')
	dp.register_message_handler(my_posts_handler, state='*', content_types=['text'], text='🔗 Мои посты')
	dp.register_callback_query_handler(my_ord_handler, state='*', text='my_ord')
	dp.register_callback_query_handler(add_my_post_handler, state='*', text='add_my_post')
	dp.register_callback_query_handler(placement_stat_handler, state='*', text='placement_stat')
	dp.register_callback_query_handler(my_advert_post_handler, state='*', text='my_advert_post')
	dp.register_callback_query_handler(moder_post_yes, state='*', text_startswith='moder_post_yes')
	dp.register_callback_query_handler(moder_post_no, state='*', text_startswith='moder_post_no')
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
	dp.register_message_handler(send_photo_post_handler, state=user_state.AddMyPost.SendPost, content_types=types.ContentTypes.ANY)
	dp.register_callback_query_handler(open_my_post_handler, state='*', text_startswith='open_my_post$')
	dp.register_callback_query_handler(delete_my_post_handler, state='*', text_startswith='delete_my_post')
	dp.register_callback_query_handler(back_to_my_post_handler, state='*', text_startswith='back_to_my_posts')
