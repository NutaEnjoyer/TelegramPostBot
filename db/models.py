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
	user_id = IntegerField()
	channel_id = IntegerField()


class Schedule(BaseModel):
	channel_id = IntegerField()
	posts_count = IntegerField(default=0)
	interval = IntegerField(null=True)
	week_interval = IntegerField(null=True)
	confirm = BooleanField(default=True)
	confirm_themes = CharField(null=True)


class Post(BaseModel):
	owner_id = IntegerField(null=True)
	price = IntegerField(null=True)
	media = TextField(null=True)
	text = TextField(null=True)
	keyboard_id = IntegerField(null=True)
	reactions_id = CharField(null=True)
	delete_human = CharField(null=True)
	delete_time = IntegerField(null=True)


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

def main(argv):
	# print(argv)
	# database.drop_tables([User, Channel, Schedule])
	# database.create_tables([User, Channel, Schedule])
	# database.create_tables([PostTime])
	#
	# database.drop_tables([Post, PostTime, Keyboard, Button])
	# database.create_tables([Post, PostTime, Keyboard, Button])

	# # database.drop_tables([Channel])
	# database.drop_tables([SendedPost, Post, PostTime])
	# database.create_tables([SendedPost, Post, PostTime])
	# # database.drop_tables([Post])
	# database.create_tables([Post])
	database.drop_tables([Admin])
	database.create_tables([Admin])

	pass
if __name__ == '__main__':
	import sys
	main(sys.argv)
