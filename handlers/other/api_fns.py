import requests

token = '0518dd11a17f76b7b3917dbf3cc08fa5309e92b6'

def search(q: str, page: int=1, filter: str='active'):
	base_url = 'https://api-fns.ru/api/search'
	params = dict()
	params['q'] = q
	params['page'] = page
	params['filter'] = filter
	params['key'] = token

	r = requests.get(base_url, params=params)

	return r.json()


def main(argv):
	parametr = 'Долгов Максим Сергеевич'
	resp = search(q=parametr)
	print(resp)


if __name__ == '__main__':
	import sys
	main(sys.argv)
