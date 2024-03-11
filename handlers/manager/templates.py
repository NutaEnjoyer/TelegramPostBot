from aiogram import types

from db.models import Manager, PostInfo

manager_button = "Уголок менеджера"

manager_text = """<b>( 〃● ₃● ) ~

🏘️ Это твой уголок 👩🏻‍💻</b>"""

make_post_button = "Создать пост"
make_repost_button = "Создать репост"
cabinet_button = "Личный кабинет"
schedule_button = "Расписание"
menu_button = "Меню"


def manager_menu():
	keyboard = types.ReplyKeyboardMarkup(
		resize_keyboard=True,
		keyboard=[
			# [types.KeyboardButton(make_post_button), types.KeyboardButton(make_repost_button)],
			[types.KeyboardButton(make_post_button)],
			[types.KeyboardButton(cabinet_button), types.KeyboardButton(schedule_button)],
			[types.KeyboardButton(menu_button)],
		]
	)

	return keyboard


###############################################################################

schedule_text = "Выберите канал"


def schedule_menu(channels):
	keyboards = types.InlineKeyboardMarkup()

	for channel in channels:
		b = types.InlineKeyboardButton(f"{channel.title}", callback_data=f"manager_open_channel_schedule${channel.id}")
		keyboards.add(b)

	return keyboards


def back_to_schedule_choose():
	keyboards = types.InlineKeyboardMarkup(
		inline_keyboard=[
			[types.InlineKeyboardButton("Назад 🔙", callback_data='back_to_schedule_choose')]
		]
	)

	return keyboards


######################################################

cabinet_message = "Личный кабинет 💼"

placement_stat_button = "Статистика размещений"
my_manage_channels_button = "Мои каналы"
channel_debt_button = "Задолжности каналов"
client_debt_button = "Задолжности клиентов"
main_menu_button = "Главное меню"


def cabinet_menu():
	keyboard = types.ReplyKeyboardMarkup(
		resize_keyboard=True,
		keyboard=[
			[types.KeyboardButton(my_manage_channels_button)],
			[types.KeyboardButton(placement_stat_button)],
			[types.KeyboardButton(channel_debt_button), types.KeyboardButton(client_debt_button)],
			[types.KeyboardButton(main_menu_button)],
		]
	)

	return keyboard


def cabinet_my_channels_message(channels):
	text = "*ੈ✩‧₊˚༺☆༻*ੈ✩‧₊˚\n<b>Ты менеджер следующих каналов:</b>\n\n"

	for channel in channels:
		text += f"""▪ <a href="{channel.invite_link}">{channel.title}</a>\n"""

	return text


channel_debt_message = "⋆༺𓆩☠︎︎𓆪༻\n<b>Задолжности каналов</b>"

client_debt_message = "⋆༺𓆩☠︎︎𓆪༻\n<b>Задолжности клиентов</b>"


def channel_debt_menu(debts):
	keyboards = types.InlineKeyboardMarkup()
	if len(debts) == 0:
		return keyboards
	manager = Manager.get(admin_id=debts[0][1].manager_id)
	for debt in debts:
		b = types.InlineKeyboardButton(f"💲 {debt[0].title} - {round(debt[1].price * manager.rate / 100, 2)}",
									   callback_data=f"open_channel_debt${debt[1].id}")
		keyboards.add(b)
	return keyboards


def client_debt_menu(debts):
	keyboards = types.InlineKeyboardMarkup()
	for debt in debts:
		b = types.InlineKeyboardButton(f"💲 {debt[1].client_name} - {debt[1].price} ₽",
									   callback_data=f"open_client_debt${debt[1].id}")
		keyboards.add(b)
	return keyboards

def client_debt_form_message(client, placement):
	text = f"<b>💁🏼‍♂️ Задолжность</b>\n\n<b>👤 Клиент: {client}</b>\n\n<b>💵 Размер: <code>{placement.price}</code></b>"

	return text


def channel_debt_form_message(channel, placement, rate):
	text = f"<b>💁🏼‍♂️ Задолжность</b>\n\n{channel}\n\n<b>💵 Размер: <code>{round(placement.price*rate/100, 2)}</code></b>"

	return text

def client_debt_manu(placement):
	keyboards = types.InlineKeyboardMarkup(
		inline_keyboard=[
			[types.InlineKeyboardButton("Оплачено ✅", callback_data=f'pay_client_debt${placement.id}')],
			[types.InlineKeyboardButton("Назад  🔙", callback_data=f'back_to_client_debt')],
		]
	)

	return keyboards

def channel_debt_manu(placement):
	keyboards = types.InlineKeyboardMarkup(
		inline_keyboard=[
			[types.InlineKeyboardButton("Оплачено ✅", callback_data=f'pay_channel_debt${placement.id}')],
			[types.InlineKeyboardButton("Назад  🔙", callback_data=f'back_to_channel_debt')],
		]
	)

	return keyboards

def back_placement_stat_menu():
	keyboards = types.InlineKeyboardMarkup(
		inline_keyboard=[
			[types.InlineKeyboardButton("Назад  🔙", callback_data=f'back_placement_stat')]
		]
	)

	return keyboards

def placement_stat_form(counts):
	text = f"""·:*¨༺ ♱✮♱ ༻¨*:·
<b>📊 Общая статистика

💸 За день: <code>{counts['day'][0]}</code> шт. <code>{counts['day'][1]}</code> ₽
💸 За неделю: <code>{counts['week'][0]}</code> шт. <code>{counts['week'][1]}</code> ₽
💸 За месяц: <code>{counts['month'][0]}</code> шт. <code>{counts['month'][1]}</code> ₽

💸 Всего: <code>{counts['full'][0]}</code> шт. <code>{counts['full'][1]}</code> ₽
</b>

<i>Для детальной статистики по опрделенному каналу выберите его в меню</i>
"""

	return text

def channel_placement_stat_form(channel, counts):
	text = f"""·:*¨༺ ♱✮♱ ༻¨*:·
<b>📊 Статистика канала <a href="{channel.invite_link}">{channel.title}</a>

💸 За день: <code>{counts['day'][0]}</code> шт. <code>{counts['day'][1]}</code> ₽
💸 За неделю: <code>{counts['week'][0]}</code> шт. <code>{counts['week'][1]}</code> ₽
💸 За месяц: <code>{counts['month'][0]}</code> шт. <code>{counts['month'][1]}</code> ₽

💸 Всего: <code>{counts['full'][0]}</code> шт. <code>{counts['full'][1]}</code> ₽
</b>

	"""

	return text

def placement_stat_menu(channels):
	keyboards = types.InlineKeyboardMarkup()

	for channel in channels:
		b = types.InlineKeyboardButton(f"{channel.title}", callback_data=f"open_channel_placement_stat${channel.id}")
		keyboards.add(b)

	return keyboards


poster_1_message = "Выберите канал"
poster_2_message = "Отправьте имя клиента. Оно нужно только для удобства вашей дальнейшей работы"
poster_3_message = "Теперь отправьте пост"

cancel_button = "Отмена ✘"

album_edit_message = "⚙️ Настройка поста"

def poster_reply_menu():
	keyboard = types.ReplyKeyboardMarkup(
		resize_keyboard=True,
		keyboard=[
			[types.KeyboardButton(cancel_button)],
		]
	)

	return keyboard

def poster_send_channel_menu(channels):
	keyboard = types.InlineKeyboardMarkup()
	for channel in channels:
		b = types.InlineKeyboardButton(f'{channel.title}', callback_data=f'poster_choose_channel${channel.id}')
		keyboard.add(b)

	return keyboard

def poster_send_post_menu(context=None):
	keyboard = types.InlineKeyboardMarkup()

	context = PostInfo.get_or_none(id=context) if context else None

	price = f': {context.price}' if context.price else ''

	b1 = types.InlineKeyboardButton(text='Изменить текст', callback_data='edit_text')
	b2 = types.InlineKeyboardButton(text='Изменить медиа', callback_data='edit_media')
	b3 = types.InlineKeyboardButton(text='URL-кнопки', callback_data='swap_keyboard')
	b5 = types.InlineKeyboardButton(text=f'Цена{price}', callback_data='edit_price')

	if context is None or context.with_comment:
		b6 = types.InlineKeyboardButton(text='Комментарии ✅', callback_data='swap_comments')
	else:
		b6 = types.InlineKeyboardButton(text='Комментарии ❌', callback_data='swap_comments')

	b7 = types.InlineKeyboardButton(text='Заменить ссылки', callback_data='swap_links')

	b8 = types.InlineKeyboardButton(text='Отмена', callback_data='back_post')
	b9 = types.InlineKeyboardButton(text='Дальше', callback_data='next_post')

	keyboard.add(b1, b2)
	keyboard.add(b3)
	keyboard.add(b5)
	keyboard.add(b6)
	keyboard.add(b7)
	keyboard.add(b8, b9)

	return keyboard

def only_back():
	keyboard = types.InlineKeyboardMarkup()
	b1 = types.InlineKeyboardButton(text='Назад', callback_data='back')
	keyboard.add(b1)

	return keyboard

send_changed_price_message = "Пришлите стоимость объявления"

poster_swap_keyboard_message = '''Отправь мне список URL-кнопок и/или рекций одним сообщением в следующем формате:

Одна кнопка в новом рядке:

<code>Кнопка 1 - http://t.me/durov
Кнопка 2 - http://vk.com/id1</code>


Используй разделитель |, чтобы добавить до трех кнопок в один ряд.


<code>Кнопка 1 - http://t.me/durov | Кнопка 2 - http://t.me/telepost_blog
Кнопка 3 - http://t.me/telepost_blog | Кнопка 4 - http://vk.com</code>'''

error_parse_keyboard = '''Ошибка парсинга клавиатуры'''

poster_swap_text_message = "Введите новый текст"
poster_swap_media_message = "Пришлите новое медиа"
poster_swap_links_message = "Пришлите новую ссылку"

poster_postpone_message = '''Отправь время, чтобы опубликовать пост сегодня.

Или отправь сразу время и дату, чтобы запланировать на любой другой день.
Например: <code>12:00</code> или <code>1200 16.9</code>'''

error_parse_time_message = '''Ошибка парсинга времени!'''


def moder_manager_post(id):
	keyboard = types.InlineKeyboardMarkup()

	b1 = types.InlineKeyboardButton(text='✅ Принять', callback_data=f'moder_manager_post_yes${id}')
	b2 = types.InlineKeyboardButton(text='❌ Отказать', callback_data=f'moder_manager_post_no${id}')
	b3 = types.InlineKeyboardButton(text='⏳ Другое время ⏳', callback_data=f'moder_manager_post_time${id}')

	keyboard.add(b1, b2)
	# keyboard.add(b3)

	return keyboard

def moder_manager_message(manager_placement, chat, channel):
	text = f"""<b><a href="{chat.url}">{chat.first_name} | Менеджер</a> отправил публикацию 🔝
	
Цена: {manager_placement.price}
Время: {manager_placement.human_time}

Канал: <a href="{channel.invite_link}">{channel.title}</a>
</b>"""

	return text


def paid_manager_message(manager_placement, url, chat, channel):
	print(chat)
	text = f"""<b><a href="{url}">{chat.first_name} | Менеджер</a> отметил как оплачено публикацию 💸

Цена: {manager_placement.price}
Время: {manager_placement.human_time}

Канал: <a href="{channel.invite_link}">{channel.title}</a>
</b>"""

	return text


def moder_manager_post_no_to_manager(manager_placement, channel):
	text = f"""<b>Администратор <a href="{channel.invite_link}">{channel.title}</a> отменил публикацию 🔝

Время: {manager_placement.human_time}

	</b>"""

	return text


def moder_manager_post_yes_to_manager(manager_placement, channel, manager):
	text = f"""<b>Администратор <a href="{channel.invite_link}">{channel.title}</a> подтвердил публикацию 🔝

Цена: {manager_placement.price}
Время: {manager_placement.human_time}

Канал: <a href="{channel.invite_link}">{channel.title}</a>

Оплатить рекламу ДО ВЫХОДА: {manager.requisites}
	</b>"""

	return text

def moder_manager_post_yes_to_manager_menu(id):
	return types.InlineKeyboardMarkup(
		inline_keyboard=[
			[types.InlineKeyboardButton("Оплатил 😎", callback_data=f"manager_post_paid${id}")]
		]
	)

def paid_manager_message_menu(id):
	return types.InlineKeyboardMarkup(
		inline_keyboard=[
			[types.InlineKeyboardButton("Оплачено 🤩", callback_data=f"manager_post_true_paid${id}")]
		]
	)