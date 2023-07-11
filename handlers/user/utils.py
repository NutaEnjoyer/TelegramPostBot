import json
from datetime import datetime
from pprint import pprint

import pytz
from aiogram import types, Bot
from aiogram.types import InputMediaPhoto, InputMediaVideo

from data import config
from db import functions
from db.models import Channel, NewJoin, ChannelConfiguration, SendedPost, ReactionsKeyboard, Post, Keyboard, Button, \
	Reaction
from handlers.user import TEXTS
from keyboards import inline

bot = Bot(token=config.ADMIN_TOKEN, parse_mode='HTML')


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


async def send_post_to_channel(channel_id, user_id, data, disable_web_prewiew=True):
	channel_config = ChannelConfiguration.get(channel_id=channel_id)
	print(data)

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

	text = data['text'] + f"\n\n{channel_config.auto_write if channel_config.auto_write else ''}"

	if data['media'] == [] or data['media'] is None:  # text message
		mes = await bot.send_message(channel_id, text, reply_markup=data['reply_markup'], disable_web_page_preview=channel_config.preview,
							   disable_notification=channel_config.post_without_sound)
		data['message_id'] = mes.message_id

	else:
		print('START! ELSE')

		if len(data['media']) == 1:
			try:
				mes = await bot.send_photo(channel_id, data['media'][0], caption=text, reply_markup=data['reply_markup'],
									 disable_notification=channel_config.post_without_sound)
			except Exception as e:
				mes = await bot.send_video(channel_id, data['media'][0], caption=text, reply_markup=data['reply_markup'],
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
	human_time = datetime.now(tz=pytz.timezone("Asia/Qatar")).strftime("%d-%m-%Y %H:%M")
	import time
	time = time.time()
	print('Under post')
	post = functions.create_sended_post(data, human_time=human_time, time=time, user_id=user_id)
	print(post)
	print('Post post')
	if channel_config.point:
		mes = await bot.pin_chat_message(channel_id, data['message_id'])


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

	currentSecond = datetime.now().second
	currentMinute = datetime.now().minute
	currentHour = datetime.now().hour
	currentDay = datetime.now().day
	currentMonth = datetime.now().month
	currentYear = datetime.now().year

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

	post_date = datetime(year=currentYear, month=month, day=day, hour=hour, minute=minut)
	now_date = datetime.now(tz=pytz.timezone("Asia/Qatar"))
	now_date = now_date.replace(tzinfo=None)
	if post_date < now_date:
		return

	delta = post_date - now_date
	print(f'Delta: {delta.seconds}')
	date = post_date.strftime("%d-%m-%Y %H:%M")

	return {
		'human_date': date,
		'seconds': delta.seconds
	}


async def send_post(data, user_id):
	channel = Channel.get(id=data['channel_id'])
	print(f'Data: ', data)
	if data['reaction_with'] is False:
		data['reaction_with'] = None

	try:
		await send_post_to_channel(channel_id=channel.channel_id, user_id=user_id, data=data, disable_web_prewiew=True)

	except Exception as e:
		print(e)
		admin_id = channel.admin_id
		if admin_id == user_id:
			await bot.send_message(admin_id, TEXTS.error_post_message_to_channel.format(title=channel.title))
		else:
			await bot.send_message(user_id, TEXTS.error_post_message_to_channel.format(title=channel.title))
			await bot.send_message(admin_id, TEXTS.error_post_message_to_channel.format(title=channel.title))


async def send_post_to_user(data, user_id):
	channel_id = user_id

	if data['media'] == [] or data['media'] is None:  # text message
		await bot.send_message(channel_id, data['text'], reply_markup=data['reply_markup'], disable_web_page_preview=True)

	else:
		if len(data['media']) == 1:
			try:
				await bot.send_photo(channel_id, data['media'][0], caption=data['text'], reply_markup=data['reply_markup'])
			except Exception as e:
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

	if data['media'] == [] or data['media'] is None:  # text message
		mes = await bot.send_message(user_id, text, reply_markup=data['reply_markup'],
									 disable_web_page_preview=True)

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
	for a in soup.findAll('a'):
		print(a['href'])
		a['href'] = a['href'].replace(a.get('href'), new_link)

	for b in soup.findAll('b'):
		if 'http://' in b.string or 'https://' in b.string:
			b.replace_with(new_link)

	links_list = []

	old_text = str(soup)

	for i in old_text.split():
		if ' http://' in i or ' https://' in i:
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

