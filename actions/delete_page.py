from MoinMoin.web.contexts import ScriptContext
from MoinMoin.PageEditor import PageEditor
request = ScriptContext()
pagename = u'TestPage'
print PageEditor(request, pagename).deletePage()