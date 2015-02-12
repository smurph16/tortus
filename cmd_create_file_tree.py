"""---------------------------------------------------------
Command - Create File Tree
------------------------------------------------------------

This command allows users to create file trees from the command line"""

from tortus_command import TortusScript
from tortus_page import TortusPage
from MoinMoin.web.contexts import ScriptContext
from MoinMoin import user
from MoinMoin.Page import Page
from MoinMoin.PageEditor import PageEditor
from tortus_project import TortusProjectCollection, TortusGroup
from default import *
from helper import ArgHelper
from urlparse import urlparse
import argparse, os, re, sys
from search import search_pages, print_toc, create_page, traverse_pages
#from search import 

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
		#self.update_contents(project)
		self.group_obj = TortusGroup(project.name)
		permissions = arghelper.get_permissions()
		if not self.args.url:
			print "You need to specify a url to create the file tree from"
			sys.exit()
		root_dir = self.process_url(self.args.url)
		pages = traverse_pages(root_dir)
		created = self.copy(pages, project)
		self.update_contents(project)

	def process_url(self, url, level=0):
		#Move this
		wiki_data = os.path.basename(os.path.dirname(data_folder))
		url_parts = urlparse(url)
		#Page name is a list of the respective pages in the url
		page_name = (url_parts[2].rpartition(wiki_data + '/')[2]).rsplit('/')
		file_string = '(2f)' # magic number
		file_name = file_string.join(page_name)
		moin_link = '/'.join(page_name)
		if not Page(self.request, moin_link).exists():
		    print "The url you have provided is not a page that has already been created"
		    sys.exit() #Could raise an error
		else:
		    return file_name

	def copy(self, matches, project):
    #You must know the name of the page at this point
		for page in matches:
			page_name = re.sub('\(2f\)', '/', page)
			text = Page(self.request, page_name).get_raw_body()
			user_copy = '##User copy'
			group_copy = '##Group copy'
			if text.find(user_copy) != -1:
				print "user"
				self.user_copy(project, page_name, text)
			elif text.find(group_copy) != -1:
			    self.group_copy(project, page_name, text)
			else:
				self.generic_copy(project, page_name)  

	def user_copy(self, project, page_name, text):
		"""Creates a copy of a page for each user in members
		@param members: a list of members a copy should be made for
		@param project: the project the page should be created for
		@param page_name: the name of the page to be copied
		@param file_path: the path to the page to be copied"""
		for name in project.get_members():
		    #uid = user.getUserId(self.request, name)
		    #account = user.User(self.request, uid)
		    successful = []
		    failed = []
		    p = get_permissions(user_name=name)
		    permissions = p.get('user_write_only')
		    page_text = permissions
		    #Page name
		    pg_name = self.page.get_page_path(name, project.name, page_name)
		    if Page(self.request, pg_name).exists(): #should use isUnderlayPage/isDataPage
		        print "A page with the name {0} already exists".format(pg_name)
		        failed.append(name)
		        continue #Need name here but doesn't give correct permissions. Could pass them in here?
		    else:
		        page_text += text #Should be checking if permissions exist?
		        PageEditor(self.request, pg_name).saveText(page_text, 0)
		        print "A page was created with the name {0}".format(pg_name)
		        successful.append(name)

	def group_copy(self, project, page_name, text):
	    """Creates a copy of a page for each group in accounts 
	    @param accounts: a list of groups a copy should be created for
	    @param project: the project the page should be created for
	    @param page_name: the name of the page to be copied
	    @param file_path: the path of the page to be copied"""
	    successful = []
	    failed = []
	    for group in project.groups:
	        pg_name = "{0}GroupHomepage/{1}".format(group, page_name)
	        p = get_permissions(group_name=self.group_obj.get_moin_name(group)) #These permissions for Moin are likely to be wrong
	        permissions = p.get('group_write_only')
	        page_text = permissions
	        if Page(self.request, pg_name).exists(): #should use isUnderlayPage/isDataPage
	            print "A page with the name {0} already exists".format(pg_name)
	            failed.append(group)
	        else: 
	        	try:   
		            page_text += text #Should be checking if permissions exist?
		            PageEditor(self.request, pg_name).saveText(page_text, 0)
		            print "A page was created with the name {0}".format(pg_name)
		            successful.append(group)
		        except:
		            pass

	def generic_copy(self, project, page_name):
		"""Displays the text on generic pages in an individuals path"""
		successful = []
		failed = []
		p = get_permissions()
		permissions = p.get('read_only')
		text = permissions
		text += "<<Include({0})>>".format(page_name)
		for name in project.get_members():
			pg_name = self.page.get_page_path(name, project.name, page_name)
			if Page(self.request, pg_name).exists(): #should use isUnderlayPage/isDataPage
				#print "A page with the name {0} already exists".format(pg_name)
				failed.append(name)
				 #Need name here but doesn't give correct permissions. Could pass them in here?  
			else:
				PageEditor(self.request, pg_name).saveText(text, 0)
				print "A page was created with the name {0}".format(pg_name)
				successful.append(name)
		#print successful
		#print failed
	#Current Problems
	# Effectively doesn't allow links to their own pages...? remove links from generic
	# 
		    
	def process_user_ids(self, page_name, args): #This might be the one to move...back
		"""Add a link in the users task-bar to a specific page
		@param page_name: the name of the page to add a quick link to
		@args: command line arguments"""
		user_ids = None
		if args.show_to_all:
			user_ids = getUserList(self.request)
		elif args.group_names:
			user_ids = retrieve_members(args.group_names) #Retrieve members is in groups
		if user_ids is not None:
			for uid in user_ids:
				add_quick_link(uid, page_name)

	def update_contents(self, project):
		for name in project.get_members():
			groups = ["t:{}GroupHomepage".format(group) for group in project.groups if name in project.groups[group]]
			group_needle = " or ".join(groups)
			needle = "t:{} or {}".format(name, group_needle)
			if search_pages(needle): #Try Except
				graph, reverse_dict = search_pages(needle)
				print_toc(graph, reverse_dict)
				with open ('temp.txt', 'r') as page:
					text = page.read()
					create_page(text, name)


if __name__ == "__main__":
	command = Tortus()
	command.run()

