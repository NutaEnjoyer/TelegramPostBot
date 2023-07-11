from .admin.main import register_admin_handlers
import filters

def register(dp):
	handlers = (
		register_admin_handlers,
	)
	for handler in handlers:
		handler(dp)

