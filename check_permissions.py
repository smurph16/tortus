from MoinMoin.web.contexts import ScriptContext
request = ScriptContext()
pagename = u'WaterGroup'

print request.user.may.read(pagename)