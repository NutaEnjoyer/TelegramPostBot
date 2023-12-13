from environs import Env

env = Env()
env.read_env()

ADS_BOT_TOKEN = env.str('ADS_BOT_TOKEN')
ADS_BOT_TOKEN_DEBUG = env.str('ADS_BOT_TOKEN_DEBUG')
BUY_BOT_TOKEN = env.str('BUY_BOT_TOKEN')
BUY_BOT_TOKEN_DEBUG = env.str('BUY_BOT_TOKEN_DEBUG')
TG_STAT_TOKEN = env.str('TG_STAT_TOKEN')
categories = env.list('CATEGORIES')
TRASH_CHANNEL_ID = int(env.str('TRASH_CHANNEL_ID'))
CONTENT_ID = int(env.str('CONTENT_ID'))
ORD_LOGGING = int(env.str('ORD_LOGGING'))

ADS_BOT_URL = env.str('ADS_BOT_URL')
ADS_BOT_URL_DEBUG = env.str('ADS_BOT_URL_DEBUG')
BUY_BOT_URL = env.str('BUY_BOT_URL')
BUY_BOT_URL_DEBUG = env.str('BUY_BOT_URL_DEBUG')

MODERATION_CHANNEL_ID = int(env.str('MODERATION_CHANNEL_ID'))

WEEKDAYS = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
MONTHS = [None, 'января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
		  'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']


DEBUG = int(env.str('DEBUG'))

YOOKASSA_TOKEN = env.str('YOOKASSA_TOKEN')
YOOKASSA_TOKEN_DEBUG = env.str('YOOKASSA_TOKEN_DEBUG')

if DEBUG:
    YOOKASSA_TOKEN = YOOKASSA_TOKEN_DEBUG
    ADS_BOT_URL = ADS_BOT_URL_DEBUG
    BUY_BOT_URL = BUY_BOT_URL_DEBUG
    