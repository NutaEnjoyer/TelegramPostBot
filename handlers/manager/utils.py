import json

from aiogram import types

from bot.start_bot_container import bot
from db.models import *
from bot_data import config

from handlers.user.utils import parse_time

import time



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

def content_plan_text(posts_1, posts_2, posts_3):

	import datetime
	import pytz

	texts = "( •_ •) ▬▬ι═══════ﺤ\n"

	today = datetime.datetime.now(tz=pytz.timezone("Asia/Qatar")).today() + datetime.timedelta(days=0)
	texts += f'<b>Сегодня {config.WEEKDAYS[today.weekday()]}, {str(today.day)} {config.MONTHS[today.month]}\n\n</b>'
	texts += posts_1

	today = datetime.datetime.now(tz=pytz.timezone("Asia/Qatar")).today() + datetime.timedelta(days=1)

	texts += f"<b>\nЗавтра {config.WEEKDAYS[today.weekday()]}, {str(today.day)} {config.MONTHS[today.month]}\n\n</b>"
	texts += posts_2


	today = datetime.datetime.now(tz=pytz.timezone("Asia/Qatar")).today() + datetime.timedelta(days=2)
	texts += f"<b>\nПослезавтра {config.WEEKDAYS[today.weekday()]}, {str(today.day)} {config.MONTHS[today.month]}\n\n</b>"
	texts += posts_3

	return texts





def old_content_plan_text(posts_1, posts_2, posts_3):
	import time
	import datetime
	import pytz

	today = datetime.datetime.now(tz=pytz.timezone("Asia/Qatar")).today() + datetime.timedelta(days=0)
	texts = "( •_ •) ▬▬ι═══════ﺤ\n"

	texts += f'<b>Сегодня {config.WEEKDAYS[today.weekday()]}, {str(today.day)} {config.MONTHS[today.month]}\n\n</b>'

	for i in posts_1:
		post = DictObject.get(id=i.post_id)
		dicts = Dict.select().where(Dict.object_id == post.id)
		dict_text = ''
		for dict in dicts:
			dict_text = dict.text if dict.text else dict_text
		from bs4 import BeautifulSoup

		html_code = dict_text

		soup = BeautifulSoup(html_code, 'html.parser')
		result = ''
		no_tag = True
		for element in soup.find_all():
			no_tag = False
			if element.string:
				result += element.string

		if no_tag:
			dict_text = html_code
		else:
			dict_text = result

		status = '✅' if i.time < time.time() else '⏳'
		type = ''
		match dicts[0].type:
			case 'photo':
				type = '🏞'
			case 'video':
				type = '🎥'
			case 'voice':
				type = '🗣'
			case 'audio':
				type = '🎵'
			case 'document':
				type = '📄'
			case 'animation':
				type = '🎦'
			case 'sticker':
				type = '😄'
			case 'video_note':
				type = '👁'
			case 'poll':
				type = '📣'
			case 'text':
				type = '📝'

		post_text = 'Нет текста' if not dict_text else (f'{dict_text[:12]} ...' if len(dict_text) > 12 else dict_text)
		advert_status = '💰' if post.price else ''

		text = f'▪ {i.human_time.split(",")[0]} {status} {type} {post_text} {advert_status}\n'

		texts += text

	if len(posts_1) == 0:
		texts += '▪ Free 🆓\n'

	today = datetime.datetime.now(tz=pytz.timezone("Asia/Qatar")).today() + datetime.timedelta(days=1)

	texts += f"<b>\nЗавтра {config.WEEKDAYS[today.weekday()]}, {str(today.day)} {config.MONTHS[today.month]}\n\n</b>"

	for i in posts_2:
		post = DictObject.get(id=i.post_id)
		dicts = Dict.select().where(Dict.object_id == post.id)
		dict_text = ''
		for dict in dicts:
			dict_text = dict.text if dict.text else dict_text
		from bs4 import BeautifulSoup

		html_code = dict_text

		soup = BeautifulSoup(html_code, 'html.parser')
		result = ''
		no_tag = True
		for element in soup.find_all():
			no_tag = False
			if element.string:
				result += element.string

		if no_tag:
			dict_text = html_code
		else:
			dict_text = result

		status = '✅' if i.time < time.time() else '⏳'
		type = ''
		match dicts[0].type:
			case 'photo':
				type = '🏞'
			case 'video':
				type = '🎥'
			case 'voice':
				type = '🗣'
			case 'audio':
				type = '🎵'
			case 'document':
				type = '📄'
			case 'animation':
				type = '🎦'
			case 'sticker':
				type = '😄'
			case 'video_note':
				type = '👁'
			case 'poll':
				type = '📣'
			case 'text':
				type = '📝'

		post_text = 'Нет текста' if not dict_text else (f'{dict_text[:12]} ...' if len(dict_text) > 12 else dict_text)
		advert_status = '💰' if post.price else ''

		text = f'▪ {i.human_time.split(",")[0]} {status} {type} {post_text} {advert_status}\n'

		texts += text

	if len(posts_2) == 0:
		texts += '▪ Free 🆓\n'

	today = datetime.datetime.now(tz=pytz.timezone("Asia/Qatar")).today() + datetime.timedelta(days=2)

	texts += f"<b>\nПослезавтра {config.WEEKDAYS[today.weekday()]}, {str(today.day)} {config.MONTHS[today.month]}\n\n</b>"

	for i in posts_3:
		post = DictObject.get(id=i.post_id)
		dicts = Dict.select().where(Dict.object_id == post.id)
		dict_text = ''
		for dict in dicts:
			dict_text = dict.text if dict.text else dict_text
		from bs4 import BeautifulSoup

		html_code = dict_text

		soup = BeautifulSoup(html_code, 'html.parser')
		result = ''
		no_tag = True
		for element in soup.find_all():
			no_tag = False
			if element.string:
				result += element.string

		if no_tag:
			dict_text = html_code
		else:
			dict_text = result

		status = '✅' if i.time < time.time() else '⏳'
		type = ''
		match dicts[0].type:
			case 'photo':
				type = '🏞'
			case 'video':
				type = '🎥'
			case 'voice':
				type = '🗣'
			case 'audio':
				type = '🎵'
			case 'document':
				type = '📄'
			case 'animation':
				type = '🎦'
			case 'sticker':
				type = '😄'
			case 'video_note':
				type = '👁'
			case 'poll':
				type = '📣'
			case 'text':
				type = '📝'

		post_text = 'Нет текста' if not dict_text else (f'{dict_text[:12]} ...' if len(dict_text) > 12 else dict_text)
		advert_status = '💰' if post.price else ''

		text = f'▪ {i.human_time.split(",")[0]} {status} {type} {post_text} {advert_status}\n'

		texts += text

	if len(posts_3) == 0:
		texts += '▪ Free 🆓\n'

	return texts


async def get_client_debt(manager_id):

	channels = ManagerPlacement.select().where((ManagerPlacement.manager_id == manager_id) & ManagerPlacement.active &
											(~ManagerPlacement.is_paid))
	channels = [[None, i] for i in channels]
	return channels


async def get_channel_debt(manager_id):
	channels = ManagerPlacement.select().where((ManagerPlacement.manager_id == manager_id) & (~ManagerPlacement.fee_is_paid) &
											   ManagerPlacement.is_paid)
	channels = [[await bot.get_chat(i.channel_id), i] for i in channels]
	return channels


def get_counts(places):
	day_delay = 24 * 60 * 60
	week_delay = 7 * day_delay
	month_delay = 30 * day_delay

	current_time = time.time()

	counts = {
		'day': [0, 0],
		'week': [0, 0],
		'month': [0, 0],
		'full': [0, 0]
	}

	for place in places:
		time_difference = current_time - place.time
		if time_difference < day_delay:
			counts['day'][0] += 1
			counts['day'][1] += place.price
		if time_difference < week_delay:
			counts['week'][0] += 1
			counts['week'][1] += place.price
		if time_difference < month_delay:
			counts['month'][0] += 1
			counts['month'][1] += place.price
		counts['full'][0] += 1
		counts['full'][1] += place.price

	return counts

def placement_stat(manager_id):
	places = ManagerPlacement.select().where(
		(ManagerPlacement.manager_id == manager_id) &
		ManagerPlacement.is_paid
	)

	return get_counts(places)


def channel_placement_stat(manager_id, channel_id):
	places = ManagerPlacement.select().where(
		(ManagerPlacement.manager_id == manager_id) &
		(ManagerPlacement.channel_id == channel_id) &
		ManagerPlacement.is_paid
	)

	return get_counts(places)


async def convert_message(message: types.Message, state):
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


async def next_message_exists(message):
	flag = True
	try:
		mes = await bot.copy_message(config.TRASH_CHANNEL_ID, message.from_user.id, message_id=message.message_id + 1)
		await bot.delete_message(config.TRASH_CHANNEL_ID, mes.message_id)
	except Exception as e:
		flag = False
	return flag


async def simple_send_message_dict(dict, chat_id):
	match dict['type']:
		case 'photo':
			return await bot.send_photo(chat_id, dict['file_id'], caption=dict['text'],
										reply_markup=dict['reply_markup'])
		case 'video':
			return await bot.send_video(chat_id, dict['file_id'], caption=dict['text'],
										reply_markup=dict['reply_markup'])
		case 'voice':
			return await bot.send_voice(chat_id, dict['file_id'], caption=dict['text'],
										reply_markup=dict['reply_markup'])
		case 'audio':
			return await bot.send_audio(chat_id, dict['file_id'], caption=dict['text'],
										reply_markup=dict['reply_markup'])
		case 'document':
			return await bot.send_document(chat_id, dict['file_id'], caption=dict['text'],
										   reply_markup=dict['reply_markup'])
		case 'animation':
			return await bot.send_animation(chat_id, dict['file_id'])
		case 'sticker':
			return await bot.send_sticker(chat_id, dict['file_id'])
		case 'video_note':
			return await bot.send_video_note(chat_id, dict['file_id'], reply_markup=dict['reply_markup'])
		case 'text':
			return await bot.send_message(chat_id, dict['text'], reply_markup=dict['reply_markup'])


async def group_send_message_dict(dicts, chat_id):
	media_group = types.MediaGroup()
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


def swap_links_in_markup(old_markup: types.InlineKeyboardMarkup, new_link):
	if old_markup is None:
		return
	m = old_markup.to_python()
	m = m['inline_keyboard']
	print(type(m))
	print(m)
	keyboard = types.InlineKeyboardMarkup()
	for i in m:
		buttons = []
		for u in i:
			b = types.InlineKeyboardButton(text=u['text'], url=new_link)
			buttons.append(b)
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

	return keyboard


def calculate_future_date(days_ahead):
	from datetime import datetime, timedelta

	days = (datetime.now() - datetime(1970, 1, 1)).days
	today = datetime.now()
	future_date = today + timedelta(days=days_ahead-days)
	return future_date.strftime('%d.%m')
