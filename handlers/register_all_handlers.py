
from .user.main import register_user_handlers
import filters

def register(dp):
	handlers = (
		register_user_handlers,
	)
	for handler in handlers:
		handler(dp)


