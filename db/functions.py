import json
import time
from datetime import datetime
from pprint import pprint

from aiogram import types

from db.models import *


def add_user(user_id: int):
	user = Channel.get_or_none(admin_id=user_id)
	if user is None:
		user = User.create(user_id=user_id)
		user.save()
		return user

def add_admin(user_id: int):
	user = Admin.get_or_none(user_id=user_id)
	if user is None:
		user = Admin.create(user_id=user_id)
		user.save()
		return user


def add_channel(admin_id: int, channel_id: int, title: str):
	channel = Channel.get_or_none(channel_id=channel_id)
	if channel is None:
		channel = Channel.create(channel_id=channel_id, admin_id=admin_id, title=title)
		channel.save()
		configuration = ChannelConfiguration.create(channel_id=channel_id)
		configuration.save()
		return channel


def get_all_my_admin_channels(admin_id: int) -> list:
	channels = Channel.select().where(Channel.user_id == admin_id)
	return channels


def create_schedule(channel_id):
	sh = Schedule.get_or_none(channel_id=channel_id)
	if sh is None:
		sh = Schedule.create(channel_id=channel_id)
		sh.save()
		return sh


def update_schedule(schedule_id: int, posts_count=None, interval=None, week_interval=None, confirm=None, post_time=None, confirm_themes=None) -> None:
	schedule = Schedule.get_or_none(id=schedule_id)
	if schedule is None:
		return

	if posts_count:
		schedule.posts_count = posts_count

	if interval:
		schedule.interval = interval

	if week_interval:
		schedule.week_interval = week_interval

	if confirm:
		schedule.confirm = confirm

	if post_time:
		post = PostTime.create(schedule_id=schedule.id, time=post_time)
		post.save()

	if confirm_themes:
		schedule.confirm_themes = confirm_themes

	schedule.save()


def update_channel_configurations(channel_id: int, auto_write=None, water_mark=None, hour_line=None, preview=None, point=None, post_without_sound=None, reactions=None, auto_approve=None, collect_orders=None) -> None:
	channel_config = ChannelConfiguration.get(channel_id=channel_id)

	if auto_write:
		channel_config.auto_write = auto_write

	if water_mark:
		channel_config.water_mark = water_mark

	if hour_line:
		channel_config.hour_line = hour_line

	if not(preview is None):
		channel_config.preview = preview

	if not(point is None):
		channel_config.point = point

	if not(post_without_sound is None):
		channel_config.post_without_sound = post_without_sound

	if not(auto_approve is None):
		channel_config.auto_approve = auto_approve

	if not(collect_orders is None):
		channel_config.collect_orders = collect_orders

	if reactions:
		channel_config.reactions = reactions

	print(channel_config.preview)

	channel_config.save()
	return channel_config

def update_admin(admin_id: int, type=None, card_number=None, INN=None) -> None:
	admin = User.get(user_id=admin_id)

	if type:
		admin.type = type

	if card_number:
		admin.card_number = card_number

	if INN:
		admin.INN = INN

	admin.save()

def get_schedule(schedule_id: int) -> Schedule:
	return Schedule.get()


def create_post_time(data, time, human_date, user_id):
	pprint(data)
	media = ''
	for i in data['media']:
		media += i + '$'
	media = media[:-1]
	text = data['text']
	markup: types.InlineKeyboardMarkup = data['reply_markup']
	if markup is None:
		post = Post.create(media=media, text=text)
	else:
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
		print(s)
		post = Post.create(media=media, text=text, keyboard_id=kb.id, reactions_id=data.get('reaction_with'))
	post.save()
	post_time = PostTime.create(channel_id=data['channel_id'], post_id=post.id, time=time, human_time=human_date, user_id=user_id)
	post_time.save()


def create_sended_post(data, time, human_time, user_id):
	print(data)
	media = ''
	if data.get('media'):
		for i in data['media']:
			media += i + '$'
		media = media[:-1]

	text = data['text']
	markup: types.InlineKeyboardMarkup = data['reply_markup']
	if markup is None:
		post = Post.create(media=media, text=text)
	else:
		kb = Keyboard.create()
		kb.save()
		s = markup.as_json()
		s = json.loads(s)
		s = s['inline_keyboard']
		print('s', s)
		for i in range(len(s)):
			for u in range(len(s[i])):
				try:
					b = Button.create(keyboard_id=kb.id, text=s[i][u]['text'], url=s[i][u]['url'], row=i, column=u)
					b.save()
				except Exception as e:
					pass
		post = Post.create(media=media, text=text, keyboard_id=kb.id, reactions_id=data.get('reaction_with'))
	post.save()
	if data['channel_id'] < 0:
		channel = Channel.get(channel_id=data['channel_id'])
		data['channel_id'] = channel.id
	post_time = SendedPost.create(channel_id=data['channel_id'], message_id=data['message_id'], post_id=post.id, time=time, human_time=human_time, user_id=user_id)
	print(f'ID: {post_time.id}')
	post_time.save()

	return post_time

def get_post_by_id(post_time_id):
	post_time = PostTime.get(id=post_time_id)
	post = Post.get_or_none(id=post_time.post_id)
	if post is None:
		return
	media = post.media.split('$') if post.media else None
	#	await state.update_data(channel_id=channel_id, active=False, date=None, text='', media=[], reply_markup=None)
	data = {
		'channel_id': post_time.channel_id,
		'active': True,
		'date': None,
		'text': post.text,
		'media': media,
		'reply_markup': None,
		'reaction_with': post.reactions_id if post.reactions_id else False,
		'postpone': True
	}

	if post.keyboard_id is None:
		return data

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

	return data

def from_post_id_to_data(post_id):
	post = Post.get_or_none(id=post_id)
	if post is None:
		return
	media = post.media.split('$') if post.media else []
	#	await state.update_data(channel_id=channel_id, active=False, date=None, text='', media=[], reply_markup=None)
	data = {
		'active': True,
		'date': None,
		'text': post.text,
		'media': media,
		'reply_markup': None,
		'reaction_with': post.reactions_id if post.reactions_id else False,
		'postpone': True
	}

	if post.keyboard_id is None:
		return data

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

	return data

def get_all_content_plan(day_delta, channel_id):
	sended_posts = SendedPost.select().where(SendedPost.channel_id == channel_id)

	currentSecond = datetime.now().second
	currentMinute = datetime.now().minute
	currentHour = datetime.now().hour

	day_second = currentSecond + 60 * (currentMinute + (24 * currentHour))

	one_day = 24 * 60 * 60

	day_start = time.time() - day_second + day_delta * one_day
	day_finish = day_start + one_day

	print(f'{round(day_start)} - {round(day_finish)}')
	print(one_day)
	posts = []

	for sended_post in sended_posts:
		print(f'Sended post: ', sended_post.human_time, sended_post.time)
		if day_start < sended_post.time < day_finish:
			posts.append(sended_post)

	# posts = list(reversed(posts))

	time_posts = PostTime.select().where(PostTime.channel_id == channel_id)

	for time_post in time_posts:
		print(f'Time post: ', time_post.human_time, time_post.time)
		if day_start < time_post.time < day_finish and time_post.active:
			posts.append(time_post)

	return posts

def get_advert_content_plan(day_delta, channel_id):
	sended_posts = SendedPost.select().where(SendedPost.channel_id == channel_id)

	currentSecond = datetime.now().second
	currentMinute = datetime.now().minute
	currentHour = datetime.now().hour

	day_second = currentSecond + 60 * (currentMinute + (24 * currentHour))

	one_day = 24 * 60 * 60

	day_start = time.time() - day_second + day_delta * one_day
	day_finish = day_start + one_day

	print(f'{round(day_start)} - {round(day_finish)}')
	print(one_day)
	posts = []

	for sended_post in sended_posts:
		print(f'Sended post: ', sended_post.human_time, sended_post.time)
		post = Post.get(id=sended_post.post_id)
		if day_start < sended_post.time < day_finish and post.price:
			posts.append(sended_post)

	# posts = list(reversed(posts))

	time_posts = PostTime.select().where(PostTime.channel_id == channel_id)

	for time_post in time_posts:
		print(f'Time post: ', time_post.human_time, time_post.time)
		post = Post.get(id=time_post.post_id)

		if day_start < time_post.time < day_finish and time_post.active and post.price:
			posts.append(time_post)

	return posts


def get_all_schedule_posts(channel_id, advert):
	import time
	time_posts = PostTime.select().where(PostTime.channel_id == channel_id & PostTime.active)
	posts = []
	now_time = time.time()
	for post in time_posts:
		if post.time > now_time:
			if advert:
				post_ = Post.get(id=post.post_id)
				if post_.price:
					posts.append(post)
			else:
				posts.append(post)

	return posts
