from db.models import *
from handlers.other import tg_stat

def add_channel_to_find_channel_from_channel(id):
	# find_channel = FindChannel.create(channel_id=id, title=)
	pass

def update_tg_stat():
	channels = FindChannel.select()
	for c in channels:
		try:
			subscribers = tg_stat.get_channel_subscriber(c.channel_id)
			err = tg_stat.get_channel_err(c.channel_id)
			c.views = round(subscribers * err / 100)
			c.subscribers = subscribers
			c.err = err
			c.save()
		except Exception as e:
			print(e)

def readd_find_channel():
	pass


def main():
	update_tg_stat()


if __name__ == '__main__':
	main()

