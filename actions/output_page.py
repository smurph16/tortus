from MoinMoin.Page import Page
from MoinMoin.web.contexts import ScriptContext
request = ScriptContext()
pagename = u'WhatUpDict' #The name of the page you want to print to the console...stored in /moin/eduwiki/data/pages
text = Page(request, pagename).get_raw_body()
print text