from aiogram import types

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
	keyboard.add(b5)

	return keyboard

def publications_keyboard():
	keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
	b1 = types.KeyboardButton('Создать пост')
	b2 = types.KeyboardButton('Контент план')
	b3 = types.KeyboardButton('Редактировать пост')
	b4 = types.KeyboardButton('Меню')

	keyboard.add(b1)
	keyboard.add(b2, b3)
	keyboard.add(b4)

	return keyboard

def cabinet_keyboard():
	keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
	b1 = types.KeyboardButton('Баланс лицевого счета')
	b2 = types.KeyboardButton('Статистика')
	b3 = types.KeyboardButton('Платежные данные')
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
