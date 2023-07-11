from aiogram.dispatcher.filters.state import StatesGroup, State


class SendSmallAnswer(StatesGroup):
	sendAnswerStartOfferAccess = State()

class AddNewChannel(StatesGroup):
	sendMessageFromChannel = State()

class SettingSchedule(StatesGroup):
	SettingSchedule = State()
	SetPostCount = State()
	SetOutputTime = State()
	SetOutputInterval = State()
	SetDayInterval = State()
	SetConfirm = State()

class CommonStates(StatesGroup):
	FreeState = State()

class Advert(StatesGroup):
	Main = State()

class Settings(StatesGroup):
	Main = State()
	sendMessageFromChannel = State()
	ChooseSettingChannel = State()
	SettingChannel = State()
	SendAutoWrite = State()
	SendReactions = State()

class CabinetPaymentData(StatesGroup):
	Main = State()

class BalanceMyWallet(StatesGroup):
	Main = State()
	ChooseChannel = State()

class ContentPlan(StatesGroup):
	ChooseChannel = State()
	Main = State()
	ResendPost = State()
	SetDeleteTime = State()
	SetPostTime = State()
	SetPrice = State()


class EditPost(StatesGroup):
	EditMedia = State()
	EditText = State()
	EditMarkup = State()

class CreatePost(StatesGroup):
	ChooseChannel = State()

class ChooseCategory(StatesGroup):
	Main = State()


class SelfPerson(StatesGroup):
	Main = State()
	SendCardNumber = State()
	SendORD = State()
	SendINN = State()


class AddPost(StatesGroup):
	Main = State()
	SendPost = State()
	SendTime = State()
	SwapKeyboard = State()

class RewritePost(StatesGroup):
	Main = State()
	EditMedia = State()
	EditText = State()
	EditMarkup = State()

class ChangeLinks(StatesGroup):
	SendPost = State()
	SendLink = State()