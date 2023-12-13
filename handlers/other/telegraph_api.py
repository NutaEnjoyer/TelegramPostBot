from telegraph import Telegraph

short_name = 'FOCACHA'

telegraph = Telegraph()
telegraph.create_account(short_name=short_name)


def create_page(title, html_content=None):
	if not html_content:
		html_content = title

	response = telegraph.create_page(
		title,
		html_content=html_content
	)
	print(response)
	return response['url']
