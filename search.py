from MoinMoin.web.contexts import ScriptContext
from MoinMoin.search import searchPages
request = ScriptContext()
from MoinMoin.Page import Page
from MoinMoin import search
from MoinMoin.PageEditor import PageEditor
from default import *
import pprint, collections
import re, os

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

def search_pages(needle):
#needle = "t:battabo332 or t:7GroupHomepage"
	search_result = search.searchPages(request, needle)
	#Choice here...should every page appear?
	if search_result.hits: #and request.user.may.read(pagename)
		graph = {}
		reverse_dict = {}
		for title in search_result.hits:
			print title.page_name
			pages = title.page_name.split('/') #Add a conditional here...only want to exclude the first level if it is a user
			if reverse_dict.has_key(pages[-1]):
				reverse_dict[pages[-1]].append(title.page_name)
			else:
				reverse_dict[pages[-1]] = [title.page_name]
			for i in xrange(0,len(pages)):
				data = setInDict(graph, pages[0:i+1], {})
			graph = data
		return graph, reverse_dict

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
        #result.pop()
        return '.'.join(result)

def print_toc(graph, reverse_dict):
	text = ""
	open ('temp.txt', 'w').close()
	def recurse(sections, path, text, reverse_dict):
		for section in sections:
			# Unpack each tree node as (string, list) tuple.
			title, children = section, sections[section]
			#print reverse_dict[title]
			try:
				link = reverse_dict[title][0] 
				#print link#Broken when there is two key values...returns the first one by default
				with open ('temp.txt', 'a') as page:
					text = '{}. [[{} | {}]]<<BR>>'.format(path, link.encode('utf-8'), title) 
					page.write(text)
				#print '{}. [[{} | {} ]]<<BR>>'.format(path, link.encode('utf-8'), title)  
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
	start = SectionPath((1, None))
	recurse(graph, start, "", reverse_dict)
	#print text
        
    # Pass the recursive tree structure into the table of contents printer.

def create_page(text, page_name):
	if Page(request, page_name).exists(): #should use isUnderlayPage/isDataPage
	    print "A page with the name {0} already exists".format(page_name)
	    #Do you want to continue
	    n_text = PageEditor(request, page_name).get_raw_body()
	    pattern = re.compile('(##Contents)[^----]*(----)', re.M)
	    match = re.search(pattern, n_text)
	    if match:
	    	print "match"
	    	n_text = re.sub(pattern, "\g<1><<BR>>\n{}<<BR>>\g<2>".format(text), n_text)
	    	print n_text
	    else:
	    	#permissions = Page(request, pagename).getACL(request)
	    	n_text = text + n_text #This will probably render the permissions a little weirdly
	    PageEditor(request, page_name).saveText(n_text, 0)
	    print "A page was created with the name {0}".format(page_name) #Is there already a table of contents there?
	else:    
		try: #Should be checking if permissions exist?
			text = "##Contents\n{}\n----".format(text)
			PageEditor(request, page_name).saveText(text, 0)
			print "A page was created with the name {0}".format(page_name)
		except:
			pass

def find_groups(matches):
		#Look through all the groups in the wiki...and check for pages with Group in them
		pattern = re.compile('.*\(2f\)(.*)Group')
		matched_groups = [group for group in matches if re.search(pattern, group)]
		moin_groups = request.groups
		group_dict = {}
		for group in matched_groups:
			moin_group = moin_groups.get(re.sub('\(2f\)', '/',group))
			if moin_group:
				user_name = re.search('.*\(2f\)(.*)Group', group).group(1)
				group_dict[user_name] = [member for member in moin_group]
		return group_dict 

##MADE A MESS OF THIS. THESE WERE TAKEN FROM CREATE FILE TREE, CREATE PAGE, REMOVE PROJECT
#SOMETHING IS OFF WITH CREATE PAGE 
def traverse_pages(project_name, remove=0):
    #Get all pages that 
    matches = []
    if remove == 1:
    	page_pattern = re.compile('.*{0}.*'.format(project_name))
    else:
    	page_pattern = re.compile('^{0}.*').format(project_name) #Be careful of this
    #Find all pages with this 
    for page in os.walk(os.path.join(data_folder, 'pages')).next()[1]:
        match = re.search(page_pattern,page) 
        if match:
            matches.append(match.group())
    return matches



