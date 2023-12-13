from db.models import *

start = '''Добро пожаловать в бот для приобретения рекламы
Для продолжения согласитесь с офертой:

https://telegra.ph/PUBLICHNAYA-OFERTA-07-25'''

old_start = '''🏠 Стартовое меню'''

bot_doesnot_work = '''Бот не работает'''

write_support = '''👩‍💻  Написать в поддержку: @support_contact'''

choose_cat = '🔎 Поиск каналов'

myself_cabinet = 'Личный кабинет'

cabinet_payment_data = '''Платежные данные'''

phys_person = '''Физ лицо инфо'''

self_employed = '''Самозанятый инфо'''

IPOOO = '''ИП инфо'''

my_ord_success = '''<b>✅ ОРД успешно зарегистрирован!</b>'''

my_ord_unsuccess = '''<b>❌ ОРД не зарегистрирован!</b>'''

send_card_number = '''Введите номер карты'''

my_posts = '<b>Мои посты</b>'

send_my_post = '''<b>Пришлите пост</b>'''

swap_keyboard_rules = '''Отправь мне список URL-кнопок одним сообщением в следующем формате:

Одна кнопка в новом рядке:

<code>Кнопка 1 - http://t.me/durov
Кнопка 2 - http://vk.com/id1</code>


Используй разделитель |, чтобы добавить до трех кнопок в один ряд.


<code>Кнопка 1 - http://t.me/durov | Кнопка 2 - http://t.me/telepost_blog
Кнопка 3 - http://t.me/telepost_blog | Кнопка 4 - http://vk.com
</code>
'''

error_parse_time = '''Ошибка парсинга времени!'''

EMPTY_LINK = '''Оставить ссылку'''

postpone_rule = '''Отправь время, чтобы опубликовать пост сегодня.

Или отправь сразу время и дату, чтобы запланировать на любой другой день.
Например: <code>12:00</code> или <code>1200 16.9</code>'''

async def placements_stat(week, month, future, all, bot):
	from collections import Counter
	ids = [i[1].channel_id for i in all]
	id_counts = Counter(ids)

	unique_count = len(id_counts)

	most_popular_id = id_counts.most_common(1)[0][0]
	most_popular_count = id_counts.most_common(1)[0][1]
	
	if len(all) > 0:
		chat = await bot.get_chat(most_popular_id)
		channel_text = f'''<i>В {unique_count} разных каналах</i>
		
<b>Самый популярный <a href='{chat.invite_link}'>{chat.title}</a> {most_popular_count} раз</b>'''
	else:
		channel_text = ''
	text = f'''<b>📊 Статистика рекламных размещений:

	За неделю:
	Количество: {len(week)}
	Стоимость: {sum([i[1].price for i in week])}
	
	За месяц:
	Количество: {len(month)}
	Стоимость: {sum([i[1].price for i in month])}

	Отложенно:
	Количество: {len(future)}
	Стоимость: {sum([i[1].price for i in future])}
	
	За все время:
	Количество: {len(all)}
	Стоимость: {sum([i[1].price for i in all])}


</b>{channel_text}'''
	return text

async def my_advert_post(bot, placements):
	text = f'''📆 Запланированные посты\n\n'''
	count = 0
	for i in placements:
		count+=1
		ad, wl = i
		chat = await bot.get_chat(wl.channel_id)
		t = f'''<b>{count}. {wl.human_date} | <a href='{chat.invite_link}'>{chat.title}</a> | {wl.price}₽</b>\n'''
		text += t
	return text

def basket(channels=None):
	if channels is None:
		channels = []
	text = '<b>🛒 Корзина</b>\n\n'
	# if len(channels) == 0:
	# 	text += '\n\nНет каналов'
	# else:
	# 	for channel in channels:
	# 		text += f'''\n\n<a href='{channel.link}'><b>{channel.title}</b></a>'''
	text += f'\n\nВсего {len(channels)} каналов'

	return text


change_links_start = '''Пришлите свой креатив'''

def setting_filters(data=None):
	text = '''Настройки фильтров'''

	if data:
		if data.get('err'):
			err = f'''{(data.get('err') - 1) * 20}-{data.get('err') * 20}'''
			text += f'''\n\nERR: {err}%'''
		if data.get('views'):
			views = f'''{data.get('views')[0]}-{data.get('views')[1]}'''
			text += f'''\n\nПросмотры: {views}'''
		if data.get('sub'):
			views = f'''{data.get('sub')[0]}-{data.get('sub')[1]}'''
			text += f'''\n\nПодписчики: {views}'''
	return text


send_link = '''Пришлите ссылку в формате https://t.me/_____'''

choose_channel = 'Найденные каналы:'

def find_channel_form(channel):
	cat = Category.get(id=channel.category)
	text = f'''<b>Канал <a href='{channel.link}'>{channel.title}</a></b>

<b>Стоимость:</b> {channel.base_price} ₽

<b>ERR:</b> {channel.err}%

<b>Количество просмотров:</b> {channel.views}
<b>Количество подписчиков:</b> {channel.subscribers}

<b>Тематика:</b> <code>{cat.name_ru}</code>'''

	return text

def basket_stat(subs, views, count, price):
	text = f'''<b>Общая статистика корзины</b>

	<b>Общая стоимость:</b> {price} ₽

	<b>Количество просмотров:</b> {views}
	<b>Количество подписчиков:</b> {subs}
	
	<b>Количество каналов:</b> {count}'''

	return text


card_message = '''<b>Карты для оплаты:</b>

<code>4300 0000 0000 0777</code>
<code>5000 0000 0000 0009</code>
<code>4000 0000 0000 0119</code>
<code>5000 0000 0000 0116</code>
<code>4000 0000 0000 0101</code>
<code>5000 0000 0000 0108</code>

<b>Срок везде: </b> <code>11/22</code>
<b>Код: </b> <code>111</code>
'''

def get_link_form(channel):
	text = f'''<b>Пришлите ссылку для канала <a href='{channel.link}'>{channel.title}</a></b>'''
	return text

