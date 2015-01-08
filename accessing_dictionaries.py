from MoinMoin.Page import Page
from MoinMoin.web.contexts import ScriptContext
request = ScriptContext()

pagename = u"WhatUpDict"
d = request.dicts.get(pagename, {})
print d
print d.items()
print d['Alas']