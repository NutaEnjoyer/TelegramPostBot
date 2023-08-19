from db.models import Category

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

send_card_number = '''Введите номер карты'''

my_posts = '<b>Мои посты</b>'

send_my_post = '''<b>Пришлите пост</b>'''


def placements_stat(placements):
	text = f'''<b>📊 Статистика размещений\n\n Всего размещений: {len(placements)}</b>'''
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

