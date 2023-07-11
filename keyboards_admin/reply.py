from aiogram import types

def main_keyboard():
	keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

	b1 = types.KeyboardButton(text='Выбрать по КАТЕГОРИИ')
	b2 = types.KeyboardButton(text='ВЕСЬ ПРАЙС')
	b3 = types.KeyboardButton(text='Избранное')
	b4 = types.KeyboardButton(text='Личный кабинет')
	b5 = types.KeyboardButton(text='Замена ссылок')
	b6 = types.KeyboardButton(text='Написать нам')
	b7 = types.KeyboardButton(text='Корзина')

	keyboard.add(b1)
	keyboard.add(b2)
	keyboard.add(b3, b4)
	keyboard.add(b5, b6)
	keyboard.add(b7)

	return keyboard
