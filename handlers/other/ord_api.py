import requests

from translate import Translator

url = 'https://api.ord-lab.ru/api/v1'
token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lcklkIjoiZGEzZmVjZjYtYzhmYi00Yzg4LWE4OTItODQyNDkwZjcyZWJlIiwiZXhwI' \
		'joyMDEwNDE4MzE5LCJpYXQiOjE2OTUwNTgzMTksImp0aSI6ImNmYTg3ZTVjLTcyMDctNGYxOC1hNjA4LTFlMjljYTliYWViYSJ9.XK_4Y9lAxW' \
		'_10vtOKH5XKN5KMWVi0a46oq9_n3EPKpI'

headers = {
	"Authorization": f"Bearer {token}"
}

def translate_text(text):
	translator = Translator(from_lang='ru', to_lang='en')
	translated = translator.translate(text)
	return translated

def snake_case_to_camel_case(text):
	words = text.split('_')
	camel_case = ''.join(word.title() for word in words)
	return camel_case

def get_exrnal_id(input_string):
	translated_text = translate_text(input_string)
	snake_case_text = translated_text.lower().replace(' ', '_')
	camel_case_result = snake_case_to_camel_case(snake_case_text)
	return camel_case_result

def register_organization(type, inn, name, platforms):
	"""types:
ip - Индивидуальный предприниматель;
fl - Физическое лицо;
ul - Юридическое лицо.
"""
	json = {
		"type": type,
		"isOrs": False,
		"isRr": True,
		"inn": inn,
		"name": name,
		"platforms": platforms
	}
	respononse = requests.post(url+'/organizations', headers=headers, json=json)
	return respononse.json()

def get_organization(id):
	response = requests.get(url+f'/organizations/{id}', headers=headers)
	return response.json()

def update_organization(id, inn=None, name=None, platforms=None):
	organization = get_organization(id)
	for k in organization.keys():
		if organization[k] == '': organization[k] = None
	if inn:
		organization['inn'] = inn
	if name:
		organization['name'] = name
	if platforms:
		organization['platforms'] = platforms

	response = requests.put(url+f'/organizations/{id}', headers=headers, json=organization)
	return response.json()

def create_platform_object(name, url):
	platform = {
		'externalId': get_exrnal_id(name),
		'type': 'is',
		'isOwned': False,
		'name': name,
		'url': url.strip(),
	}
	return platform

def create_standard_platform_object():
	platform = {
		'externalId': get_exrnal_id("Telegram"),
		'type': 'is',
		'isOwned': False,
		'name': "Telegram",
		'url': "https://telegram.org",
	}
	return platform

def add_platform(id, name, url):
	organization = get_organization(id)
	platform = create_platform_object(name, url)
	organization['platforms'].append(platform)
	response = update_organization(id, platforms=organization['platforms'])
	return response

def creative_one_data(type, data):
	if type == 'text':
		obj = {
			'description': '',
			'textData': data
		}
	elif type == 'photo':
		obj = {
			'description': '',
			'mediaUrl': data
		}
	elif type == 'video':
		obj = {
			'description': '',
			'mediaUrl': data
		}
	else:
		obj = {}
	
	return obj

def creative_data(listData):
	creativeData = []
	for exampleData in listData:
		creativeOneData = creative_one_data(type=exampleData['type'], data=exampleData['data'])
		creativeData.append(creativeOneData)

	return creativeData

def create_creative(contractId, form, advert_url, listData):
	"""advert_url - ссылки на сам пост
	
	forms: video Видеоролик	text-graphic-block	Текстово графический блок text-block Текстовый блок audio-rec Аудиозапись other Иное
"""
	if not isinstance(advert_url, list): advert_url = [advert_url]

	json = { 
		"contractId": contractId,
		"description": "Реклама в телеграм",
		"type": "cpm",
		"form": form,
		"url": advert_url,
		"isSocial": False,
		"creativeData": creative_data(listData)
	}
	
	response = requests.post(url+'/creatives', json=json, headers=headers)
	return response.json()

def create_contract(clientId, contractorId, amount, number, date=None):
	if not date:
		import datetime

		now = datetime.datetime.now(datetime.timezone.utc)

		date = now.strftime("%Y-%m-%d")
		print(date)
	json = {
		"type": "contract",
		"clientId": clientId,
		"contractorId": contractorId,
		"isRegReport": False,
		"actionType": "conclude",
		"subjectType": "distribution",
		"number": str(number),
		"date": date,
		"amount": amount,
		"isVat": False,
		"contractId": None
	}
	response = requests.post(url+'/contracts', json=json, headers=headers)
	return response.json()

def main():
	# platform1 = create_platform_object(name="Telegram Channel", url="https://t.me/naukogradnew")
	# platform2 = create_platform_object(name="Telegram Channel", url="https://t.me/marketing_outside_hogwarts")
	org1 = get_organization("a4ef71fa-95e7-4cf1-b12a-8e8e21c429b4")
	resp = update_organization(id="a4ef71fa-95e7-4cf1-b12a-8e8e21c429b4", platforms=[org1['platforms'][0]])
	# org2 = register_organization("fl", "381608053039", name="Жукова Лилия", platforms=[platform2])
	# listData = [
	# 	{
	# 		"type": "photo",
	# 		"data": "https://avatars.mds.yandex.net/get-images-cbir/2302938/vkRSZjrggI8hmbpWcfGnGw5424/ocr"
	# 	},
	# 	{
	# 		"type": "text",
	# 		"data": "Кто из этих людей был первым и последним президентом СССР?"
	# 	}
	# 	]
	print(resp)


	orgId1 = "a4e2dff9-5dfd-45d3-9ae2-9aa8539afd1c"
	orgId2 = "f9c11d60-5332-403d-87aa-da94e5f9870f"
	contractId = "3696f657-9a87-4a36-ab83-7974d566f8bf"
	creativeId = "d0819ac5-2719-41ff-8de5-e07d0dad0ae1"


if __name__ == '__main__':
	main()
