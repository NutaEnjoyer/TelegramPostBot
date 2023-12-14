from peewee import *

database = SqliteDatabase('database.db')

class BaseModel(Model):
	id = PrimaryKeyField()

	class Meta:
		database = database


class User(BaseModel):
	user_id = IntegerField()
	type = CharField(null=True)
	card_number = CharField(null=True)
	INN = CharField(null=True)

class Admin(BaseModel):
	user_id = IntegerField()


class Channel(BaseModel):
	channel_id = IntegerField()
	admin_id = IntegerField()
	title = CharField()


class Moderator(BaseModel):
	admin_id = IntegerField()
	channel_id = IntegerField()
	title = CharField()
	name = CharField()


class Schedule(BaseModel):
	channel_id = IntegerField()
	posts_count = IntegerField(default=0)
	interval = IntegerField(null=True)
	week_interval = IntegerField(null=True)
	confirm = BooleanField(default=True)
	confirm_id = IntegerField(null=True)
	confirm_themes = CharField(null=True)


class Post(BaseModel):
	is_advert = BooleanField(default=False)
	owner_id = IntegerField(null=True)
	price = IntegerField(null=True)
	media = TextField(null=True)
	text = TextField(null=True)
	keyboard_id = IntegerField(null=True)
	reactions_id = CharField(null=True)
	delete_human = CharField(null=True)
	delete_time = IntegerField(null=True)


class PostInfo(BaseModel):
	post_id = IntegerField(null=True)
	with_notification = BooleanField(default=True)
	with_comment = BooleanField(default=True)
	with_auto_write = BooleanField(default=False)
	disable_web_preview = BooleanField(default=True)
	hidden_sequel_text = CharField(null=True)
	hidden_sequel_button_text = CharField(null=True)
	reply_message_id = IntegerField(null=True)
	SharePost = TextField(null=True)
	price = IntegerField(null=True)


class PostTime(BaseModel):
	user_id = IntegerField()
	channel_id = IntegerField()
	active = BooleanField(default=True)
	post_id = IntegerField()
	human_time = CharField()
	time = IntegerField()


class SendedPost(BaseModel):
	user_id = IntegerField()
	channel_id = IntegerField()
	message_id = IntegerField()
	post_id = IntegerField()
	human_time = CharField()
	time = IntegerField()


class Keyboard(BaseModel):
	type = CharField(default='inline')
	reactions_id = IntegerField(null=True)


class Button(BaseModel):
	keyboard_id = IntegerField()
	text = CharField()
	url = CharField(null=True)
	row = IntegerField()
	column = IntegerField()


class ReactionsKeyboard(BaseModel):
	channel_id = IntegerField()
	message_id = IntegerField(null=True)
	amount = IntegerField(null=True)


class Reaction(BaseModel):
	reaction_keyboard_id = IntegerField()
	text = CharField()
	value = IntegerField(default=0)

class UserReaction(BaseModel):
	user_id = IntegerField()
	reaction_id = IntegerField()

class ChannelConfiguration(BaseModel):
	channel_id = IntegerField()
	linked_chat_id = IntegerField(null=True)
	auto_write = CharField(null=True)
	auto_approve = BooleanField(default=False)
	collect_orders = BooleanField(default=False)
	water_mark = CharField(null=True)
	hour_line = IntegerField(default=3)
	preview = BooleanField(default=False)
	point = BooleanField(default=False)
	post_without_sound = BooleanField(default=False)
	reactions = CharField(null=True)


class NewJoin(BaseModel):
	channel_id = IntegerField()
	user_id = IntegerField()
	approve = BooleanField(default=False)


class FindChannel(BaseModel):
	channel_id = IntegerField()
	title = CharField()
	link = CharField()
	base_price = IntegerField(default=0)
	min_price = IntegerField(null=True)
	format = CharField(null=True)
	views = IntegerField()
	subscribers = IntegerField()
	err = IntegerField(null=True)
	contacts = CharField(null=True)
	category = IntegerField()  # 47 default
	active = BooleanField(default=False)

class Basket(BaseModel):
	user_id = IntegerField()
	find_channel_id = IntegerField()

class Saved(BaseModel):
	user_id = IntegerField()
	find_channel_id = IntegerField()


class TinkoffOrder(BaseModel):
	user_id = IntegerField()
	order_id = CharField()
	payment_id = CharField()
	active = BooleanField(default=True)

class Category(BaseModel):
	name_ru = CharField()
	name_en = CharField(null=True)

class MyPost(BaseModel):
	user_id = IntegerField()
	post_id = IntegerField()

class MyPostBot(BaseModel):
	user_id = IntegerField()
	post_id = IntegerField()

class Placement(BaseModel):
	user_id = IntegerField()
	channel_id = IntegerField()
	post_id = IntegerField()
	status = CharField(default='CREATE')  # CREATE MODERATION MODERATION_SUCCESS MODERATION_FAIL POSTED

class ChannelCode(BaseModel):
	channel_id = IntegerField()
	code = CharField()

class WaitList(BaseModel):
	channel_id = IntegerField()
	user_id = IntegerField()
	admin_id = IntegerField()
	dict_object_id = IntegerField()
	seconds = IntegerField()
	human_date = CharField()
	price = IntegerField(default=1)
	ORD = CharField(null=True)
	from_admin_bot = BooleanField(default=False)

class AccountOrd(BaseModel):
	user_id = IntegerField()
	ord_id = CharField()

class AdvertPost(BaseModel):
	post_time_id = IntegerField()
	wait_list_id = IntegerField()
	is_paid = BooleanField(default=False)
	invoice_message_id = IntegerField(null=True)
	active = BooleanField(default=True)

class Wallet(BaseModel):
	user_id = IntegerField()
	balance = IntegerField(default=0)

class AdPlacement(BaseModel):
	user_id = IntegerField()
	admin_id = IntegerField()
	time = IntegerField()
	price = IntegerField()

class DictObject(BaseModel):
	is_advert = BooleanField(default=False)
	owner_id = IntegerField(null=True)
	price = IntegerField(null=True)
	delete_human = CharField(null=True)
	delete_time = IntegerField(null=True)

class Dict(BaseModel):
	object_id = IntegerField()
	type = CharField()
	file_id = TextField(null=True)
	file_path = TextField(null=True)
	text = TextField(null=True)
	reply_markup = IntegerField(null=True)

class ChannelBlock(BaseModel):
	channel_id = IntegerField()

class DeferredVerification(BaseModel):
	admin_id = IntegerField()
	user_id = IntegerField()
	price = IntegerField()
	channel_id = IntegerField()
	post_id = IntegerField()
	start_time = IntegerField()
	finish_time = IntegerField()
	active = BooleanField(default=True)

def main(argv):
	database.drop_tables([DeferredVerification])
	database.create_tables([DeferredVerification])
	# database.create_tables([DictObject])

	pass


if __name__ == '__main__':
	import sys
	main(sys.argv)
