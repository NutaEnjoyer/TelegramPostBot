from db.models import ChannelCode
from handlers.user import utils as user_utils


start = '''Добро пожаловать в бот для планирования публикаций и рекламы
Для продолжения согласитесь с офертой'''

old_start = '''Стартовое меню'''

access_start_offer = 'Успешно подтверждено!'

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

balance_my_wallet = '''Баланс: 0\n\n<i>Вывод доступен только после подтверждения заказчиком выполнения заказа, либо через 24 часа с момента публикации материала</i>'''

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

album_edit = '''Album'''

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
	return f'<b>Ссылка для рекламы:\n https://t.me/FocachaADSbot?start=a{link}</b>'
