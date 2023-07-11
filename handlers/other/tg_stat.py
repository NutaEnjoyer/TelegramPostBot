# from data.config import TG_STAT_TOKEN as token
token = '2cf289bf172b9d1a1a96f660b6b9d58e'

import requests


def get_channel_info(channel_id):
	base_url = 'https://api.tgstat.ru/channels/get'
	params = dict()
	params['token'] = token
	params['channelId'] = channel_id

	r = requests.get(base_url, params=params)

	return r.json()

def get_channel_stat(channel_id):
	base_url = 'https://api.tgstat.ru/channels/stat'
	params = dict()
	params['token'] = token
	params['channelId'] = channel_id

	r = requests.get(base_url, params=params)

	return r.json()

def get_channel_subscriber(channel_id):
	base_url = 'https://api.tgstat.ru/channels/subscribers'
	params = dict()
	params['token'] = token
	params['channelId'] = channel_id

	r = requests.get(base_url, params=params)

	return r.json()

def get_channel_views(channel_id):
	base_url = 'https://api.tgstat.ru/channels/views'
	params = dict()
	params['token'] = token
	params['channelId'] = channel_id

	r = requests.get(base_url, params=params)

	return r.json()

def get_channel_avg_posts_reach(channel_id):
	base_url = 'https://api.tgstat.ru/channels/avg-posts-reach'
	params = dict()
	params['token'] = token
	params['channelId'] = channel_id

	r = requests.get(base_url, params=params)

	return r.json()

def get_channel_err(channel_id):
	base_url = 'https://api.tgstat.ru/channels/err'
	params = dict()
	params['token'] = token
	params['channelId'] = channel_id

	r = requests.get(base_url, params=params)

	return r.json()

def main(argv):
	parametr = 'https://t.me/lawproblemsru'
	resp = get_channel_err(parametr)
	print(resp)


if __name__ == '__main__':
	import sys
	main(sys.argv)
