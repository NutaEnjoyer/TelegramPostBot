import json
import re
from datetime import datetime
from pprint import pprint

import pytz
from aiogram import types, Bot
from aiogram.types import InputMediaPhoto, InputMediaVideo

from bot_data import config
from db import functions
from db.models import *
from handlers.user import TEXTS
from keyboards import inline

from handlers.other import tg_stat

from bot.start_bot_container import bot
from bot.start_semi_bot_container import bot as user_bot

import handlers.other.ord_api as ord_api

import os

# bot = Bot(token=config.ADMIN_TOKEN, parse_mode='HTML')


def check_inn(type, inn):
    if type == "ul":
        if len(inn) == 10:
            coefficients = [2, 4, 10, 3, 5, 9, 4, 6, 8]
            control_sum = sum([int(inn[i]) * coefficients[i] for i in range(9)]) % 11
            control_digit = int(inn[-1])
            return control_sum % 10 == control_digit
    elif type == "fl" or type == "ip":
        if len(inn) == 12:
            coefficients_1 = [7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
            coefficients_2 = [3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
            control_sum_1 = sum([int(inn[i]) * coefficients_1[i] for i in range(10)]) % 11
            control_sum_2 = sum([int(inn[i]) * coefficients_2[i] for i in range(11)]) % 11
            control_digit_1 = int(inn[-2])
            control_digit_2 = int(inn[-1])
            return control_sum_1 % 10 == control_digit_1 and control_sum_2 % 10 == control_digit_2
    return False


def check_name(type, name):
    if len(name) > 255:
        return False
    if type == "fl":
        pattern = r'^([а-яёА-ЯЁ]+(\s[а-яёА-ЯЁ]+)?){1,255}$'
    elif type == "ip" or type == "ul":
        pattern = r'^([a-zA-Zа-яёА-ЯЁ0-9?!*$]+(-|\s|\s"|"\s))*[a-zA-Zа-яёА-ЯЁ0-9?!*$][^(\s|\-)]+$'
    else:
        pattern = r'^([a-zA-Zа-яёА-ЯЁ0-9?!*$]+(-|\s|\s"|"\s))*[a-zA-Zа-яёА-ЯЁ0-9?!*$][^(\s|\-)]+$'
    return bool(re.match(pattern, name))

def get_full_name(short_name):
    if short_name == 'ffl':
        return 'Иностранное физическое лицо'
    elif short_name == 'ful':
        return 'Иностранное юридическое лицо'
    elif short_name == 'ip':
        return 'Индивидуальный предприниматель'
    elif short_name == 'fl':
        return 'Физическое лицо'
    elif short_name == 'ul':
        return 'Юридическое лицо'
    else:
        return 'Неизвестное значение'

def get_info_ord(user_id, first_name):
	account = AccountOrd.get(user_id=user_id)
	info = ord_api.get_organization(id=account.ord_id)
	html = f'''<h3>Информация о рекламодателе</h3>
		<b>{first_name}

		Название: {info['name']}
		Тип: {get_full_name(info['type'])}
		ИНН: {info['inn']}
		</b>
'''
	return html

def is_ad(post_time):
	advert_post = AdvertPost.get_or_none(post_time_id=post_time.id)
	if not advert_post:
		return False
	return True

def new_ad_placement(post_time, message_id=None):
	advert_post = AdvertPost.get_or_none(post_time_id=post_time.id)
	wl = WaitList.get(id=advert_post.wait_list_id)

	dv = DeferredVerification.create(
		admin_id = wl.admin_id,
		user_id = wl.user_id,
		price = wl.price,
		channel_id = wl.channel_id,
		post_id = message_id,
		start_time = wl.seconds,
		finish_time = wl.seconds + 79_200,
		from_admin_bot=wl.from_admin_bot
	)
	dv.save()

	ad_placement = AdPlacement.create(user_id=wl.user_id, admin_id=wl.admin_id, price=wl.price, time=wl.seconds)
	ad_placement.save()
	
async def is_no_paid(post_time):
	advert_post = AdvertPost.get_or_none(post_time_id=post_time.id)
	result = False

	p = PostInfo.get_or_none(post_id=post_time.post_id)

	if p:
		manager = ManagerPlacement.get_or_none(info=p.id)
		if manager:
			if not manager.is_admin_paid:
				return True


	if not advert_post:
		return False

	if not advert_post.is_paid:
		wl = WaitList.get_or_none(id=advert_post.wait_list_id)
		if wl:
			return False
		if advert_post.active:
			try:
				await bot.send_message(wl.admin_id, "Рекламный  пост отменен из-за просрочки оплаты")
				await user_bot.send_message(wl.user_id, "Рекламный  пост в канале отменен из-за просрочки оплаты")
				await user_bot.delete_message(wl.user_id, advert_post.invoice_message_id)
			except Exception as e:
				pass
		result = True
	
	advert_post.active = False
	advert_post.save()
	return result

async def create_organization(data, user_id):
	platform = ord_api.create_platform_object(name=data['title'], url=data['url'])
	organization = ord_api.register_organization(type=data['type'], inn=data['inn'], name=data['name'], platforms=[platform])
	org_id = organization['id']
	account = AccountOrd.create(user_id=user_id, ord_id=org_id)
	account.save()
	await bot.send_message(config.ORD_LOGGING, TEXTS.register_organization(data, user_id, org_id))

async def create_client_organization(data, user_id):
	platform = ord_api.create_standard_platform_object()
	organization = ord_api.register_organization(type=data['type'], inn=data['inn'], name=data['name'], platforms=[platform])
	org_id = organization['id']
	account = AccountOrd.create(user_id=user_id, ord_id=org_id)
	account.save()
	await bot.send_message(config.ORD_LOGGING, TEXTS.register_client_organization(data, user_id, org_id))

async def add_platform(account_id, name, url, user_id):
	ord_api.add_platform(id=account_id, name=name, url=url)
	await bot.send_message(config.ORD_LOGGING, TEXTS.new_platform(user_id, name, url))

async def register_creative(contract_id, media, text, link):
	pass

async def new_contract(post_time, message):
	channel = Channel.get(id=post_time.channel_id)

	advert_post = AdvertPost.get(post_time_id=post_time.id)
	wl = WaitList.get(id=advert_post.wait_list_id)
	if not wl.ORD:
		return
	
	admin_id = wl.admin_id
	user_id = wl.user_id

	price = wl.price

	admin_account = AccountOrd.get(user_id=admin_id)
	user_account = AccountOrd.get(user_id=user_id)

	admin_org_id = admin_account.ord_id
	user_org_id = user_account.ord_id

	contract = ord_api.create_contract(clientId=user_org_id, contractorId=admin_org_id, amount=price, number=wl.id)
	print(contract)
	contract_id = contract['id']

	await bot.send_message(config.ORD_LOGGING, TEXTS.new_contract(user_id, admin_id, price, contract_id, wl.id))

	bot_info = await bot.get_me()
	message_link = f"https://t.me/{bot_info.username}?start={channel.channel_id}_{message}"
	await register_creative(contract_id=contract_id, media=wl.media, text=wl.html_text, link=message_link)

async def dv_proccess(dv):
	dv.active = False
	dv.save()
	views = tg_stat.get_post_views(dv.channel_id, dv.post_id)
	print(f"{views=}")
	# channel = Channel.get(channel_id=dv.channel_id)
	chat = await bot.get_chat(dv.channel_id)
	channel = f'''<a href="{chat.invite_link}">{chat.title}</a>'''
	print(channel)
	text = f'''<b>🎉🎉 Прошло 24 часа после публикации поста в канале {channel} 🎉🎉

💵 Цена: {dv.price} ₽ 

👁 Кол-во просмотров: {views} ₽

📊Результат: {round(dv.price/views, 2) if views else 0} ₽/пр.</b>'''

	if dv.from_admin_bot:
		await bot.send_message(dv.user_id, text)
	else:
		await user_bot.send_message(dv.user_id, text)



async def check_user_subscription(channel_id: int, admin_id: int) -> bool:
	chat_member = await bot.get_chat_member(chat_id=channel_id, user_id=admin_id)

	if chat_member.status in ("member", "administrator", "creator"):
		return True
	else:
		return False

async def check_admin_rights(channel_id):
	try:
		chat = await bot.get_chat(chat_id=channel_id)
		admins = await chat.get_administrators()
		admins = [i.user.id for i in admins]
		me = await bot.get_me()
		bot_id = me.id
		return bot_id in admins

	except Exception as e:
		return False


async def get_channel_info(channel_id):
	try:
		chat = await bot.get_chat(chat_id=channel_id)
		return chat

	except Exception as e:
		return None


def time_message_convert(message):
	spl = message.split(':')
	if len(spl) > 2: return

	if len(spl) == 2:
		hour = spl[0]
		minut = spl[1]

	else:
		hour = spl[0][:-2]
		minut = spl[0][-2:]

	if not(hour.isdigit() and minut.isdigit()): return

	hour = int(hour)
	minut = int(minut)

	if not(hour >= 0 and hour < 24 and minut >=0 and minut < 60): return

	return f'{hour}:{minut}'

async def convert_message(message: types.Message):
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

async def simple_send_message_dict_file_path(dict, chat_id, info, config):
	text = dict['text']
	disable_notification = False
	if dict.get('file_path'):
		file = open(dict['file_path'], 'rb')

	match dict['type']:
		case 'photo':
			return await bot.send_photo(chat_id, file, caption=text, reply_markup=dict['reply_markup'], disable_notification=disable_notification)
		case 'video':
			return await bot.send_video(chat_id, file, caption=text, reply_markup=dict['reply_markup'], disable_notification=disable_notification)
		case 'voice':
			return await bot.send_voice(chat_id, file, caption=text, reply_markup=dict['reply_markup'], disable_notification=disable_notification)
		case 'audio':
			return await bot.send_audio(chat_id, file, caption=text, reply_markup=dict['reply_markup'], disable_notification=disable_notification)
		case 'document':
			return await bot.send_document(chat_id, file, caption=text, reply_markup=dict['reply_markup'], disable_notification=disable_notification)
		case 'animation':
			return await bot.send_animation(chat_id,  file, disable_notification=disable_notification)
		case 'sticker':
			return await bot.send_sticker(chat_id,  file, disable_notification=disable_notification)
		case 'video_note':
			return await bot.send_video_note(chat_id, file, reply_markup=dict['reply_markup'], disable_notification=disable_notification) 
		case 'text':
			return await bot.send_message(chat_id, text, reply_markup=dict['reply_markup'], disable_notification=disable_notification, allow_sending_without_reply=True)


async def group_send_message_dict_file_path(dicts, chat_id, info, config):
	disable_notification = False
	media_group = types.MediaGroup()

	for dict in dicts:
		if dict['text']:
			text = dict['text']	
		else:
			text = ''

		print('Dict object:', dict)
		if dict.get('file_path'):
			file = open(dict['file_path'], 'rb')
		match dict['type']:
			case 'photo':
				media_group.attach_photo(file, caption=text)
			case 'video':
				media_group.attach_video(file, caption=text)
			case 'audio':
				media_group.attach_audio(file, caption=text)
			case 'document':
				media_group.attach_document(file, caption=text)
	mes = await bot.send_media_group(chat_id, media_group, disable_notification=disable_notification)
	return mes 

async def simple_send_message_dict(dict, chat_id, info, config, bot=bot):
	print('SIMPLE')
	if config and info:
		text = (dict['text'] if dict['text'] else '') + '\n\n' + config.auto_write if info.with_auto_write else dict['text']
	else:
		text = dict['text']
	if info:
		disable_notification = not info.with_notification
		disable_web_preview = info.disable_web_preview
	else:
		disable_notification = False
		disable_web_preview = True


	match dict['type']:
		case 'photo':
			return await bot.send_photo(chat_id, dict['file_id'], caption=text, reply_markup=dict['reply_markup'], disable_notification=disable_notification)
		case 'video':
			return await bot.send_video(chat_id, dict['file_id'], caption=text, reply_markup=dict['reply_markup'], disable_notification=disable_notification)
		case 'voice':
			return await bot.send_voice(chat_id, dict['file_id'], caption=text, reply_markup=dict['reply_markup'], disable_notification=disable_notification)
		case 'audio':
			return await bot.send_audio(chat_id, dict['file_id'], caption=text, reply_markup=dict['reply_markup'], disable_notification=disable_notification)
		case 'document':
			return await bot.send_document(chat_id, dict['file_id'], caption=text, reply_markup=dict['reply_markup'], disable_notification=disable_notification)
		case 'animation':
			return await bot.send_animation(chat_id,  dict['file_id'], disable_notification=disable_notification)
		case 'sticker':
			return await bot.send_sticker(chat_id,  dict['file_id'], disable_notification=disable_notification)
		case 'video_note':
			return await bot.send_video_note(chat_id, dict['file_id'], reply_markup=dict['reply_markup'], disable_notification=disable_notification)
		case 'text':
			print(f'DISABLE PREVIEW: {disable_web_preview}')
			return await bot.send_message(chat_id, text, reply_markup=dict['reply_markup'], disable_notification=disable_notification, allow_sending_without_reply=True, disable_web_page_preview=disable_web_preview)



async def group_send_message_dict(dicts, chat_id, info, config, bot=bot):
	disable_notification = not info.with_notification if info else False
	print('Disable', disable_notification)
	media_group = types.MediaGroup()
	has_text = False
	for dict in dicts:
		if dict['text']:
			has_text = True
	for dict_i in range(len(dicts)):
		dict = dicts[dict_i]
		text = None
		if has_text:
			if dict['text']:
				if info:
					text = dict['text'] + '\n\n' + config.auto_write if info.with_auto_write else dict['text']
				else:
					text = dict['text']
			else:
				text = text
		else:
			if dict_i == 0:
				if info:
					text = config.auto_write if info.with_auto_write else None
				else:
					text = None
			else:
				text = None
		match dict['type']:
			case 'photo':
				media_group.attach_photo(dict['file_id'], caption=text)
			case 'video':
				media_group.attach_video(dict['file_id'], caption=text)
			case 'audio':
				media_group.attach_audio(dict['file_id'], caption=text)
			case 'document':
				media_group.attach_document(dict['file_id'], caption=text)
	mes = await bot.send_media_group(chat_id, media_group, disable_notification=disable_notification)
	return mes 
			
async def send_message_dicts(dicts, chat_id, info=None, config=None, bot=bot):
	if len(dicts) == 1:
		return await simple_send_message_dict(dicts[0], chat_id, info, config, bot)
	else:
		return await group_send_message_dict(dicts, chat_id, info, config, bot)	
			
async def send_message_dicts_file_path(dicts, chat_id, info=None, config=None):
	print("dicts")
	print(dicts)
	if len(dicts) == 1:
		return await simple_send_message_dict_file_path(dicts[0], chat_id, info, config)
	else:
		return await group_send_message_dict_file_path(dicts, chat_id, info, config)
	


def create_dict_object(data, user_id):
	dicts = data['dicts']
	post_info = PostInfo.get(id=data['info'])
	price = data.get('price') if data.get('price') else post_info.price
	dictObject = DictObject.create(owner_id=user_id, price=price)
	dictObject.save()
	for dict in dicts:
		object = Dict.create(
			object_id=dictObject.id,
			type=dict.get('type'),
			file_id=dict.get('file_id'),
			text=dict.get('text'),
			reply_markup=create_keyboard(dict.get('reply_markup')),
		)
		object.save()
		
	return dictObject.id

async def send_post_to_channel(channel_id, user_id, data, info=None, config=None, bot=bot):
	import time
	import datetime 
	import calendar
	print('WE HERE 2')


	channel_config = ChannelConfiguration.get(channel_id=channel_id)
	dicts = data['dicts']
	if info:
		p = info
		config = config
	else:
		p = PostInfo.get(id=data['info'])
		channel = Channel.get(id=data.get('channel_id'))
		config = ChannelConfiguration.get(channel_id=channel.channel_id)
		print('CONFIG SEND POST TO CHANNEL: ', config.id)
	data['info']  = p.id
	print('P: ', p.id, p.disable_web_preview)
	to_return = await send_message_dicts(dicts, channel_id, p, config, bot)
	chat = await bot.get_chat(channel_id)

	# point 

	human_time = datetime.datetime.now(tz=pytz.timezone("Europe/Moscow")).strftime("%H:%M, %d {} %Y").format(calendar.month_name[datetime.datetime.now(tz=pytz.timezone("Europe/Moscow")).today().month])
	print(f'{human_time=}')
	# human_time = datetime.datetime.now(tz=pytz.timezone("Europe/Moscow")).strftime("%d-%m-%Y %H:%M")
	today = datetime.date.today().strftime('%Y-%m-%d')
	moscow_timezone = datetime.timezone(datetime.timedelta(hours=3))
	today_start = datetime.datetime.strptime(today, '%Y-%m-%d').replace(tzinfo=moscow_timezone)
	print(f'human_time: {human_time}\ntoday_time: {today_start}')
	time = time.time()

	dict_object = create_dict_object(data, user_id)
	p.post_id = dict_object
	p.save()
	if not (type(to_return) is list):
		mes_id = to_return.message_id
	else:
		mes_id = ''
		for i in to_return:
			print('I: ', i)
			mes_id += f'{i.message_id}$'
		mes_id = mes_id[:-1]
	post = SendedPost.create(channel_id=data['channel_id'], message_id=mes_id, post_id=dict_object,
									  time=time, human_time=human_time, user_id=user_id)
	post.save()
	
	if channel_config.point:
		if '$' in mes_id:
			mes = await bot.pin_chat_message(channel_id, mes_id.split('$')[-1])
			await bot.delete_message(channel_id, mes.message_id)
		else:
			mes = await bot.pin_chat_message(channel_id, mes_id)
			await bot.delete_message(channel_id, mes.message_id)
	return mes_id

async def send_post_to_user(user_id, data):
	dicts = data['dicts']
	to_return = await send_message_dicts(dicts, user_id)

	if not (type(to_return) is list):
		mes_id = to_return.message_id
	else:
		mes_id = ''
		for i in to_return:
			print('I: ', i)
			mes_id += f'{i.message_id}$'
		mes_id = mes_id[:-1]

	return mes_id


async def create_post_time(data, time, human_date, user_id):
	dict_object = create_dict_object(data, user_id)
	p = PostInfo.get(id=data['info'])
	p.post_id = dict_object
	p.save()
	dicts = data['dicts']
	post_time = PostTime.create(channel_id=data['channel_id'], post_id=dict_object, time=time, human_time=human_date, user_id=user_id)
	post_time.save()
	print('My data: ', data)
	post_info = None
	if data.get('reply_message_id') and data.get('main'):
		post_info = PostInfo.create(post_id=dict_object, reply_message_id=data['reply_message_id'])
		post_info.save()
	if data.get('hidden_sequel'):
		if not post_info: post_info = PostInfo.create(post_id=dict_object)
		post_info.hidden_sequel_text = data['hidden_sequel']
		post_info.hidden_sequel_button_text = data['hidden_sequel_button_text']
		post_info.save()
	if data.get('share_context'):
		if not post_info: post_info = PostInfo.create(post_id=dict_object)
		result = ''
		for i in data['share_context']:
			result += str(i) + '$'
		result = result[:-1]
		post_info.SharePost = result
		post_info.save()

async def send_post_to_channel_(channel_id, user_id, data, disable_web_prewiew=True):
	channel_config = ChannelConfiguration.get(channel_id=channel_id)
	print('MY DATA', data)

	if data.get('reaction_with'):
		if data.get('postpone'):
			data['reply_markup'], reactions_id = inline.add_reactions(data, data['reaction_with'])
		else:
			pass

	else:
		reactions = channel_config.reactions
		if reactions:
			data['reply_markup'], reactions_id = inline.add_reactions(data, reactions)
			data['reaction_with'] = reactions_id
		else:
			reactions_id = None

	if data.get('hidden_sequel_text'):
		print('IT IS hidden_sequel')
		human_time = datetime.now(tz=pytz.timezone("Europe/Moscow")).strftime("%d-%m-%Y %H:%M")
		import time
		time = time.time()

		media = ''
		if data.get('media'):
			for i in data['media']:
				media += i + '$'
			media = media[:-1]

		text = data['text']

		post = Post.create(media=media, text=text)

		post.save()
		post_info = PostInfo.create(post_id=post.id, hidden_sequel_text=data.get('hidden_sequel_text'))
		post_info.save()

		data['reply_markup'] = inline.get_hidden_sequel(data.get('hidden_sequal_button_text'), post_info.id)

		text = data['text'] + f"\n\n{channel_config.auto_write if channel_config.auto_write else ''}"

		if data['media'] == [] or data['media'] is None:  # text message
			print('MAX DATA', data)
			print('----------')
			if data.get('reply_message_id'):
				try:
					mes = await bot.send_message(channel_id, text, reply_markup=data['reply_markup'],
												 disable_web_page_preview=not channel_config.preview,
												 disable_notification=channel_config.post_without_sound,
												 reply_to_message_id=data['reply_message_id'])
				except Exception as e:
					mes = await bot.send_message(channel_id, text, reply_markup=data['reply_markup'],
												 disable_web_page_preview=not channel_config.preview,
												 disable_notification=channel_config.post_without_sound)
			else:
				mes = await bot.send_message(channel_id, text, reply_markup=data['reply_markup'],
											 disable_web_page_preview=not channel_config.preview,
											 disable_notification=channel_config.post_without_sound)

			data['message_id'] = mes.message_id

		else:
			print('START! ELSE')

			if len(data['media']) == 1:
				try:
					if data.get('reply_message_id'):
						try:
							mes = await bot.send_photo(channel_id, data['media'][0], caption=text,
													   reply_markup=data['reply_markup'],
													   disable_notification=not channel_config.post_without_sound,
													   reply_to_message_id=data['reply_message_id'])
						except Exception as e:
							mes = await bot.send_photo(channel_id, data['media'][0], caption=text,
													   reply_markup=data['reply_markup'],
													   disable_notification=channel_config.post_without_sound)

					else:
						mes = await bot.send_photo(channel_id, data['media'][0], caption=text,
												   reply_markup=data['reply_markup'],
												   disable_notification=channel_config.post_without_sound)
				except Exception as e:
					if data.get('reply_message_id'):
						try:
							mes = await bot.send_video(channel_id, data['media'][0], caption=text,
													   reply_markup=data['reply_markup'],
													   disable_notification=channel_config.post_without_sound,
													   reply_to_message_id=data['reply_message_id'])
						except Exception as e:
							mes = await bot.send_video(channel_id, data['media'][0], caption=text,
													   reply_markup=data['reply_markup'],
													   disable_notification=channel_config.post_without_sound)

					else:
						mes = await bot.send_video(channel_id, data['media'][0], caption=text,
												   reply_markup=data['reply_markup'],
												   disable_notification=channel_config.post_without_sound)

				data['message_id'] = mes.message_id

			else:
				print('START!')
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
							media.attach_photo(data['media'][i], text)
						elif type == 'video':
							media.attach_video(data['media'][i], text)
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

				mes = await bot.send_media_group(channel_id, media,
												 disable_notification=channel_config.post_without_sound)
				data['message_id'] = mes[-1].message_id

		reactions = None


		if data['channel_id'] < 0:
			channel = Channel.get(channel_id=data['channel_id'])
			data['channel_id'] = channel.id
		post_time = SendedPost.create(channel_id=data['channel_id'], message_id=data['message_id'], post_id=post.id,
									  time=time, human_time=human_time, user_id=user_id)
		print(f'ID: {post_time.id}')
		post_time.save()

		if channel_config.point:
			mess = await bot.pin_chat_message(channel_id, data['message_id'])
		return data['message_id']

	text = data['text'] + f"\n\n{channel_config.auto_write if channel_config.auto_write else ''}"

	if data['media'] == [] or data['media'] is None:  # text message
		print('MAX DATA', data)
		print('----------')
		if data.get('reply_message_id'):
			try:
				mes = await bot.send_message(channel_id, text, reply_markup=data['reply_markup'], disable_web_page_preview=channel_config.preview, disable_notification=channel_config.post_without_sound, reply_to_message_id=data['reply_message_id'])
			except Exception as e:
				mes = await bot.send_message(channel_id, text, reply_markup=data['reply_markup'],
											 disable_web_page_preview=not channel_config.preview,
											 disable_notification=channel_config.post_without_sound)
		else:
			mes = await bot.send_message(channel_id, text, reply_markup=data['reply_markup'],
										 disable_web_page_preview=not channel_config.preview,
										 disable_notification=channel_config.post_without_sound)

		data['message_id'] = mes.message_id

	else:
		print('START! ELSE')

		if len(data['media']) == 1:
			try:
				if data.get('reply_message_id'):
					try:
						mes = await bot.send_photo(channel_id, data['media'][0], caption=text,
												   reply_markup=data['reply_markup'],
												   disable_notification=channel_config.post_without_sound, reply_to_message_id=data['reply_message_id'])
					except Exception as e:
						mes = await bot.send_photo(channel_id, data['media'][0], caption=text,
												   reply_markup=data['reply_markup'],
												   disable_notification=channel_config.post_without_sound)

				else:
					mes = await bot.send_photo(channel_id, data['media'][0], caption=text, reply_markup=data['reply_markup'], disable_notification=channel_config.post_without_sound)
			except Exception as e:
				if data.get('reply_message_id'):
					try:
						mes = await bot.send_video(channel_id, data['media'][0], caption=text,
												   reply_markup=data['reply_markup'],
												   disable_notification=channel_config.post_without_sound,
												   reply_to_message_id=data['reply_message_id'])
					except Exception as e:
						mes = await bot.send_video(channel_id, data['media'][0], caption=text,
												   reply_markup=data['reply_markup'],
												   disable_notification=channel_config.post_without_sound)

				else:
					mes = await bot.send_video(channel_id, data['media'][0], caption=text,
											   reply_markup=data['reply_markup'],
											   disable_notification=channel_config.post_without_sound)

			data['message_id'] = mes.message_id

		else:
			print('START!')
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
						media.attach_photo(data['media'][i], text)
					elif type == 'video':
						media.attach_video(data['media'][i], text)
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

			mes = await bot.send_media_group(channel_id, media, disable_notification=channel_config.post_without_sound)
			data['message_id'] = mes[-1].message_id

	reactions = None
	if data.get('reaction_with'):
		try:
			reactions = ReactionsKeyboard.get(id=data.get('reaction_with'))
		except Exception as e:
			pass

	else:
		try:
			reactions = ReactionsKeyboard.get_or_none(id=reactions_id)
		except Exception as e:
			pass

	if reactions:
		reactions.message_id = data['message_id']
		reactions.save()
	human_time = datetime.now(tz=pytz.timezone("Europe/Moscow")).strftime("%d-%m-%Y %H:%M")
	import time
	time = time.time()
	print('Under post')
	post = functions.create_sended_post(data, human_time=human_time, time=time, user_id=user_id)
	print(post)
	print('Post post')
	if channel_config.point:
		mess = await bot.pin_chat_message(channel_id, data['message_id'])

	return data['message_id']

async def send_post_to_channel_by_post_id(channel_id, user_id, post_id):
	post = Post.get_or_none(id=post_id)

	if post is None:
		print('post is None')
		return
	new_post = Post.create()

	if post.reactions_id:
		buttons = Reaction.select().where(Reaction.reaction_keyboard_id == post.reactions_id)
		key = ReactionsKeyboard.create(channel_id=channel_id)
		key.save()
		for b in buttons:
			i = Reaction.create(reaction_keyboard_id=key.id, text=b.text)
			i.save()
		new_post.reactions_id = key.id

	new_post.owner_id = user_id
	new_post.media = post.media
	new_post.text = post.text
	new_post.keyboard_id = post.keyboard_id
	new_post.save()

	post = new_post
	media = post.media.split('$') if post.media else None
	#	await state.update_data(channel_id=channel_id, active=False, date=None, text='', media=[], reply_markup=None)
	data = {
		'channel_id': channel_id,
		'active': True,
		'date': None,
		'text': post.text,
		'media': media,
		'reply_markup': None,
		'reaction_with': post.reactions_id if post.reactions_id else False,
		'postpone': True
	}

	if not(post.keyboard_id is None):
		buttons_select = Button.select().where(Button.keyboard_id == post.keyboard_id)
		keyboard = types.InlineKeyboardMarkup()

		row = 0
		buttons = []
		for b in buttons_select:
			if b.row == row:
				buttons.append(types.InlineKeyboardButton(text=b.text, url=b.url))
			else:

				if len(buttons) == 1:
					keyboard.add(buttons[0])
				elif len(buttons) == 2:
					keyboard.add(buttons[0], buttons[1])
				elif len(buttons) == 3:
					keyboard.add(buttons[0], buttons[1], buttons[2])
				elif len(buttons) == 4:
					keyboard.add(buttons[0], buttons[1], buttons[2], buttons[3])
				elif len(buttons) == 5:
					keyboard.add(buttons[0], buttons[1], buttons[2], buttons[3], buttons[4])
				elif len(buttons) == 6:
					keyboard.add(buttons[0], buttons[1], buttons[2], buttons[3], buttons[4], buttons[5])
				elif len(buttons) == 7:
					keyboard.add(buttons[0], buttons[1], buttons[2], buttons[3], buttons[4], buttons[5], buttons[6])
				elif len(buttons) == 8:
					keyboard.add(buttons[0], buttons[1], buttons[2], buttons[3], buttons[4], buttons[5], buttons[6],
								 buttons[7])

				buttons = [types.InlineKeyboardButton(text=b.text, url=b.url)]
				row += 1

		if len(buttons) == 1:
			keyboard.add(buttons[0])
		elif len(buttons) == 2:
			keyboard.add(buttons[0], buttons[1])
		elif len(buttons) == 3:
			keyboard.add(buttons[0], buttons[1], buttons[2])
		elif len(buttons) == 4:
			keyboard.add(buttons[0], buttons[1], buttons[2], buttons[3])
		elif len(buttons) == 5:
			keyboard.add(buttons[0], buttons[1], buttons[2], buttons[3], buttons[4])
		elif len(buttons) == 6:
			keyboard.add(buttons[0], buttons[1], buttons[2], buttons[3], buttons[4], buttons[5])
		elif len(buttons) == 7:
			keyboard.add(buttons[0], buttons[1], buttons[2], buttons[3], buttons[4], buttons[5], buttons[6])
		elif len(buttons) == 8:
			keyboard.add(buttons[0], buttons[1], buttons[2], buttons[3], buttons[4], buttons[5], buttons[6],
						 buttons[7])

		data['reply_markup'] = keyboard

	await send_post_to_channel(channel_id, user_id, data)


def parse_time(data, plus):
	from datetime import datetime
	import calendar
	currentSecond = datetime.now().second
	currentMinute = datetime.now().minute
	currentHour = datetime.now().hour
	moscow_tz = pytz.timezone('Europe/Moscow')
	current_datetime = datetime.now(moscow_tz)

	# Получаем текущий день, месяц и год
	currentDay = current_datetime.day
	currentMonth = current_datetime.month
	currentYear = current_datetime.year

	spl = data.split()
	if len(spl) > 2:
		return

	if len(spl) == 2:
		time = spl[0]
		date = spl[1]
		spl = time.split(':')
		if len(spl) > 2: return

		if len(spl) == 2:
			hour = spl[0]
			minut = spl[1]

		else:
			hour = spl[0][:-2]
			minut = spl[0][-2:]

		if not (hour.isdigit() and minut.isdigit()): return

		hour = int(hour)
		minut = int(minut)

		if not (hour >= 0 and hour < 24 and minut >= 0 and minut < 60): return

		spl = date.split('.')
		if len(spl) > 2: return

		if len(spl) == 2:
			day = spl[0]
			month = spl[1]

		else:
			day = spl[0][:-2]
			month = spl[0][-2:]

		if not (day.isdigit() and month.isdigit()): return

		day = int(day) + plus
		month = int(month)

		if not (day >= 0 and day < 32 and month >= 0 and month < 13): return

	else:
		time = spl[0]
		spl = time.split(':')
		if len(spl) > 2: return

		if len(spl) == 2:
			hour = spl[0]
			minut = spl[1]

		else:
			hour = spl[0][:-2]
			minut = spl[0][-2:]

		if not (hour.isdigit() and minut.isdigit()): return

		hour = int(hour)
		minut = int(minut)

		if not (hour >= 0 and hour < 24 and minut >= 0 and minut < 60): return

		day = currentDay + plus
		month = currentMonth

	try:
		post_date = datetime(year=currentYear, month=month, day=day, hour=hour, minute=minut)
	except ValueError:
		try:
			post_date = datetime(year=currentYear, month=month+1, day=1, hour=hour, minute=minut)
		except Exception as e:
			post_date = datetime(year=currentYear+1, month=1, day=1, hour=hour, minute=minut)

	now_date = datetime.now(tz=pytz.timezone("Europe/Moscow"))
	now_date = now_date.replace(tzinfo=None)
	if post_date < now_date:
		return

	delta = post_date - now_date
	print(f'Delta: {delta.seconds}')
	print(post_date)
	print(now_date)
	delta = (post_date - now_date).total_seconds()
	print(f'Delta: {delta}')

	# date = post_date.strftime("%d-%m-%Y %H:%M")
	date = post_date.strftime("%H:%M, %d {} %Y").format(calendar.month_name[post_date.month])

	return {
		'human_date': date,
		'seconds': delta
	}


async def send_post(data, user_id, post_id):
	channel = Channel.get(id=data['channel_id'])
	print(f'Data: ', data)
	post_time = PostTime.get(id=post_id)
	info = PostInfo.get(post_id=post_time.post_id)
	config = ChannelConfiguration.get(channel_id=channel.channel_id)

	try:
		mes_id = await send_post_to_channel(channel_id=channel.channel_id, user_id=user_id, data=data, info=info, config=config)
		if data.get('share_context'):
			print(data['share_context'])
			for i in data['share_context'].split('$'):
				print('I: ', i)
				chnl = Channel.get(id=int(i))
				try:
					await bot.forward_message(chnl.channel_id, channel.channel_id, mes_id)
				except Exception as e:
					await bot.send_message(channel.admin_id, TEXTS.error_post_message_to_channel.format(title=chnl.title))
		return mes_id
	except Exception as e:
		print(e)
		admin_id = channel.admin_id
		if admin_id == user_id:
			await bot.send_message(admin_id, TEXTS.error_post_message_to_channel.format(title=channel.title))
		else:
			await bot.send_message(user_id, TEXTS.error_post_message_to_channel.format(title=channel.title))
			await bot.send_message(admin_id, TEXTS.error_post_message_to_channel.format(title=channel.title))


async def send_post_to_user_(data, user_id):
	channel_id = user_id
	print('Data:', data)
	if data['media'] == [] or data['media'] is None:  # text message
		await bot.send_message(channel_id, data['text'], reply_markup=data['reply_markup'], disable_web_page_preview=True)

	else:
		if len(data['media']) == 1:
			try:
				print(data['reply_markup'])
				await bot.send_photo(channel_id, data['media'][0], caption=data['text'], reply_markup=data['reply_markup'])
			except Exception as e:
				print(e)
				await bot.send_video(channel_id, data['media'][0], caption=data['text'], reply_markup=data['reply_markup'])

		else:
			media = types.MediaGroup()
			for i in range(len(data['media'])):
				if i == len(data['media']) - 1:
					try:
						media.attach_photo(data['media'][i], data['text'])
					except Exception as e:
						media.attach_video(data['media'][i], data['text'])
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

			await bot.send_media_group(channel_id, media)


async def approve_all(channel_id):
	orders = NewJoin.select().where(NewJoin.channel_id==channel_id)

	for order in orders:
		try:
			await bot.approve_chat_join_request(order.channel_id, order.user_id)
		except Exception as e:
			pass
		order.approve = True
		order.save()


async def from_post_id_to_data(post_id):
	pass


async def send_old_post_to_user(user_id, data):
	text = data['text']
	print('Logging')
	print(data)

	if data['media'] == [] or data['media'] is None:  # text message
		mes = await bot.send_message(user_id, text, reply_markup=data['reply_markup'],
									 disable_web_page_preview=True)
		print(mes)

	else:
		if len(data['media']) == 1:
			try:
				mes = await bot.send_photo(user_id, data['media'][0], caption=text,
										   reply_markup=data['reply_markup'])
			except Exception as e:
				mes = await bot.send_video(user_id, data['media'][0], caption=text,
										   reply_markup=data['reply_markup'])

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
						media.attach_photo(data['media'][i], text)
					elif type == 'video':
						media.attach_video(data['media'][i], text)

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

			mes = await bot.send_media_group(user_id, media)

	return mes


async def edit_post_text(post_id, text):
	post = Post.get(id=post_id)
	post.text = text
	post.save()

	sended_post = SendedPost.get_or_none(post_id=post_id)

	if sended_post:
		channel = Channel.get(id=sended_post.channel_id)
		channel_config = ChannelConfiguration.get(channel_id=channel.channel_id)
		if channel_config.auto_write:
			text += f'\n\n{channel_config.auto_write}'
		keyboard = inline.click_reaction(sended_post)
		try:
			await bot.edit_message_text(text=text, chat_id=channel.channel_id, message_id=sended_post.message_id, disable_web_page_preview=True, reply_markup=keyboard)
		except Exception as e:
			await bot.edit_message_caption(caption=text, chat_id=channel.channel_id, message_id=sended_post.message_id, reply_markup=keyboard)


def create_keyboard(markup):
	if markup is None:
		return
	kb = Keyboard.create()
	kb.save()
	s = markup.as_json()
	s = json.loads(s)
	s = s['inline_keyboard']
	for i in range(len(s)):
		for u in range(len(s[i])):
			try:
				b = Button.create(keyboard_id=kb.id, text=s[i][u]['text'], url=s[i][u]['url'], row=i, column=u)
				b.save()
			except Exception as e:
				pass
	return kb.id


async def edit_post_markup(post_id, reply_markup, reaction_with):
	key_id = create_keyboard(reply_markup)
	post = Post.get(id=post_id)

	if reaction_with is None:
		post = Post.get(id=post_id)
		post.keyboard_id = key_id
		post.reactions_id = reaction_with
		post.save()
	else:
		sended_post = SendedPost.get(post_id=post.id)
		channel = Channel.get(id=sended_post.channel_id)
		data = {
			'reply_markup': reply_markup,
			'channel_id': channel.channel_id
		}
		reply_markup, reaction_with = inline.add_reactions_without(data, reaction_with, message_id=sended_post.message_id)

		post.keyboard_id = key_id
		post.reactions_id = reaction_with
		post.save()

	sended_post = SendedPost.get_or_none(post_id=post_id)

	if sended_post:
		channel = Channel.get(id=sended_post.channel_id)
		await bot.edit_message_reply_markup(chat_id=channel.channel_id, message_id=sended_post.message_id, reply_markup=reply_markup)


async def edit_post_media(post_id, media):
	post = Post.get(id=post_id)
	old_media = post.media.split('$')
	print(old_media)
	print(media)
	media = list(reversed(media))
	if len(old_media) < len(media): return 1
	media_str = ''
	for i in media:
		media_str += f'{i}$'
	media_str = media_str[:-1]
	post.media = media_str
	post.save()

	sended_post = SendedPost.get_or_none(post_id=post_id)

	if sended_post:
		delta_media = len(old_media) - len(media)

		channel = Channel.get(id=sended_post.channel_id)

		text = post.text

		channel_config = ChannelConfiguration.get(channel_id=channel.channel_id)
		if channel_config.auto_write:
			text += f'\n\n{channel_config.auto_write}'

		reply_markup = inline.click_reaction(sended_post)

		for i in range(len(media)):
			try:
				print('photo is')
				mes = await bot.send_photo(config.TRASH_CHANNEL_ID, media[i])
				type = 'photo'

			except Exception as e:
				print('Except')
				mes = await bot.send_video(config.TRASH_CHANNEL_ID, media[i])
				type = 'video'
			if type == 'photo':
				if i == len(media) -1:
					media_obj = InputMediaPhoto(media[i], caption=text)
				else:
					media_obj = InputMediaPhoto(media[i])

			elif type == 'video':
				if i == len(media) -1:
					media_obj = InputMediaVideo(media[i], caption=text)
				else:
					media_obj = InputMediaVideo(media[i])
			try:
				await bot.edit_message_media(chat_id=channel.channel_id, message_id=sended_post.message_id - i, media=media_obj, reply_markup=reply_markup)
			except Exception as e:
				try:
					await bot.edit_message_media(chat_id=channel.channel_id, message_id=sended_post.message_id - i, media=media_obj)
				except Exception as e:
					pass

		print(f'Delta media: {delta_media}')
		for i in range(delta_media):
			print(sended_post.message_id - len(media) - i)
			await bot.delete_message(chat_id=channel.channel_id, message_id=sended_post.message_id - len(media) - i)


def swap_links_in_text(old_text: str, new_link):
	from bs4 import BeautifulSoup

	soup = BeautifulSoup(old_text, 'html.parser')
	try:
		link_soup = BeautifulSoup(new_link, 'html.parser')
		new_link_bs4 = new_link
		new_link_text = new_link
		for a in link_soup.findAll('a'):
			new_link_bs4 = a['href']
			new_link_text = str(a.string)
	except Exception as e: 
		new_link_bs4 = new_link
		new_link_text = new_link
	print(new_link_text)
	print(new_link_bs4)
	for a in soup.findAll('a'):
		a['href'] = a['href'].replace(a.get('href'), new_link_bs4)

	for b in soup.findAll('b'):
		if 'http://' in b.string or 'https://' in b.string:
			new_tag = soup.new_tag('a', href=new_link_bs4)
			new_text = soup.new_string(new_link_text)
			b.replace_with(new_text)
			new_tag.append(new_text)
			b.wrap(new_tag)

	for i in soup.findAll('i'):
		if 'http://' in i.string or 'https://' in i.string:
			i.replace_with(new_link)

	links_list = []

	old_text = str(soup)
	print(old_text)

	for i in old_text.split():
		if 'http://' == i[:7] or 'https://' == i[:8]:
			links_list.append(i)

	print(f'LINKS:', links_list)

	for old_link in links_list:
		old_text = old_text.replace(old_link, f' {new_link}')

	for i in old_text.split():
		if ' http://' in i or ' https://' in i:
			links_list.append(i)

	print(f'LINKS:', links_list)

	for old_link in links_list:
		old_text = old_text.replace(old_link, f' {new_link}')

	return old_text


def create_code_channel():
	import random
	strings = 'qwertyuiopadsfghjklzxcvbnm'
	code = ''
	for i in range(10):
		code += random.choice(strings)
	return code
