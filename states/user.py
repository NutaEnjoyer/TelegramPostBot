from aiogram.dispatcher.filters.state import StatesGroup, State


class SendSmallAnswer(StatesGroup):
	sendAnswerStartOfferAccess = State()

class AddNewChannel(StatesGroup):
	sendMessageFromChannel = State()

class SettingSchedule(StatesGroup):
	StartSettingSchedule = State()
	ADSLink = State()
	SettingSchedule = State()
	SetPostCount = State()
	SetOutputTime = State()
	SetOutputInterval = State()
	SetDayInterval = State()
	SetConfirm = State()
	Public = State()
	Order = State()

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
	Public = State()

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
	SendHiddenSequel = State()
	SendPostToReply = State()
	SwapKeyboard = State()
	SwapMedia = State()
	SendPrice = State()
	SendDeleteTime = State()

class RewritePost(StatesGroup):
	Main = State()
	EditMedia = State()
	EditText = State()
	EditMarkup = State()

class ChangeLinks(StatesGroup):
	SendPost = State()
	SendLink = State()

class Find(StatesGroup):
	SendKeyword = State()


class SendKeyword(StatesGroup):
	ChooseChannel = State()

class Formation(StatesGroup):
	SendPost = State()
	PreSendPost = State()
	ChooseMyPost = State()

class Payments(StatesGroup):
	SendINN = State()

class SettingFilters(StatesGroup):
	Main = State()
	SetERR = State()
	SetView = State()
	SetSub = State()

class SendLink(StatesGroup):
	SendLink = State()

class CabinetStats(StatesGroup):
	Main = State()

class AddMyPost(StatesGroup):
	SendPost = State()

class SendEditPost(StatesGroup):
	EditText = State()

class EditModerationPost(StatesGroup):
	Main = State()
	SendText = State()
	SendMedia = State()
	SendKeyboard = State()
	SendTime = State()
	SendPrice = State()

class AddOrd(StatesGroup):
	ChooseType = State()
	SendInn = State()
	SendName = State()


class ModerationManage(StatesGroup):
	Main = State()
	ChooseCat = State()
	SendRedactor = State()
	OpenRedactor = State()
	ChooseConfirmer = State()

class ManagerManage(StatesGroup):
	Main = State()
	ChooseCat = State()
	SendRedactor = State()
	SendRequisites = State()
	OpenRedactor = State()
	ChooseConfirmer = State()

	EditRate = State()
	EditRequisites = State()

class WlNewTime(StatesGroup):
	SendTime = State()
	

class Admin(StatesGroup):
	SendMail = State()
	SendBlock = State()

class CheckUser(StatesGroup):
	SendMessage = State()

class Schedule(StatesGroup):
	ChooseChannel = State()
	Main = State()
	SendSchedule = State()
