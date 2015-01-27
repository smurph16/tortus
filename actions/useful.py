from default import *
import re
from MoinMoin.Page import Page
from MoinMoin.web.contexts import ScriptContext
request = ScriptContext()

#add quick_link

#check if page exists

#check if there are already permissions on the page
def has_permissions(page_name):
	permissions = False
	pattern = re.compile('#acl ')
	text = Page(request, page_name).get_raw_body()
	search_obj = re.search(pattern, text)
	if search_obj is not None:
		permissions = True
	return permissions