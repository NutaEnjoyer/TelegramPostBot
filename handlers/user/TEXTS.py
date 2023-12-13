from db.models import ChannelCode
from handlers.user import utils as user_utils

from bot_data import config

from db.models import * 

postpone_rule = '''Отправь время, чтобы опубликовать пост сегодня.'''

my_ord_success = '''<b>✅ ОРД успешно зарегистрирован!</b>'''

my_ord_unsuccess = '''<b>❌ ОРД не зарегистрирован!</b>'''

choose_cat = '🔎 Поиск каналов'

choose_channel = 'Найденные каналы:'

EMPTY_LINK = '''Оставить ссылку'''

my_posts = '<b>Мои посты</b>'
send_my_post = '''<b>Пришлите пост</b>'''

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

def get_link_form(channel):
	text = f'''<b>Пришлите ссылку для канала <a href='{channel.link}'>{channel.title}</a></b>'''
	return text


def basket_stat(subs, views, count, price):
	text = f'''<b>Общая статистика корзины</b>

	<b>Общая стоимость:</b> {price} ₽

	<b>Количество просмотров:</b> {views}
	<b>Количество подписчиков:</b> {subs}
	
	<b>Количество каналов:</b> {count}'''

	return text



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

async def placements_stat_basket(week, month, future, all, bot):
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

def find_channel_form(channel):
	cat = Category.get(id=channel.category)
	text = f'''<b>Канал <a href='{channel.link}'>{channel.title}</a></b>

<b>Стоимость:</b> {channel.base_price} ₽

<b>ERR:</b> {channel.err}%

<b>Количество просмотров:</b> {channel.views}
<b>Количество подписчиков:</b> {channel.subscribers}

<b>Тематика:</b> <code>{cat.name_ru}</code>'''

	return text

start = '''Добро пожаловать в бот для планирования публикаций и рекламы
Для продолжения согласитесь с офертой'''

old_start = '''Стартовое меню'''

adv_start = '''🏠 Рекламное меню'''

access_start_offer = 'Успешно подтверждено!'

ord_rules_message = 'Для работы с ботом необходимо зарегистрироваться в ОРД'

ord_choose_type = 'Выберите тип организации'

bot_doesnot_work = '''Бот не работает'''

instruct_to_add_channel = '''В этом разделе вы можете добавить свой первый канал. Для этого назначьте бота администратором в вашем канале выдав следующие права (картинка)
Затем перешлите любое сообщение из ленты и сможете продолжить настройку  '''

bot_is_not_admin = '''Бот не является админом канала'''

the_channel_already_added = '''Данный канал уже добавлен!'''

the_channel_success_added = '''Канал успешно добавлен!'''

setting_schedule = 'Настройка расписания'

set_output_time = '''Укажите количество
рекламных постов в день
(отправьте цифру 1,2,3 и тд)'''

set_output_interval = 'Установите минимальный интервал выхода публикаций'

set_day_interval = 'Установите персональные интервалы по дням недели (если требуется)'

set_confirm = '''При выборе автоматического подтверждения выхода рекламной публикации рекламные посты будут автоматически добавляться после модерации нашим агентством.
ВАЖНО!!! Мы не рекламируем казино, скам, ставки, алкоголь, наркотики, даркнет и не берем кликбейтные или жестокие посты других каналов. Вы также можете указать интересующие тематики кнопкой "выбрать все" или убрав/поставив зеленую галочку нажав на интересующей тематике просто нажав на нее.  '''

error = 'Ошибка!'

publications_menu = '''Публикации'''

settings_menu = '''Настройки'''

advert_menu = '''Реклама и ВП'''

cabinet_menu = '''Кабинет'''

cabinet_payment_data = '''Платежные данные'''

balance_my_wallet = '''<b>Баланс: {balance}</b>\n\n<i>Вывод доступен только после подтверждения заказчиком выполнения заказа, либо через 24 часа с момента публикации материала</i>'''

content_plan = '''Контент план'''

choose_channel = '''Выберите канал'''

set_post_output_time = '''Время выхода {post} поста
Формат 09:15 или 0915'''

choose_category = '''Выберите категории'''

phys_person = '''Физ лицо инфо'''

self_employed = '''Самозанятый инфо'''

IPOOO = '''ИП инфо'''

send_card_number = '''Введите номер карты'''

send_post = '''Ты выбрал канал
<b>{title}</b>.

Отправь боту то, что собираешься опубликовать.'''

no_one_send_post = '''Нет сообщений для публикации.'''

message_will_be_post = '''1 сообщение будет опубликовано в <b>{title}</b>'''

message_will_be_post_question = '''Хочешь опубликовать пост прямо сейчас или отложить на будущее?'''

error_post_message_to_channel = '''Не удалось опубликовать пост в канале <b>{title}</b>'''

message_posted_success = '''Сообщение успешно опубликовано в канале <b>{title}</b>'''

album_edit = '''⚙️  Настройка сообщения ✏️'''

postpone_rule = '''Отправь время, чтобы опубликовать пост сегодня.

Или отправь сразу время и дату, чтобы запланировать на любой другой день.
Например: <code>12:00</code> или <code>1200 16.9</code>'''

delete_time_rule = '''Отправь время, чтобы удалить пост сегодня.

Или отправь сразу время и дату, чтобы запланировать на любой другой день.
Например: <code>12:00</code> или <code>1200 16.9</code>'''

error_parse_time = '''Ошибка парсинга времени!'''

success_post_time = '''✅ Отложенный пост в канал <b>{title}</b> создан и будет опубликован

{date} GMT+3 Europe/Moscow'''

swap_keyboard_rules = '''Отправь мне список URL-кнопок и/или рекций одним сообщением в следующем формате:

Одна кнопка в новом рядке:

<code>Кнопка 1 - http://t.me/durov
Кнопка 2 - http://vk.com/id1</code>


Используй разделитель |, чтобы добавить до трех кнопок в один ряд.


<code>Кнопка 1 - http://t.me/durov | Кнопка 2 - http://t.me/telepost_blog
Кнопка 3 - http://t.me/telepost_blog | Кнопка 4 - http://vk.com
👍 / 👎</code>


Реакции не могут идти в одном рядке с урл-кнопками и должны быть на последней строке'''

swap_edit_rules = '<b>Пришлите новое медиа</b>'

error_parse_keyboard = '''Ошибка парсинга клавиатуры'''

referal_message = '''Ваша реферальная ссылка: https://t.me/FocachaADSbot?start={user_id}'''

channel_setting = '''Настройки канала'''

public = 'Public'

auto_wtire_rules = '''Rules

Нынешнее значение:
{now_value}'''

choose_time_zone = '''Выберите time zone'''

reactions_rule = '''Установка стандартных реакций:

<code>👍 / 👎</code>'''

application_manage = '''Application manage'''

open_post_text = '''<code>↑ Пост находится над этим сообщением ↑</code>
Статус: <b>{status}</b>
Тип поста: <b>{post_type}</b>
Автор: <b>{author}</b>'''

set_price_rule = '''Введите стоимость поста'''

edit_post = '''Изменение поста'''

edit_media = '''Пришлите новое(ые) медиа'''
edit_text = '''Введите новый текст поста'''
edit_markup = '''Клавиатура'''

rewrite_post_main = '''Редактирование поста меню'''

change_links_start = '''Пришлите свой креатив'''

send_link = '''Пришлите ссылку в формате https://t.me/_____'''

def ads_link(channel_id):
	link = ChannelCode.get_or_none(channel_id=channel_id)
	if link:
		return link.code
	code = user_utils.create_code_channel()
	link = ChannelCode.create(channel_id=channel_id, code=code)
	link.save()
	return code

def ads_link_text(channel_id):
	link = ads_link(channel_id)
	return f'<b>Ссылка для рекламы:\n {config.BUY_BOT_URL}?start=a{link}</b>'

def register_organization(data, user_id, org_id):
	text = f'''<b>Новая организация

	Название: {data['name']}
	Тип: {data['type']}
	ИНН: {data['inn']}
	ID Пользователя: {user_id}
	ID Организации в ОРД: {org_id}

	Платформа:
	Название: {data['title']}
	URL: {data['url']}
	</b>'''

	return text 

def register_client_organization(data, user_id, org_id):
	text = f'''<b>Новая организация

	Название: {data['name']}
	Тип: {data['type']}
	ИНН: {data['inn']}
	ID Пользователя: {user_id}
	ID Организации в ОРД: {org_id}
	
	</b>'''

	return text 

def new_platform(user_id, name, url):
	text = f'''<b>Новая Платформа

	ID Пользователя: {user_id}

	Платформа:
	Название: {name}
	URL: {url}
	</b>'''

	return text 

def new_contract(user_id, admin_id, price, contract_id, number):
	text = f'''<b>Новый контракт

	ID Клиента: {user_id}
	ID Контрагента: {admin_id}

	Сумма: {price}
	Номер контракта: {number}

	ID Контракта: {contract_id}
	</b>'''

	return text 

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

def my_ord_form(data):
	text = f'''<b>Информация о вашей организациии

	Название: {data['name']}
	Тип: {get_full_name(data['type'])}
	ИНН: {data['inn']}
	ID Организации в ОРД: {data['id']}

	</b>'''

	return text 

def stats(week, month, all):
	text = f'''<b>📊 Статистика рекламных размещений:

	За неделю:
	Количество: {len(week)}
	Стоимость: {sum([i.price for i in week])}
	
	За месяц:
	Количество: {len(month)}
	Стоимость: {sum([i.price for i in month])}
	
	За все время:
	Количество: {len(all)}
	Стоимость: {sum([i.price for i in all])}

</b>'''
	
	return text

def placements_stat(week, month, future, all):
	text = f'''<b>📊 Статистика рекламных размещений:

	За неделю:
	Количество: {len(week)}
	Стоимость: {sum([i for i in week])}
	
	За месяц:
	Количество: {len(month)}
	Стоимость: {sum([i for i in month])}

	Отложенно:
	Количество: {len(future)}
	Стоимость: {sum([i for i in future])}
	
	За все время:
	Количество: {len(all)}
	Стоимость: {sum([i for i in all])}

</b>'''
	return text
