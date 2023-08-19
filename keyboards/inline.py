from pprint import pprint

from aiogram import types
from bot_data import config
from db.models import ReactionsKeyboard, Reaction, Button, Post, FindChannel, Category, Saved, Basket, PostInfo


def setting_schedule(without=None):
	keyboard = types.InlineKeyboardMarkup()
	b2 = types.InlineKeyboardButton(text='Время выхода рекламы', callback_data='output_time')
	b1 = types.InlineKeyboardButton(text='Подтверждение', callback_data='confirm')
	b3 = types.InlineKeyboardButton(text='Минимальные интервалы публикаций', callback_data='output_interval')
	b4 = types.InlineKeyboardButton(text='Сохранить', callback_data='next')
	b5 = types.InlineKeyboardButton(text='Назад', callback_data='back')

	keyboard.add(b1)
	keyboard.add(b2)
	keyboard.add(b3)
	keyboard.add(b4)
	keyboard.add(b5)

	return keyboard

def only_back():
	keyboard = types.InlineKeyboardMarkup()
	b1 = types.InlineKeyboardButton(text='Назад', callback_data='back')
	keyboard.add(b1)

	return keyboard

def set_confirm():
	keyboard = types.InlineKeyboardMarkup()
	b1 = types.InlineKeyboardButton(text='Да', callback_data='confirm_yes')
	b2 = types.InlineKeyboardButton(text='Нет', callback_data='confirm_no')
	keyboard.add(b1, b2)
	return keyboard

def setting_keyboard():
	keyboard = types.InlineKeyboardMarkup()
	b2 = types.InlineKeyboardButton(text='Настройки канала', callback_data='setting_channel')
	b1 = types.InlineKeyboardButton(text='Добавить канал', callback_data='add_channel')
	b3 = types.InlineKeyboardButton(text='Партнерская программа', callback_data='referal_program')

	keyboard.add(b1)
	keyboard.add(b2)
	keyboard.add(b3)

	return keyboard

def advert_keyboard():
	keyboard = types.InlineKeyboardMarkup()
	b3 = types.InlineKeyboardButton(text='Заявки на взаимопиар', callback_data='offers_VP')
	b5 = types.InlineKeyboardButton(text='Разместить предложение на ВП', callback_data='add_offer_VP')
	b2 = types.InlineKeyboardButton(text='Рекламные креативы', callback_data='advert_creatives')
	b4 = types.InlineKeyboardButton(text='Замена ссылок в посте', callback_data='change_links')
	b1 = types.InlineKeyboardButton(text='Купить рекламу', callback_data='buy_advert')

	keyboard.add(b1)
	keyboard.add(b2)
	keyboard.add(b3)
	keyboard.add(b4)
	keyboard.add(b5)

	return keyboard

def cabinet_payment_data_keyboard():
	keyboard = types.InlineKeyboardMarkup()
	b2 = types.InlineKeyboardButton(text='Я физлицо', callback_data='phys-person')
	b3 = types.InlineKeyboardButton(text='Я самозанятый', callback_data='self-employed')
	b1 = types.InlineKeyboardButton(text='Я ИП/ООО', callback_data='IPOOO')
	b4 = types.InlineKeyboardButton(text='Назад', callback_data='back')

	keyboard.add(b1)
	keyboard.add(b2)
	keyboard.add(b3)
	keyboard.add(b4)

	return keyboard


def balance_my_wallet_keyboard():
	keyboard = types.InlineKeyboardMarkup()
	b1 = types.InlineKeyboardButton(text='Вывести средства', callback_data='phys-person')
	keyboard.add(b1)

	return keyboard

def advert_creatives_keyboard():
	keyboard = types.InlineKeyboardMarkup()
	b1 = types.InlineKeyboardButton(text='Создать самому', callback_data='self-made')
	b2 = types.InlineKeyboardButton(text='Заказать рекламный пост', callback_data='order_advert_post')
	b3 = types.InlineKeyboardButton(text='Назад', callback_data='back')

	keyboard.add(b1)
	keyboard.add(b2)
	keyboard.add(b3)

	return keyboard

def content_plan_keyboard():
	keyboard = types.InlineKeyboardMarkup()
	b2 = types.InlineKeyboardButton(text='Рекламный', callback_data='advert')
	b1 = types.InlineKeyboardButton(text='Общий', callback_data='all')
	b3 = types.InlineKeyboardButton(text='Назад', callback_data='back')

	keyboard.add(b1)
	keyboard.add(b2)
	keyboard.add(b3)

	return keyboard

def choose_channel(channels):
	keyboard = types.InlineKeyboardMarkup()
	for channel in channels:
		b = types.InlineKeyboardButton(text=channel.title, callback_data=f'{channel.id}')
		keyboard.add(b)

	return keyboard

def choose_category(pams=[]):
	keyboard = types.InlineKeyboardMarkup()

	b = types.InlineKeyboardButton(text='Все категории ' + ('✅' if 'all' in pams else ''), callback_data=f'choose_category$all$' + ('off' if 'all' in pams else 'on'))
	keyboard.add(b)
	b = types.InlineKeyboardButton(text='Каналы схожей тематики' + ('✅' if 'my' in pams else ''),
								   callback_data=f'choose_category$my$' + ('off' if 'my' in pams else 'on'))
	keyboard.add(b)

	for category in range(len(config.categories)):
		cat = config.categories[category]
		category = str(category)
		b = types.InlineKeyboardButton(text=f'{cat} ' + ('✅' if category in pams else ''),
									   callback_data=f'choose_category${category}$' + ('off' if category in pams else 'on'))
		keyboard.add(b)

	b = types.InlineKeyboardButton(text='Сохранить', callback_data=f'choose_category_end')
	keyboard.add(b)

	return keyboard


def add_card_number():
	keyboard = types.InlineKeyboardMarkup()
	b1 = types.InlineKeyboardButton(text='Добавить номер карты', callback_data='add_card_number')
	b2 = types.InlineKeyboardButton(text='Назад', callback_data='back')
	keyboard.add(b1)
	keyboard.add(b2)

	return keyboard


def add_card_number_ORD():
	keyboard = types.InlineKeyboardMarkup()
	b1 = types.InlineKeyboardButton(text='Добавить номер карты', callback_data='add_card_number')
	b2 = types.InlineKeyboardButton(text='Подключить ОРД', callback_data='add_ORD')
	b3 = types.InlineKeyboardButton(text='Назад', callback_data='back')
	keyboard.add(b1)
	keyboard.add(b2)
	keyboard.add(b3)

	return keyboard

def add_INN_ORD():
	keyboard = types.InlineKeyboardMarkup()
	b1 = types.InlineKeyboardButton(text='Добавить ИНН', callback_data='add_INN')
	b2 = types.InlineKeyboardButton(text='Подключить ОРД', callback_data='add_ORD')
	b3 = types.InlineKeyboardButton(text='Назад', callback_data='back')
	keyboard.add(b1)
	keyboard.add(b2)
	keyboard.add(b3)

	return keyboard

def rewrite_keyboard(start_markup):
	keyboard = types.InlineKeyboardMarkup()

	if start_markup:
		start_markup = start_markup['inline_keyboard']

		for u in start_markup:
			buttons = []

			for i in u:
				button = i
				buttons.append(button)

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
				keyboard.add(buttons[0], buttons[1], buttons[2], buttons[3], buttons[4], buttons[5], buttons[6], buttons[7])

	return keyboard

def add_markup_send_post(start_markup, is_album=False, context=None):
	if not start_markup:
		start_markup = types.InlineKeyboardMarkup()

	context = PostInfo.get_or_none(id=context) if context else None

	b1 = types.InlineKeyboardButton(text='Изменить текст', callback_data='edit_text')
	b2 = types.InlineKeyboardButton(text='Изменить медиа', callback_data='edit_media')
	b3 = types.InlineKeyboardButton(text='Изменить клавиатуру', callback_data='swap_keyboard')
	b4 = types.InlineKeyboardButton(text='Скрытое продолжение', callback_data='hidden_sequel')
	if context:
		if context.with_notification:
			b5 = types.InlineKeyboardButton(text='Уведомления ✅', callback_data='swap_notification')
		else:
			b5 = types.InlineKeyboardButton(text='Уведомления ❌', callback_data='swap_notification')
	b6 = types.InlineKeyboardButton(text='Комментарии', callback_data='swap_keyboard')
	b7 = types.InlineKeyboardButton(text='Подделиться', callback_data='share')
	b8 = types.InlineKeyboardButton(text='Копировать', callback_data='copy')
	b9 = types.InlineKeyboardButton(text='Заказать продвижение', callback_data='order_adv')
	b10 = types.InlineKeyboardButton(text='Ответный пост', callback_data='reply_post')

	start_markup.add(b1, b2)
	if not is_album:
		start_markup.add(b3)
	start_markup.add(b4)
	start_markup.add(b5, b6)
	start_markup.add(b7, b8)
	start_markup.add(b9)
	start_markup.add(b10)

	return start_markup


def message_will_post():
	keyboard = types.InlineKeyboardMarkup()
	b1 = types.InlineKeyboardButton(text='Опубликовать', callback_data='send_post_now')
	b2 = types.InlineKeyboardButton(text='Отложить', callback_data='postpone_post')
	b3 = types.InlineKeyboardButton(text='Назад', callback_data='back')
	keyboard.add(b1, b2)
	keyboard.add(b3)

	return keyboard


def postpone(data):
	keyboard = types.InlineKeyboardMarkup()
	date = data['post_date']
	if date == 0:
		b1 = types.InlineKeyboardButton(text='Сегодня ✅', callback_data='postpone_date$0')
	else:
		b1 = types.InlineKeyboardButton(text='Сегодня', callback_data='postpone_date$0')

	if date == 1:
		b2 = types.InlineKeyboardButton(text='Завтра ✅', callback_data='postpone_date$1')
	else:
		b2 = types.InlineKeyboardButton(text='Завтра', callback_data='postpone_date$1')

	if date == 2:
		b3 = types.InlineKeyboardButton(text='Послезавтра ✅', callback_data='postpone_date$2')
	else:
		b3 = types.InlineKeyboardButton(text='Послезавтра', callback_data='postpone_date$2')

	b4 = types.InlineKeyboardButton(text='Назад', callback_data='back')
	keyboard.add(b1, b2, b3)
	keyboard.add(b4)

	return keyboard

def parse_swap_keyboard(message_text, channel_id):
	rows = message_text.splitlines()
	keyboard = types.InlineKeyboardMarkup()
	reactions = None
	if not('-' in rows[-1]):
		reactions = rows[-1].split('/')
		rows = rows[:-1]

	for row in rows:
		start_buttons = row.split('|')
		buttons = []
		if len(start_buttons) > 8: return
		for button in start_buttons:
			but = button.split('-')
			btn = types.InlineKeyboardButton(text=but[0], url=but[1].strip())
			buttons.append(btn)
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
			keyboard.add(buttons[0], buttons[1], buttons[2], buttons[3], buttons[4], buttons[5], buttons[6], buttons[7])

	if reactions:
		reactions_db = ReactionsKeyboard.create(channel_id=channel_id, amount=len(reactions))
		reactions_db.save()

		buttons = []
		for i in reactions:
			r = Reaction.create(reaction_keyboard_id=reactions_db.id, text=i)
			r.save()
			b = types.InlineKeyboardButton(text=f'{r.value} {i}', callback_data=f'click_reaction${r.id}')
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
			keyboard.add(buttons[0], buttons[1], buttons[2], buttons[3], buttons[4], buttons[5], buttons[6], buttons[7])

		return keyboard, reactions_db.id

	else:
		return keyboard, None


def channel_setting():
	keyboard = types.InlineKeyboardMarkup()

	b1 = types.InlineKeyboardButton(text='Публикации', callback_data='public')
	b2 = types.InlineKeyboardButton(text='Управление принятием заявок', callback_data='application_manage')
	b3 = types.InlineKeyboardButton(text='Поддержка', callback_data='support')
	b4 = types.InlineKeyboardButton(text='Расписание', callback_data='schedule')
	b5 = types.InlineKeyboardButton(text='Рекламная ссылка', callback_data='ads_link')
	b6 = types.InlineKeyboardButton(text='Назад', callback_data='back')

	keyboard.add(b1)
	keyboard.add(b2)
	keyboard.add(b3)
	keyboard.add(b4)
	keyboard.add(b5)
	keyboard.add(b6)

	return keyboard

def public(channel_config):
	keyboard = types.InlineKeyboardMarkup()

	b1 = types.InlineKeyboardButton(text='Автоподпись', callback_data='auto_write')
	b2 = types.InlineKeyboardButton(text='Водяные знаки', callback_data='water_mark')
	b3 = types.InlineKeyboardButton(text='Часовой пояс', callback_data='hour_line')
	b4 = types.InlineKeyboardButton(text=f"Реакции", callback_data='reactions')
	b5 = types.InlineKeyboardButton(text=f"Превью: {'вкл' if channel_config.preview else 'выкл'}", callback_data='preview')
	b6 = types.InlineKeyboardButton(text=f"Закрепить {'✅' if channel_config.point else ''}", callback_data='point')
	b7 = types.InlineKeyboardButton(text=f"Без звука {'✅' if channel_config.post_without_sound else ''}", callback_data='post_without_sound')
	b8 = types.InlineKeyboardButton(text='Назад', callback_data='back')

	keyboard.add(b1)
	keyboard.add(b2)
	keyboard.add(b3)
	keyboard.add(b4)
	keyboard.add(b5)
	keyboard.add(b6)
	keyboard.add(b7)
	keyboard.add(b8)

	return keyboard

def time_zones():
	keyboard = types.InlineKeyboardMarkup()

	text = 'Etc/GMT'

	buttons = []
	for i in range(-11, 13):
		b = types.InlineKeyboardButton(text=text+(str(i) if i < 0 else '+'+str(i)), callback_data=f'time_zone${i}')
		buttons.append(b)

	for i in range(0, len(buttons), 2):
		keyboard.add(buttons[i], buttons[i+1])

	return keyboard


def application_manage(channel_config):
	keyboard = types.InlineKeyboardMarkup()

	b1 = types.InlineKeyboardButton(text=f"Автоприем {'вкл' if channel_config.auto_approve else 'выкл'}", callback_data='auto_approve')
	b2 = types.InlineKeyboardButton(text='Массовый прием', callback_data='full_approve')
	b3 = types.InlineKeyboardButton(text=f"Сбор базы входящих заявок {'вкл' if channel_config.collect_orders else 'выкл'}", callback_data='collect_orders')
	b4 = types.InlineKeyboardButton(text='Назад', callback_data='back')

	keyboard.add(b1)
	keyboard.add(b2)
	keyboard.add(b3)
	keyboard.add(b4)

	return keyboard


def add_reactions(data, reactions):
	keyboard = data['reply_markup']
	if keyboard is None:
		keyboard = types.InlineKeyboardMarkup()

	if type(reactions) == str and not reactions.isdigit():
		spl = reactions.split('/')

		reactions = ReactionsKeyboard.create(channel_id=data['channel_id'], amount=len(spl))
		reactions.save()

		buttons = []
		for i in spl:
			print('I = ', i)
			r = Reaction.create(reaction_keyboard_id=reactions.id, text=i)
			r.save()
			b = types.InlineKeyboardButton(text=f'{r.value} {r.text}', callback_data=f'click_reaction${r.id}')
			buttons.append(b)

	else:
		reactions = int(reactions)
		reaction_keyboard = ReactionsKeyboard.get(id=reactions)
		reactions_ = Reaction.select().where(Reaction.reaction_keyboard_id == reactions)

		print(f'reactions: ', reactions)
		print(len(reactions_))

		buttons = []
		for i in reactions_:
			b = types.InlineKeyboardButton(text=f'{i.value} {i.text}', callback_data=f'click_reaction${i.id}')
			buttons.append(b)

		reactions = reaction_keyboard


	print(f'buttons: ', buttons)
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
		keyboard.add(buttons[0], buttons[1], buttons[2], buttons[3], buttons[4], buttons[5], buttons[6], buttons[7])

	return keyboard, reactions.id


def add_reactions_without(data, reactions, message_id):
	keyboard = data['reply_markup']
	if keyboard is None:
		keyboard = types.InlineKeyboardMarkup()

	if type(reactions) == str and not reactions.isdigit():
		spl = reactions.split('/')

		reactions = ReactionsKeyboard.create(channel_id=data['channel_id'], message_id=message_id, amount=len(spl))
		reactions.save()

		buttons = []
		for i in spl:
			r = Reaction.create(reaction_keyboard_id=reactions.id, text=i)
			r.save()
			b = types.InlineKeyboardButton(text=f'{r.value} {r.text}', callback_data=f'click_reaction${r.id}')
			buttons.append(b)

	else:
		reactions = int(reactions)
		reaction_keyboard = ReactionsKeyboard.get(id=reactions)
		reactions_ = Reaction.select().where(Reaction.reaction_keyboard_id == reactions)

		buttons = []
		for i in reactions_:
			b = types.InlineKeyboardButton(text=f'{i.value} {i.text}', callback_data=f'click_reaction${i.id}')
			buttons.append(b)

		reactions = reaction_keyboard

	return keyboard, reactions.id


def click_reaction(post_arg, reaction_keyboard_id=None):
	keyboard = types.InlineKeyboardMarkup()
	post = Post.get(id=post_arg.post_id)

	if not(post.keyboard_id is None):

		buttons_select = Button.select().where(Button.keyboard_id == post.keyboard_id)

		row = 0
		buttons = []
		for b in buttons_select:
			pprint(b.text)
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

	print('success')
	if reaction_keyboard_id:
		reaction_keyboard = ReactionsKeyboard.get(id=reaction_keyboard_id)

		buttons = Reaction.select().where(Reaction.reaction_keyboard_id == reaction_keyboard.id)

		buttons = [types.InlineKeyboardButton(text=f'{i.value} {i.text}', callback_data=f'click_reaction${i.id}') for i
				   in buttons]


	else:
		reaction_keyboard = ReactionsKeyboard.select().where(ReactionsKeyboard.channel_id == post_arg.channel_id)

		correct = None
		for i in reaction_keyboard:
			if i.message_id == post_arg.message_id:
				correct = i

		if not correct:
			reaction_keyboard = ReactionsKeyboard.select().where(ReactionsKeyboard.channel_id == post_arg.channel_id)
			for i in reaction_keyboard:
				if i.message_id == post_arg.message_id:
					correct = i
			if not correct:
				return keyboard

		reaction_keyboard = correct

		buttons = Reaction.select().where(Reaction.reaction_keyboard_id==reaction_keyboard.id)

		buttons = [types.InlineKeyboardButton(text=f'{i.value} {i.text}', callback_data=f'click_reaction${i.id}') for i in buttons]

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


def all_content_plan_keyboard(time_delay, posts, without_date=False):
	import time
	import datetime

	keyboard = types.InlineKeyboardMarkup()
	for i in posts:
		post = Post.get(id=i.post_id)
		status = '✅' if i.time < time.time() else '⏳'
		post_text = 'Нет текста' if post.text == '' else (f'{post.text[:12]} ...' if len(post.text) > 12 else post.text)
		advert_status = '💰' if post.price else ''
		text = f'{i.human_time.split()[1]} {status} {post_text} {advert_status}'
		b = types.InlineKeyboardButton(text=str(text), callback_data=f'open_post${post.id}')
		keyboard.add(b)

	today = datetime.date.today() + datetime.timedelta(days=time_delay)
	tomorrow = today + datetime.timedelta(days=1)
	yesterday = today - datetime.timedelta(days=1)

	if not without_date:
		b1 = types.InlineKeyboardButton(text=f'← {config.WEEKDAYS[yesterday.weekday()]}, {yesterday.day} {config.MONTHS[yesterday.month]}', callback_data=f'open_all_content_plan${time_delay-1}')
		b2 = types.InlineKeyboardButton(text=f'{config.WEEKDAYS[today.weekday()]}, {today.day} {config.MONTHS[today.month]}', callback_data=f'open_all_content_plan${time_delay}')
		b3 = types.InlineKeyboardButton(text=f'{config.WEEKDAYS[tomorrow.weekday()]}, {tomorrow.day} {config.MONTHS[tomorrow.month]} →', callback_data=f'open_all_content_plan${time_delay+1}')

		b4 = types.InlineKeyboardButton(text=f'🔎 Все отложенные посты', callback_data=f'open_all_schedule_posts')
		b5 = types.InlineKeyboardButton(text=f'← Назад', callback_data=f'back')
		keyboard.add(b1, b2, b3)
		keyboard.add(b4)
		keyboard.add(b5)

	else:
		b4 = types.InlineKeyboardButton(text=f'🔎 Все посты', callback_data=f'open_all_content_plan$0')
		b5 = types.InlineKeyboardButton(text=f'← Назад', callback_data=f'back')
		keyboard.add(b4)
		keyboard.add(b5)

	return keyboard


def open_post(post_date, post):
	keyboard = types.InlineKeyboardMarkup()
	b1 = types.InlineKeyboardButton(text=f'Дата: {post_date}', callback_data=f'set_post_time')
	b2 = types.InlineKeyboardButton(text=f"Время удаления: {post.delete_human if post.delete_human else 'Не задано'}", callback_data=f'set_delete_time')
	if post.price:
		b3 = types.InlineKeyboardButton(text=f'💰 Рекламный ({post.price} руб.)', callback_data=f'set_price')
	else:
		b3 = types.InlineKeyboardButton(text=f'Указать цену', callback_data=f'set_price')

	b4 = types.InlineKeyboardButton(text=f'Изменить', callback_data=f'edit_post')
	b5 = types.InlineKeyboardButton(text=f'Дублировать', callback_data=f'copy_post')
	b6 = types.InlineKeyboardButton(text=f'Удалить', callback_data=f'delete_post')
	b7 = types.InlineKeyboardButton(text=f'← Назад', callback_data=f'back_to_all_content_plan')

	keyboard.add(b1)
	keyboard.add(b2)
	keyboard.add(b3)
	keyboard.add(b4)
	keyboard.add(b5)
	keyboard.add(b6)
	keyboard.add(b7)

	return keyboard

def edit_post(post_id):
	keyboard = types.InlineKeyboardMarkup()

	b2 = types.InlineKeyboardButton(text='Изменить медиа', callback_data='edit_media')
	b1 = types.InlineKeyboardButton(text='Изменить текст', callback_data='edit_text')
	b3 = types.InlineKeyboardButton(text='Изменить клавиатуру', callback_data='edit_markup')
	b4 = types.InlineKeyboardButton(text='← Назад', callback_data=f'open_post${post_id}')

	keyboard.add(b1)
	keyboard.add(b2)
	keyboard.add(b3)
	keyboard.add(b4)

	return keyboard


def edit_post_main(type=None):
	keyboard = types.InlineKeyboardMarkup()

	b2 = types.InlineKeyboardButton(text='Изменить медиа', callback_data='edit_media')
	b1 = types.InlineKeyboardButton(text='Изменить текст', callback_data='edit_text')
	b3 = types.InlineKeyboardButton(text='Изменить клавиатуру', callback_data='edit_markup')

	if type != 'text':
		keyboard.add(b1)
	keyboard.add(b2)
	if type != 'album':
		keyboard.add(b3)

	return keyboard


def recreate_reactions(channel_id, reactions):
	if type(reactions) is str and not(reactions.isdigit()):
		reactions = reactions.split('/')
	else:
		reactions = Reaction.select().where(Reaction.reaction_keyboard_id==int(reactions))

	reactions_db = ReactionsKeyboard.create(channel_id=channel_id, amount=len(reactions))
	reactions_db.save()

	buttons = []
	for i in reactions:
		r = Reaction.create(reaction_keyboard_id=reactions_db.id, text=i)
		r.save()
		b = types.InlineKeyboardButton(text=f'{r.value} {i}', callback_data=f'click_reaction${r.id}')
		buttons.append(b)


	return reactions_db.id


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

def setting_filters():
	keyboard = types.InlineKeyboardMarkup()

	b1 = types.InlineKeyboardButton(text='Средний охват поста ERR', callback_data='filter_err')
	b2 = types.InlineKeyboardButton(text='Охват', callback_data='filter_views')
	b3 = types.InlineKeyboardButton(text='Подписчики', callback_data='filter_sub')
	b4 = types.InlineKeyboardButton(text='Показать результаты', callback_data='filter_show_result')
	b5 = types.InlineKeyboardButton(text='В меню', callback_data='back')

	keyboard.add(b1)
	keyboard.add(b2)
	keyboard.add(b3)
	keyboard.add(b4)
	keyboard.add(b5)

	return keyboard

def choose_find_channel(channels, page=1):
	keyboard = types.InlineKeyboardMarkup()

	for channel in channels[10 * (page - 1):10 * page]:
		b = types.InlineKeyboardButton(text=channel.title, callback_data=f'open_find_channel${channel.id}')
		keyboard.add(b)

	if page > 1:
		if page < len(channels) // 10 + 1 if len(channels) % 10 else 0:
			b1 = types.InlineKeyboardButton(text='⬅️', callback_data=f'change_page_to_find_channel${page - 1}')
			b2 = types.InlineKeyboardButton(text='➡️', callback_data=f'change_page_to_find_channel${page + 1}')

			keyboard.add(b1, b2)
		else:
			b1 = types.InlineKeyboardButton(text='⬅️', callback_data=f'change_page_to_find_channel${page - 1}')

			keyboard.add(b1)
	else:
		if page < len(channels) // 10 + 1 if len(channels) % 10 else 0:
			b2 = types.InlineKeyboardButton(text='➡️', callback_data=f'change_page_to_find_channel${page + 1}')

			keyboard.add(b2)

	b = types.InlineKeyboardButton(text='◀️ Назад', callback_data=f'back_page_to_find')
	keyboard.add(b)

	return keyboard

def basket(channels, page=1):
	keyboard = types.InlineKeyboardMarkup()

	for channel in channels[8 * (page - 1):8 * page]:
		b = types.InlineKeyboardButton(text=channel.title, callback_data=f'open_basket_channel${channel.id}')
		keyboard.add(b)

	if page > 1:
		if page < len(channels) // 10 + 1 if len(channels) % 10 else 0:
			b1 = types.InlineKeyboardButton(text='⬅️', callback_data=f'change_page_basket_channel${page - 1}')
			b2 = types.InlineKeyboardButton(text='➡️', callback_data=f'change_page_basket_channel${page + 1}')

			keyboard.add(b1, b2)
		else:
			b1 = types.InlineKeyboardButton(text='⬅️', callback_data=f'change_page_basket_channel${page - 1}')

			keyboard.add(b1)
	else:
		if page < len(channels) // 10 + 1 if len(channels) % 10 else 0:
			b2 = types.InlineKeyboardButton(text='➡️', callback_data=f'change_page_basket_channel${page + 1}')

			keyboard.add(b2)

	b1 = types.InlineKeyboardButton(text='➕ Добавить', callback_data=f'add_basket_channel')
	b2 = types.InlineKeyboardButton(text='🗑 Очистить', callback_data=f'delete_all_basket_channels')
	b3 = types.InlineKeyboardButton(text='📊 Статистика', callback_data=f'load_basket_stat')
	b4 = types.InlineKeyboardButton(text='🛒 К оформлению', callback_data=f'order_basket')
	keyboard.add(b1)
	keyboard.add(b2)
	keyboard.add(b3)
	keyboard.add(b4)

	return keyboard

def back_to_find_channel(user_id, id):
	keyboard = types.InlineKeyboardMarkup()

	saved = Saved.select().where(Saved.user_id == user_id)
	in_saved = id in [i.find_channel_id for i in saved]

	basket = Basket.select().where(Basket.user_id == user_id)
	in_basket = id in [i.find_channel_id for i in basket]

	if in_basket:
		b1 = types.InlineKeyboardButton(text='Перейти в корзину', callback_data=f'go_to_basket')
	else:
		b1 = types.InlineKeyboardButton(text='Добавить в корзину', callback_data=f'basket_find_channel${id}')
	if in_saved:
		b2 = types.InlineKeyboardButton(text='⭐️ Избранное', callback_data=f'save_find_channel${id}')
	else:
		b2 = types.InlineKeyboardButton(text='Избранное', callback_data=f'save_find_channel${id}')
	b3 = types.InlineKeyboardButton(text='Назад', callback_data=f'back_to_find_channel')

	keyboard.add(b1)
	keyboard.add(b2)
	keyboard.add(b3)

	return keyboard

def my_saved(channels):
	channels = [FindChannel.get(id=i.find_channel_id) for i in channels]
	keyboard = types.InlineKeyboardMarkup()
	for channel in channels:
		b1 = types.InlineKeyboardButton(text=channel.title, callback_data=f'open_saved_channel${channel.id}')
		keyboard.add(b1)

	b2 = types.InlineKeyboardButton(text='Назад', callback_data=f'back')
	keyboard.add(b2)

	return keyboard

def back_to_saved_channel(id):
	keyboard = types.InlineKeyboardMarkup()

	b1 = types.InlineKeyboardButton(text='Удалить', callback_data=f'delete_saved_channel${id}')
	b2 = types.InlineKeyboardButton(text='Назад', callback_data=f'back_to_saved_channels')

	keyboard.add(b1)
	keyboard.add(b2)

	return keyboard

def choose_payment_type():
	keyboard = types.InlineKeyboardMarkup()

	b1 = types.InlineKeyboardButton(text='Оплата картой', callback_data=f'payments_card')
	b2 = types.InlineKeyboardButton(text='Оплата по безналу', callback_data=f'payments_bill')
	b3 = types.InlineKeyboardButton(text='Назад', callback_data=f'back_form_order')

	keyboard.add(b1)
	keyboard.add(b2)
	keyboard.add(b3)

	return keyboard

def choose_cat(page=1):
	keyboard = types.InlineKeyboardMarkup()

	pre_cats = Category.select()

	cats = pre_cats[10*(page-1):10*page]
	print(cats)

	for cat in cats:
		b = types.InlineKeyboardButton(text=cat.name_ru, callback_data=f'choose_cat_to_find${cat.id}')
		keyboard.add(b)

	if page > 1:
		if page < len(pre_cats) // 10 + 1 if len(pre_cats) % 10 else 0:
			b1 = types.InlineKeyboardButton(text='⬅️', callback_data=f'change_page_to_find${page-1}')
			b2 = types.InlineKeyboardButton(text='➡️', callback_data=f'change_page_to_find${page+1}')

			keyboard.add(b1, b2)

		else:
			b1 = types.InlineKeyboardButton(text='⬅️', callback_data=f'change_page_to_find${page - 1}')

			keyboard.add(b1)
	else:
		if page < len(pre_cats) // 10 + 1 if len(pre_cats) % 10 else 0:
			b2 = types.InlineKeyboardButton(text='➡️', callback_data=f'change_page_to_find${page + 1}')

			keyboard.add(b2)

	return keyboard


def order_keyboard(url):
	keyboard = types.InlineKeyboardMarkup()

	b1 = types.InlineKeyboardButton(text='Оплата', url=url)

	keyboard.add(b1)

	return keyboard

def valid_inn(user_id):
	keyboard = types.InlineKeyboardMarkup()

	b1 = types.InlineKeyboardButton(text='Одобрено', callback_data=f'valid_inn${user_id}')

	keyboard.add(b1)

	return keyboard

def back_to_filters():
	keyboard = types.InlineKeyboardMarkup()

	b1 = types.InlineKeyboardButton(text='Назад', callback_data=f'back_to_filters')

	keyboard.add(b1)

	return keyboard

def filters_err():
	keyboard = types.InlineKeyboardMarkup()

	b1 = types.InlineKeyboardButton(text='0-20%', callback_data=f'filters_err${1}')
	b2 = types.InlineKeyboardButton(text='20-40%', callback_data=f'filters_err${2}')
	b3 = types.InlineKeyboardButton(text='40-60%', callback_data=f'filters_err${3}')
	b4 = types.InlineKeyboardButton(text='60-80%', callback_data=f'filters_err${4}')
	b5 = types.InlineKeyboardButton(text='80-100%', callback_data=f'filters_err${5}')
	b6 = types.InlineKeyboardButton(text='Назад', callback_data=f'back_to_filters')

	keyboard.add(b1)
	keyboard.add(b2)
	keyboard.add(b3)
	keyboard.add(b4)
	keyboard.add(b5)
	keyboard.add(b6)

	return keyboard

def choose_basket_channel(channel_id):
	keyboard = types.InlineKeyboardMarkup()

	b1 = types.InlineKeyboardButton(text='🗑 Удалить', callback_data=f'delete_basket_channel${channel_id}')
	b2 = types.InlineKeyboardButton(text='⬅️ Назад', callback_data=f'back_to_basket')

	keyboard.add(b1)
	keyboard.add(b2)

	return keyboard

def myself_cabinet():
	keyboard = types.InlineKeyboardMarkup()

	b1 = types.InlineKeyboardButton(text='Статистика размещений', callback_data=f'placement_stat')
	b2 = types.InlineKeyboardButton(text='Мои платежные данные', callback_data=f'payment_data')
	b3 = types.InlineKeyboardButton(text='Мои посты', callback_data=f'my_posts')

	keyboard.add(b1)
	keyboard.add(b2)
	keyboard.add(b3)

	return keyboard


def pre_post_keyboard():
	keyboard = types.InlineKeyboardMarkup()

	b1 = types.InlineKeyboardButton(text='Заказать рекламу', callback_data=f'go_post')
	b2 = types.InlineKeyboardButton(text='Заказать репост', callback_data=f'None')
	b3 = types.InlineKeyboardButton(text='Заказать статью', callback_data=f'None')
	b4 = types.InlineKeyboardButton(text='Назад', callback_data=f'back_form_order')

	keyboard.add(b1)
	keyboard.add(b2)
	keyboard.add(b3)
	keyboard.add(b4)

	return keyboard

def moder_post():
	keyboard = types.InlineKeyboardMarkup()

	b1 = types.InlineKeyboardButton(text='✅ Принять', callback_data=f'go_post')
	b2 = types.InlineKeyboardButton(text='❌ Отказать', callback_data=f'None')

	keyboard.add(b1, b2)

	return keyboard

def my_posts(posts):
	import re

	CLEANR = re.compile('<.*?>')

	def cleanhtml(raw_html):
		cleantext = re.sub(CLEANR, '', raw_html)
		return cleantext
	keyboard = types.InlineKeyboardMarkup()

	for post in posts:
		current_post = Post.get(id=post.post_id)
		b = types.InlineKeyboardButton(text=f"{re.sub(CLEANR, '', current_post.text)[:20]}..", callback_data=f'open_my_post${post.id}')
		keyboard.add(b)

	b3 = types.InlineKeyboardButton(text='Добавить', callback_data=f'add_my_post')
	b4 = types.InlineKeyboardButton(text='Назад', callback_data=f'back')

	keyboard.add(b3)
	keyboard.add(b4)

	return keyboard

def from_db_to_markup_by_key_id(key_id):
	if key_id is None:
		return None

	keyboard = types.InlineKeyboardMarkup()
	buttons_select = Button.select().where(Button.keyboard_id == key_id)

	row = 0
	buttons = []
	for b in buttons_select:
		pprint(b.text)
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

	return keyboard

def my_post_panel(my_post_id):
	keyboard = types.InlineKeyboardMarkup()

	b1 = types.InlineKeyboardButton('Удалить', callback_data=f'delete_my_post${my_post_id}')
	b2 = types.InlineKeyboardButton('Назад', callback_data=f'back_to_my_posts')

	keyboard.add(b1)
	keyboard.add(b2)

	return keyboard

def start_channel(user_id, id):
	keyboard = types.InlineKeyboardMarkup()

	saved = Saved.select().where(Saved.user_id == user_id)
	in_saved = id in [i.find_channel_id for i in saved]

	basket = Basket.select().where(Basket.user_id == user_id)
	in_basket = id in [i.find_channel_id for i in basket]

	if in_basket:
		b1 = types.InlineKeyboardButton(text='Перейти в корзину', callback_data=f'go_to_basket')
	else:
		b1 = types.InlineKeyboardButton(text='Добавить в корзину', callback_data=f'basket_find_channel${id}')
	if in_saved:
		b2 = types.InlineKeyboardButton(text='⭐️ Избранное', callback_data=f'save_find_channel${id}')
	else:
		b2 = types.InlineKeyboardButton(text='Избранное', callback_data=f'save_find_channel${id}')

	keyboard.add(b1)
	keyboard.add(b2)

	return keyboard
