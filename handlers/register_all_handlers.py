
from .user.main import register_user_handlers
from .user.second import register_second_handlers

import filters

def register(dp):
	handlers = (
		register_second_handlers,
		register_user_handlers,
	)
	for handler in handlers:
		handler(dp)


