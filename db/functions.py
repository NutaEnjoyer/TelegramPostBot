import json
import time
from datetime import datetime
from pprint import pprint

from aiogram import types

from db.models import *
from handlers.other import tg_stat
from handlers.user import utils


def add_user(user_id: int):
	wallet = Wallet.get_or_none(user_id=user_id)
	if wallet is None:
		wallet = Wallet.create(user_id=user_id)
		wallet.save()
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


def add_channel(admin_id: int, channel_id: int, title: str, link: str):
	channel = Channel.get_or_none(channel_id=channel_id)
	if channel is None:
		channel = Channel.create(channel_id=channel_id, admin_id=admin_id, title=title)
		channel.save()
		configuration = ChannelConfiguration.create(channel_id=channel_id)
		configuration.save()
		schedule = Schedule.create(channel_id=channel_id)
		schedule.save()

		# add_find_channel(channel_id=channel_id, title=title, link=link)
		return channel

def add_find_channel(channel_id: int, title: str, link: str):
	channel = FindChannel.get_or_none(channel_id=channel_id)
	if channel is None:
		try:
			subscribers = tg_stat.get_channel_subscriber(channel_id)
			err = tg_stat.get_channel_err(channel_id)
			views = round(subscribers * err / 100)
		except Exception as e:
			subscribers = 0
			err = 0
			views = 0
			tg_stat.add_channel(link)
		channel = FindChannel.create(channel_id=channel_id, title=title, link=link, views=views, subscribers=subscribers, err=err, category=47)
		channel.save()
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
	# now point
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
	print('My data: ', data)
	post_info = None
	if data.get('reply_message_id') and data.get('main'):
		post_info = PostInfo.create(post_id=post.id, reply_message_id=data['reply_message_id'])
		post_info.save()
	if data.get('hidden_sequel'):
		if not post_info: post_info = PostInfo.create(post_id=post.id)
		post_info.hidden_sequel_text = data['hidden_sequel']
		post_info.hidden_sequel_button_text = data['hidden_sequel_button_text']
		post_info.save()
	if data.get('share_context'):
		if not post_info: post_info = PostInfo.create(post_id=post.id)
		result = ''
		for i in data['share_context']:
			result += str(i) + '$'
		result = result[:-1]
		post_info.SharePost = result
		post_info.save()


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
	from keyboards.inline import from_db_to_markup_by_key_id
	post_time = PostTime.get(id=post_time_id)
	print('Post Time:', post_time.post_id)
	dicts = DictObject.get_or_none(id=post_time.post_id)
	if dicts is None:
		return
	post_info = PostInfo.get_or_none(post_id=dicts.id)
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
	if post_info:
		data = {
			'channel_id': post_time.channel_id,
			'active': True,
			'date': None,
			'postpone': True,
			'reply_message_id': post_info.reply_message_id,
			'hidden_sequel_text': post_info.hidden_sequel_text,
			'hidden_sequel_button_text': post_info.hidden_sequel_button_text,
			'share_context': post_info.SharePost,
			'dicts': returned_dicts,
			'price': dicts.price
		}
	else:
		data = {
			'channel_id': post_time.channel_id,
			'active': True,
			'date': None,
			'postpone': True,
			'dicts': returned_dicts,
			'price': dicts.price
		}
	return data

def get_post_by_id_(post_time_id):
	post_time = PostTime.get(id=post_time_id)
	post = Post.get_or_none(id=post_time.post_id)
	post_info = PostInfo.get_or_none(post_id=post.id)
	if post is None:
		return
	media = post.media.split('$') if post.media else None
	#	await state.update_data(channel_id=channel_id, active=False, date=None, text='', media=[], reply_markup=None)
	if post_info:
		data = {
			'channel_id': post_time.channel_id,
			'active': True,
			'date': None,
			'text': post.text,
			'media': media,
			'reply_markup': None,
			'reaction_with': post.reactions_id if post.reactions_id else False,
			'postpone': True,
			'reply_message_id': post_info.reply_message_id,
			'hidden_sequel_text': post_info.hidden_sequel_text,
			'hidden_sequel_button_text': post_info.hidden_sequel_button_text,
			'share_context': post_info.SharePost,
		}
	else:
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
	post = DictObject.get(id=post_id)
	if post is None:
		return
	dicts = []
	dicts_list = Dict.select().where(Dict.object_id == post.id)
	for dict in dicts_list:
		d = {
			'type': dict.type,
			'file_id': dict.file_id,
			'text': dict.text,
			'reply_markup': create_reply_markup(dict.reply_markup)
		}
		dicts.append(d)
	data = {
		'active': True,
		'date': None,
		'dicts': dicts,
		'postpone': True
	}
	return data

def create_reply_markup(keyboard_id):
	if keyboard_id is None:
		return None

	buttons_select = Button.select().where(Button.keyboard_id == keyboard_id)
	keyboard = types.InlineKeyboardMarkup()

	row = 0
	buttons = []
	for b in buttons_select:
		if b.row == row:
			buttons.append(types.InlineKeyboardButton(text=b.text, url=b.url))
		else:
			keyboard.add(*buttons)
			buttons = [types.InlineKeyboardButton(text=b.text, url=b.url)]
			row += 1
	keyboard.add(*buttons)	

	return keyboard

def get_post_by_id_(post_time_id):
	post_time = PostTime.get(id=post_time_id)
	post = Post.get_or_none(id=post_time.post_id)
	post_info = PostInfo.get_or_none(post_id=post.id)
	if post is None:
		return
	media = post.media.split('$') if post.media else None
	#	await state.update_data(channel_id=channel_id, active=False, date=None, text='', media=[], reply_markup=None)
	if post_info:
		data = {
			'channel_id': post_time.channel_id,
			'active': True,
			'date': None,
			'text': post.text,
			'media': media,
			'reply_markup': None,
			'reaction_with': post.reactions_id if post.reactions_id else False,
			'postpone': True,
			'reply_message_id': post_info.reply_message_id,
			'hidden_sequel_text': post_info.hidden_sequel_text,
			'hidden_sequel_button_text': post_info.hidden_sequel_button_text,
			'share_context': post_info.SharePost,
		}
	else:
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

def from_post_id_to_data_(post_id):
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
	import datetime

	today = datetime.date.today().strftime('%Y-%m-%d')
	moscow_timezone = datetime.timezone(datetime.timedelta(hours=3))
	today_start = datetime.datetime.strptime(today, '%Y-%m-%d').replace(tzinfo=moscow_timezone)
	today_end = today_start + datetime.timedelta(days=1)

	today_start_time = int(today_start.timestamp()) + 24*60*60*day_delta
	today_end_time = int(today_end.timestamp()) + 24*60*60*day_delta

	print(f'Configuration:\nDay delta: {day_delta}\nStart_time={today_start_time}\nFinish_time={today_end_time}')
	sended_post = SendedPost.select().where((SendedPost.channel_id == channel_id) & (SendedPost.time.between(today_start_time, today_end_time)))

	time_posts = PostTime.select().where((PostTime.channel_id == channel_id) & (PostTime.time.between(today_start_time, today_end_time)) & (PostTime.active))
	time_posts = time_posts.order_by(PostTime.time.asc())

	posts: list = list(sended_post + time_posts)
	return posts

def get_all_schedule_content_plan(day_delta, channel_id):
	now_day = utils.get_today_number()

	print(channel_id)

	schedule = ChannelSchedule.get_or_none(channel_id=channel_id)

	if not schedule:
		return "<i>Нет расписания. Обратитесь к администратору канала!</i>\n"

	text = ''
	for i in range(10):
		line = getattr(schedule, f'place_{i+1}')
		if not line: break

		"🆓"
		"🏷️"

		ad_slot_1 = "✅" if utils.slot_status(schedule.channel_id, now_day + day_delta, i) else "❌"

		text += f"{line} {ad_slot_1}\n"

	return text


def get_advert_content_plan(day_delta, channel_id):
	import datetime

	today = datetime.date.today().strftime('%Y-%m-%d')
	moscow_timezone = datetime.timezone(datetime.timedelta(hours=3))
	today_start = datetime.datetime.strptime(today, '%Y-%m-%d').replace(tzinfo=moscow_timezone)
	today_end = today_start + datetime.timedelta(days=1)

	today_start_time = int(today_start.timestamp()) + 24*60*60*day_delta
	today_end_time = int(today_end.timestamp()) + 24*60*60*day_delta

	print(f'Configuration:\nDay delta: {day_delta}\nStart_time={today_start_time}\nFinish_time={today_end_time}')
	sended_post = SendedPost.select().where((SendedPost.channel_id == channel_id) & (SendedPost.time.between(today_start_time, today_end_time)))


	time_posts = PostTime.select().where((PostTime.channel_id == channel_id) & (PostTime.time.between(today_start_time, today_end_time)) & (PostTime.active))

	posts: list = list(sended_post + time_posts)
	posts.reverse()
	return_posts = []
	for ps in posts:
		p = DictObject.get(id=ps.post_id)
		if p.price:
			return_posts.append(ps)
	return return_posts


def get_all_schedule_posts(channel_id, advert):
	import time
	time_posts = PostTime.select().where((PostTime.channel_id == channel_id) & (PostTime.active))
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
