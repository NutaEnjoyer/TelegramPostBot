from aiogram.dispatcher.filters.state import StatesGroup, State


class Poster(StatesGroup):
	sendChannel = State()
	sendClientName = State()
	sendPost = State()
	settingPost = State()

	sendPrice = State()
	sendKeyboard = State()
	sendText = State()
	sendMedia = State()
	sendLink = State()

	sendTime = State()

	sendCommentToManager = State()
