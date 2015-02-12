from MoinMoin.web.contexts import ScriptContext
from MoinMoin.search import searchPages
request = ScriptContext()
from MoinMoin.Page import Page
from MoinMoin import search
from MoinMoin.PageEditor import PageEditor
import pprint, collections

def getFromDict(dataDict, mapList):
	return reduce(lambda d, k: d[k], mapList, dataDict)

def setInDict(dataDict, mapList, value):
	if not dataDict:
		getFromDict(dataDict, mapList[:-1])[mapList[-1]] = value
	if getFromDict(dataDict, mapList[:-1]).has_key(mapList[-1]):
		return dataDict
	else:
		getFromDict(dataDict, mapList[:-1])[mapList[-1]] = value
	return dataDict


#Extra test of the needle
if request.user.may.read(pagename):
	

if not request.user.may.read(pagename):
	Page(request, pagename).

needle = "t:battabo332 or t:7GroupHomepage"
search_result = search.searchPages(request, needle)
levels = {}
pages = []
search_result.hits
graph = {}
index = graph
reverse_dict = {}
for title in search_result.hits:
	pages = title.page_name.split('/') #Add a conditional here...only want to exclude the first level if it is a user
	print pages
	if reverse_dict.has_key(pages[-1]):
		reverse_dict[pages[-1]].append(title.page_name)
	else:
		reverse_dict[pages[-1]] = [title.page_name]
	for i in xrange(0,len(pages)):
		data = setInDict(graph, pages[0:i+1], {})
	graph = data
print "reverse_dict"
print reverse_dict
pprint.pprint(graph)
name = 'battabo332'


class SectionPath(object):
    """Represents a path through the sections of a document tree."""

    def __init__(self, init_path):
        self.path = init_path

    def child(self):
        return SectionPath((1, self.path))
    child = property(child)

    def sibling(self):
        head, tail = self.path
        return SectionPath((head + 1, tail))
    sibling = property(sibling)

    def __str__(self):
        result = []
        path = self.path
        while path is not None:
            head, tail = path
            result.append(str(head))
            path = tail
        result.reverse()
        result.pop(1)
        return '.'.join(result)

start = SectionPath((1, None))

name = 'battabo332'
def print_toc(graph):
	text = ""
	open ('temp.txt', 'w').close()
	def recurse(sections, path, text, reverse_dict):
		for section in sections:
			# Unpack each tree node as (string, list) tuple.
			title, children = section, sections[section]
			print title
			#print reverse_dict[title]
			try:
				link = reverse_dict[title][0] 
				print link#Broken when there is two key values...returns the first one by default
				with open ('temp.txt', 'a') as page:
					text = '{}. [[{} | {}]]<<BR>>'.format(path, link.encode('utf-8'), title) 
					page.write(text)
				print '{}. [[{} | {} ]]<<BR>>'.format(path, link.encode('utf-8'), title)  
			except KeyError:
				pass
			# Print the current section number and its title.
			# Converting "path" to a string yields the section number.
			
			# Call this function recursively for each child, passing the
			# "child" property of the path.
			recurse(children, path.child, text, reverse_dict)
			# Advance the path to the next sibling.
			path = path.sibling
		# Call the recursive function, using the "start" path to begin
		# generating section numbers starting at "1".
	recurse(graph, start, "", reverse_dict)
	print text
        
    # Pass the recursive tree structure into the table of contents printer.
text = print_toc(graph)

def create_page(text, page_name):
	if Page(request, page_name).exists(): #should use isUnderlayPage/isDataPage
	    print "A page with the name {0} already exists".format(page_name)
	    #Do you want to continue
	    n_text = PageEditor(request, page_name).get_raw_body()
	    n_text += text
	    PageEditor(request, page_name).saveText(n_text, 0)
	    print "A page was created with the name {0}".format(page_name) #Is there already a table of contents there?
	else:    
		try: #Should be checking if permissions exist?
			PageEditor(request, page_name).saveText(text, 0)
			print "A page was created with the name {0}".format(page_name)
		except:
			pass
text = ""			
with open ('temp.txt', 'r') as page:
	text += page.read()
create_page(text, "whittamoo")


class Tortus(TortusScript):

	def __init__(self):

		self.parser = argparse.ArgumentParser()
		self.request = ScriptContext()
		# self.parser.add_argument(
		# 	"--page_name", 
		# 	help="the name of the page being created")
		self.parser.add_argument(
			"--quick-link", #?? 
			help="flag if all users should have this page as a quicklink", 
			action="store_true")
		# self.parser.add_argument(
		# 	"--group_names", 
		# 	help="the name of the groups to create a quicklink for", 
		# 	action="store", 
		# 	nargs="*")
		# self.parser.add_argument(
		# 	"--user_names", 
		# 	help="the name of the users to create a central page for", 
		# 	nargs="*")
		self.parser.add_argument(
			"--permissions", 
			help="specify the permissions for the page. ", 
			choices=['instructor_read_only', 'read_only', 'user_write_only', 'group_write_only']) #Not yet implemented
		self.parser.add_argument(
			"--url", 
			help="the url of the root directory you would like to push to users", action="store")
		self.parser.add_argument(
			"--project", 
			help="the project to push the page to") #Should be able to deduce from url
		self.args = self.parser.parse_args()
		self.opts = vars(self.parser.parse_args())
		self.page = TortusPage()

	def run(self):
		arghelper = ArgHelper(self.opts, self.parser)
		project, projects = arghelper.get_project()
		self.group_obj = TortusGroup(project.name)
		permissions = arghelper.get_permissions()
		if not self.args.url:
			print "You need to specify a url to create the file tree from"
			sys.exit()
		root_dir = self.process_url(self.args.url)
		pages = self.traverse_pages(root_dir)
		created = self.copy(pages, project)
