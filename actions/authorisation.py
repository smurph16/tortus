from MoinMoin.web.contexts import ScriptContext
request = ScriptContext()
from MoinMoin import user
from MoinMoin.auth import MoinAuth

def login(name, password):
	auth = MoinAuth()
	uid = user.getUserId(request, name)
	user_obj = user.User(request, uid)
	auth.login(request, user_obj, username=name, password=password)

