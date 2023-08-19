from environs import Env

env = Env()
env.read_env()

TOKEN = env.str('BOT_TOKEN')
ADMIN_TOKEN = env.str('ADMIN_TOKEN')
SEMI_BOT_TOKEN = env.str('SEMI_BOT_TOKEN')
TG_STAT_TOKEN = env.str('TG_STAT_TOKEN')
categories = env.list('CATEGORIES')
TRASH_CHANNEL_ID = -1001783245871
WEEKDAYS = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
MONTHS = [None, 'января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
		  'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']
