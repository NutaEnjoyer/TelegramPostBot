# from bot_data.config import TG_STAT_TOKEN as token
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

	if r.json()['status'] != 'ok':
		return 0

	return r.json()['response'][0]['participants_count']

def get_channel_views(channel_id):
	base_url = 'https://api.tgstat.ru/channels/views'
	params = dict()
	params['token'] = token
	params['channelId'] = channel_id

	r = requests.get(base_url, params=params)
	if r.json()['status'] != 'ok':
		return 0
	return r.json()['response'][0]['views_count']

def get_channel_avg_posts_reach(channel_id):
	base_url = 'https://api.tgstat.ru/channels/avg-posts-reach'
	params = dict()
	params['token'] = token
	params['channelId'] = channel_id

	r = requests.get(base_url, params=params)
	if r.json()['status'] != 'ok':
		return 0
	return r.json()['response'][0]['avg_posts_reach']

def get_channel_err(channel_id):
	base_url = 'https://api.tgstat.ru/channels/err'
	params = dict()
	params['token'] = token
	params['channelId'] = channel_id

	r = requests.get(base_url, params=params)
	if r.json()['status'] != 'ok':
		return 0
	return r.json()['response'][0]['err']

def add_channel(channelName):
	base_url = 'https://api.tgstat.ru/channels/add'
	params = dict()
	params['token'] = token
	params['channelName'] = channelName

	r = requests.post(base_url, params=params)
	return r.json()

def get_post_views(channel_id, post_id):
	base_url = 'https://api.tgstat.ru/posts/get'
	params = dict()
	params['token'] = token
	params['postId'] = f"https://t.me/{str(channel_id)[4:]}/{post_id}"

	r = requests.get(base_url, params=params)
	js = r.json()
	if js['status'] == 'error':
		if js['error'] == 'post_not_found':
			params = dict()
			params['token'] = token
			params['postId'] = f"https://t.me/c/{str(channel_id)[4:]}/{post_id}"

			r = requests.get(base_url, params=params)

	try:
		js = r.json()
		return js["response"]["views"]
	except Exception as e:
		return 0


def main(argv):
	resp = get_post_views(-1001868668014, 146)
	print(resp)


if __name__ == '__main__':
	import sys
	main(sys.argv)
