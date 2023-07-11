from aiogram.dispatcher.filters.state import StatesGroup, State


class SendSmallAnswer(StatesGroup):
	sendAnswerStartOfferAccess = State()
	