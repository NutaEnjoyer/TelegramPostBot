from aiogram import types

def admin():
	keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
	b1 = types.KeyboardButton('Рассылка')
	b2 = types.KeyboardButton('Блокировать канал')
	b3 = types.KeyboardButton('Меню')
	keyboard.add(b1, b2)
	keyboard.add(b3)
	return keyboard

def start_offer_access():
	keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
	b1 = types.KeyboardButton('Согласиться')
	b2 = types.KeyboardButton('Отказаться')
	keyboard.add(b1)
	keyboard.add(b2)
	return keyboard

def add_channel():
	keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
	b1 = types.KeyboardButton('Добавить канал')
	keyboard.add(b1)
	return keyboard

def set_schedule():
	keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
	b1 = types.KeyboardButton('Настройка расписания')
	keyboard.add(b1)
	return keyboard

def main_keyboard():
	keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
	b1 = types.KeyboardButton('Публикации')
	b2 = types.KeyboardButton('Настройки')
	b3 = types.KeyboardButton('Реклама и ВП')
	b4 = types.KeyboardButton('Кабинет')
	b5 = types.KeyboardButton('Настройка расписания')

	keyboard.add(b1, b2)
	keyboard.add(b3, b4)
	# keyboard.add(b5)

	return keyboard

def publications_keyboard():
	keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
	b1 = types.KeyboardButton('Создать пост')
	b2 = types.KeyboardButton('Контент план')
	# b3 = types.KeyboardButton('Редактировать пост')
	b4 = types.KeyboardButton('Меню')

	keyboard.add(b1)
	keyboard.add(b2, b4)
	# keyboard.add(b4)

	return keyboard

def cabinet_keyboard():
	keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
	b1 = types.KeyboardButton('Баланс лицевого счета')
	b2 = types.KeyboardButton('Статистика')
	b3 = types.KeyboardButton('Данные ОРД')
	b4 = types.KeyboardButton('Меню')

	keyboard.add(b1)
	keyboard.add(b2, b3)
	keyboard.add(b4)

	return keyboard

def send_post():
	keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
	b1 = types.KeyboardButton('Отмена')
	b2 = types.KeyboardButton('Дальше')
	keyboard.add(b1, b2)

	return keyboard

def only_cancel():
	keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
	b1 = types.KeyboardButton('Отмена')
	keyboard.add(b1)

	return keyboard

from aiogram import types
from handlers.admin import TEXTS

def basket_keyboard():
	keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

	b1 = types.KeyboardButton(text='🔎 Найти канал')
	b2 = types.KeyboardButton(text='ВЕСЬ ПРАЙС')
	b3 = types.KeyboardButton(text='⭐️ Избранное')
	b4 = types.KeyboardButton(text='👤 Личный кабинет')
	# b5 = types.KeyboardButton(text='🔗 Замена ссылок')
	b5 = types.KeyboardButton(text='🔗 Мои посты')
	b6 = types.KeyboardButton(text='👩‍💻 Написать нам')
	b7 = types.KeyboardButton(text='🛒 Корзина')
	b8 = types.KeyboardButton(text='Меню')

	keyboard.add(b1)
	# keyboard.add(b2)
	keyboard.add(b3, b4)
	# keyboard.add(b5, b6)
	keyboard.add(b5, b7)
	keyboard.add(b8)

	return keyboard

def choose_cat():
	keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

	b1 = types.KeyboardButton(text='📚 По тематике')
	b2 = types.KeyboardButton(text='🔖 По ключевому слову')
	b3 = types.KeyboardButton(text='⚙️ По фильтрам')
	b4 = types.KeyboardButton(text='🏠 В меню')

	keyboard.add(b1)
	keyboard.add(b3)
	keyboard.add(b2)
	keyboard.add(b4)

	return keyboard

def myself_cabinet():
	keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

	b1 = types.KeyboardButton(text='Статистика размещений')
	b2 = types.KeyboardButton(text='Мои платежные данные')
	b3 = types.KeyboardButton(text='Мои посты')
	b4 = types.KeyboardButton(text='🏠 В меню')

	keyboard.add(b1)
	keyboard.add(b2)
	keyboard.add(b3)
	keyboard.add(b4)

	return keyboard

def basket():
	keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

	b1 = types.KeyboardButton(text='Перейти к оформлению')
	b2 = types.KeyboardButton(text='Загрузить статистику выбранных каналов')
	b3 = types.KeyboardButton(text='Добавить еще каналы')
	b4 = types.KeyboardButton(text='🏠 В меню')

	keyboard.add(b1)
	keyboard.add(b2)
	keyboard.add(b3)
	keyboard.add(b4)

	return keyboard

def only_home():
	keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

	b4 = types.KeyboardButton(text='🏠 В меню')

	keyboard.add(b4)

	return keyboard

def empty_link():
	keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

	b = types.KeyboardButton(text=TEXTS.EMPTY_LINK)

	keyboard.add(b)

	return keyboard