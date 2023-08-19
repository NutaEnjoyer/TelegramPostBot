from aiogram import types

def main_keyboard():
	keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

	b1 = types.KeyboardButton(text='🔎 Найти канал')
	b2 = types.KeyboardButton(text='ВЕСЬ ПРАЙС')
	b3 = types.KeyboardButton(text='⭐️ Избранное')
	b4 = types.KeyboardButton(text='👤 Личный кабинет')
	b5 = types.KeyboardButton(text='🔗 Замена ссылок')
	b6 = types.KeyboardButton(text='👩‍💻 Написать нам')
	b7 = types.KeyboardButton(text='🛒 Корзина')

	keyboard.add(b1)
	# keyboard.add(b2)
	keyboard.add(b3, b4)
	keyboard.add(b5, b6)
	keyboard.add(b7)

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
