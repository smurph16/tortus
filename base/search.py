from MoinMoin.web.contexts import ScriptContext
request = ScriptContext()
from MoinMoin.Page import Page
from MoinMoin import search
from MoinMoin.PageEditor import PageEditor
from default import *
import pprint, collections
import re, os, sys

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
	print needle
	search_result = search.searchPages(request, needle)
	if search_result.hits:
		graph = {}
		reverse_dict = {}
		for title in search_result.hits:
			pages = title.page_name.split('/')
			for page in pages:
				if 'Group' in page:
					pages.remove(page)
			print pages
			if not 'Project' in pages[0]:
				del pages[0]
			if not pages:
				continue
			if reverse_dict.has_key(pages[-1]):
				reverse_dict[pages[-1]].append(title.page_name)
			else:
				reverse_dict[pages[-1]] = [title.page_name]
			for i in xrange(0,len(pages)):
				data = setInDict(graph, pages[0:i+1], {})
			graph = data
		print graph
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
				if len(reverse_dict[title]) == 1:
					link = reverse_dict[title][0]
				else:
					link = reverse_dict[title][1]
				#print link# Broken when there is two key values...returns the first one by default
				with open ('temp.txt', 'a') as page:
					text = '{}. [[{} | {}]]<<BR>>'.format(path, link.encode('utf-8'), title) 
					page.write(text)
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

def create_page(text, page_name):
	if Page(request, page_name).exists():
	    n_text = PageEditor(request, page_name).get_raw_body()
	    pattern = re.compile('(##Contents)[^----]*(----)', re.M)
	    match = re.search(pattern, n_text)
	    if match:
	    	n_text = re.sub(pattern, "\g<1><<BR>>\n{}<<BR>>\g<2>".format(text), n_text)
	    else:
	    	#permissions = Page(request, pagename).getACL(request)
	    	n_text = text + n_text #This will probably render the permissions a little weirdly
	    try:
	    	PageEditor(request, page_name).saveText(n_text, 0)
	    except PageEditor.Unchanged:
	    	sys.exit()
	    print "A page was updated with the name {0}".format(page_name)
	else:    
		try:
			text = "##Contents\n{}\n----".format(text)
			PageEditor(request, page_name).saveText(text, 0)
			print "A page was created with the name {0}".format(page_name)
		except:
			pass
##Page.Unchanged	

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

def traverse_pages(project_name, remove=0):
    #Get all pages that 
    matches = []
    if remove == 1:
    	page_pattern = re.compile('.*{0}.*'.format(project_name))
    	for page in os.walk(os.path.join(data_folder, 'pages')).next()[1]:
			match = re.search(page_pattern,page)
			if match:
				matches.append(match.group())
    else:
		page_pattern = re.compile('^{0}.*'.format(project_name)) #Improve this
		for page in os.walk(os.path.join(data_folder, 'pages')).next()[1]:
			match = re.search(page_pattern,page)
			if match:
				if not "Group" in match.group():
					matches.append(match.group())     
    return matches



