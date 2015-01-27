"""---------------------------------------------------------
Command - Create Page
------------------------------------------------------------

This command allows users to create groups from the command line"""

from tortus_command import TortusScript
from tortus_page import TortusPage
from MoinMoin.web.contexts import ScriptContext
from MoinMoin import user
from MoinMoin.Page import Page
from MoinMoin.PageEditor import PageEditor
from tortus_project import TortusProjectCollection, TortusGroup
from default import *
import argparse, os

class Tortus(TortusScript):

	def __init__(self):

		self.parser = argparse.ArgumentParser()
		self.request = ScriptContext()
		self.parser.add_argument("--page_name", help="the name of the page being created")
		self.parser.add_argument("-all", "--show_to_all", help="flag if all users should have this page as a quicklink", action="store_true")
		self.parser.add_argument("--group_names", help="the name of the groups to create a quicklink for", action="store", nargs="*")
		self.parser.add_argument("--user_names", help="the name of the users to create a central page for")
		self.parser.add_argument(dest="filenames", help="the names of the files to create pages from", nargs='*')
		self.parser.add_argument("--template", help="if a page should be created for each group with the project template....specify template?") #efault="homework_template"
		self.parser.add_argument("--permissions", help="specify the permissions for the page. ", choices=['instructor_read_only', 'read_only', 
		'user_write_only', 'group_write_only'])
		self.parser.add_argument("--url", help="the url of the page you would like to push to users")
		self.parser.add_argument("--project", help="the project to push ")
		self.parser.add_argument("--central_page", help="create a homepage for the user or group", action="store_true")
		# self.parser.add_argument("--")
		self.parser.add_argument("--path", help = "creates the page as a subpage. Subpage path is taken as space separated list", nargs="*")
		self.args = self.parser.parse_args()
		self.page = TortusPage()

	def central_page(self, project, page_name, file_path, homepage=0):
        # Checks for a template page and sets homepage_default_text
		members = []
		if self.args.user_names:
			members = [self.args.user_names, ]
		elif self.args.group_names:
			members = self.request.groups.get(self.args.group_names, [])
		elif self.args.show_to_all:
			uids = user.getUserList(self.request)
			members = [user.User(self.request, uid).name for uid in uids]
		if not members:
			print "No user selected!"
			return
	    # loop through members for creating homepages
		for name in members:
			uid = user.getUserId(self.request, name)
			account = user.User(self.request, uid)
			if homepage == 1:
				if self.args.template:
					self.page.get_file_path(template, template =1)
					text = Page(self.request, self.args.template).get_raw_body()
				else:
					text = '''#acl %(user_name)s:read,write,delete,revert Default'''  #This is off
        # Check for Group definition	
				self.write_homepage(account, project.name, text)
			else:
				page_name = self.get_page_path(account, project.name, page_name)
				self.add_page_for_user(account, page_name, file_path)


	def write_homepage(self, account, project_name, homepage_text):
	# writes the homepage
		homepage = "{0}/{1}".format(project_name, account.name)
		if account.exists() and not account.disabled and not Page(self.request, homepage).exists(): #account exists?
			userhomepage = PageEditor(self.request, homepage)
			try:
				userhomepage.saveText(homepage_text, 0)
				print "Central page created for %s." % account.name
			except userhomepage.Unchanged:
				print "You did not change the page content, not saved!"
			except userhomepage.NoAdmin:
				print "You don't have enough rights to create the %s page" % account.name
		else:
			print "Page for %s already exists or account is disabled or user does not exist." % account.name

	def add_page_for_user(self, account, name, file_path):
		if account.exists() and not account.disabled and not Page(self.request, name).exists():
			# try:
			self.page.add_from_file(file_path, self.args, name, 'user') #different here
			print "Central page created for %s." % account.name
			# except IOError
			# 	print "You did not changed the page content, not saved!"
		else:
			print "Page for %s already exists or account is disabled or user does not exist" % account.name

	def get_page_path(self, account, project_name, name):
		#This is where I would get some page path
		page_path = "{0}/{1}/{2}".format(project_name, account.name, name)
		return page_path

	def run(self):
		name = None
	    # One of create, modify or delete must be specified
		if not (self.args.filenames or self.args.template or self.args.url):
			self.parser.error ("Please specify a file, url or a template to create a page from")
			return
		if not (self.args.permissions):
			 default_permissions = raw_input("The permissions for this file will be set to read_only. Press Y to continue or any other key to halt program\n")
			 if default_permissions == 'Y':
			 	self.args.permissions = 'read_only'
			 else:
			 	print "Permissions can be set using the --permissions flag. See --help for more information"
			 	return
		#This is messy. Tidy it up
		if (self.args.filenames and self.args.template) or (self.args.filenames and self.args.url) or (self.args.url and self.args.template):
			self.parser.error("You can only specify a filename, a template or a url")
			return
		if not (self.args.filenames or self.args.page_name or self.args.url):
			name = raw_input("Please specify a page name: ")
		elif self.args.page_name:
			name = args.page_name
		#elif args.group_names:
			#check execution was completed
			#find group
			#retrieve members
			#call quicklinks
		if self.args.project:
			project_name = self.args.project
		else:
			default_project = raw_input("This page will belong to the project DefaultProject. Please Y to proceed or any other key to cancel: ")
			if not default_project == "Y":
				return
			project_name = "default"
		projects = TortusProjectCollection()
		if not (projects.project_exists(project_name) == 0): #Make the project if it doesn't exist
			mk_prj = raw_input("This project does not exist yet. If you would like to create it, please Y to proceed or any other key to cancel: ")
			if mk_prj == 'Y':
				project = projects.tortus_project(name =project_name, groups={}, args=self.args)
			else:
				return #Exit if project shouldn't be created
		#Get the project again/
		else:
			project = projects.tortus_project(name=project_name, groups={}, args=self.args) #This is a retrieval step...initialises it with existing data
		group_obj = TortusGroup(project.name)
		if self.args.template:
			template = self.args.template
			file_path = self.page.get_file_path(template, template=1)
			if self.args.central_page:
				self.central_page(project, name, file_path)
			else:
				self.page.add_from_file(file_path, self.args, name, 'user')		
		elif self.args.filenames:
			for fname in self.args.filenames:
				if name is None:
					name = os.path.splitext(fname)[0]
				file_path = self.page.get_file_path(fname, file=1)
				if self.args.central_page:
					self.central_page(project, name, file_path)
				else:
					self.page.add_from_file(file_path, self.args, name, 'user')
		#homepage option?
		elif self.args.url:
			self.page.process_url_page(self.args)

	# def get_page_path():


		
	#elif args.template
# HomePage Template
#parser.add_argument("--template", help="if a page should be created for each group with the project template....specify template?")
		

if __name__ == "__main__":
	command = Tortus()
	command.run()
