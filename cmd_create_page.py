"""---------------------------------------------------------
Command - Create Page
------------------------------------------------------------

This command allows users to create pages from the command line"""

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
		self.parser.add_argument("--show_to_all", help="flag if all users should have this page as a quicklink", action="store_true")
		self.parser.add_argument("--group_names", help="the name of the groups to create a quicklink for", action="store", nargs="*")
		self.parser.add_argument("--user_names", help="the name of the users to create a central page for", nargs="*")
		self.parser.add_argument(dest="filenames", help="the names of the files to create pages from", nargs='*')
		self.parser.add_argument("--template", help="if a page should be created for each group with the project template....specify template?") #efault="homework_template"
		self.parser.add_argument("--permissions", help="specify the permissions for the page. ", choices=['instructor_read_only', 'read_only', 
		'user_write_only', 'group_write_only'])
		self.parser.add_argument("--url", help="the url of the page you would like to push to users")
		self.parser.add_argument("--project", help="the project to push the page to")
		self.parser.add_argument("--central_page", help="flag to create a page for each user or group", action="store_true")
		self.parser.add_argument("--path", help = "creates the page as a subpage. Subpage path is taken as space separated list", nargs="*")
		self.args = self.parser.parse_args()
		self.page = TortusPage()

	def central_page(self, project, page_name, file_path, homepage=0):
        # Checks for a template page and sets homepage_default_text
		"""Creates a page from a central page for each user or group
		@param project: the project the page and users belong to
		@param page_name: the name of the page that will be added for each user
		@param file_path: the path to the file or template containing the contents of the page
		@param homepage: set to 1 if the page will be the homepage for a user"""
		accounts = []
		if self.args.user_names:
			accounts = self.args.user_names
			self.user_copy(accounts, project, page_name, file_path, homepage)
		elif self.args.show_to_all:
			uids = user.getUserList(self.request)
			accounts = [user.User(self.request, uid).name for uid in uids]
			self.user_copy(accounts, project, page_name, file_path, homepage)
		elif self.args.group_names:
			for group in self.args.group_names:
				group_name = "{0}Project/{1}Group".format(project.name, group)
				temp_group = self.request.groups.get(group_name, [])
				if temp_group.member_groups:
					accounts.extend(temp_group.member_groups)
				if temp_group.members:
					accounts.append(temp_group)
			self.group_copy(accounts, project, page_name, file_path)
		if not accounts:
			print "No accounts selected for copy of page!"
			return
	    # loop through members for creating homepages
	
	def user_copy(self, members, project, page_name, file_path, homepage=0):
		"""Creates a copy of a page for each user in members
		@param members: a list of members a copy should be made for
		@param project: the project the page should be created for
		@param page_name: the name of the page to be copied
		@param file_path: the path to the page to be copied"""
		print members
		for name in members:
			uid = user.getUserId(self.request, name)
			account = user.User(self.request, uid)
			if homepage == 1:
				if self.args.template:
					self.page.get_file_path(template, template =1)
					text = Page(self.request, self.args.template).get_raw_body()
				else:
					text = '''#acl %(user_name)s:read,write,delete,revert Default'''  #This is off
				self.page.write_homepage(account, project.name, text)
			else:
				p = get_permissions(user_name=account.name)
				permissions = p.get('user_write_only')
				pg_name = self.page.get_page_path(account.name, project.name, page_name)
				self.page.add_from_file(file_path, project, pg_name, 'user', permissions)

	def group_copy(self, accounts, project, page_name, file_path):
		"""Creates a copy of a page for each group in accounts 
		@param accounts: a list of groups a copy should be created for
		@param project: the project the page should be created for
		@param page_name: the name of the page to be copied
		@param file_path: the path of the page to be copied"""
		for group in accounts:
			group_name = group.name.split('/')[1]
			pg_name = "{0}HomePage/{1}".format(group_name, page_name)
			p = get_permissions(group_name=group.name)
			permissions = p.get('group_write_only')
			self.page.add_from_file(file_path, project, pg_name, 'user', permissions)

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

	def run(self):
		name = None
		if not (self.args.filenames or self.args.template or self.args.url):
			self.parser.error ("Please specify a file, url or a template to create a page from")
			return
		if not (self.args.permissions):
			 default_permissions = raw_input("The permissions for this file will be set to default values. Press Y to continue or any other key to halt program\n")
			 if default_permissions == 'Y':
			 	p = get_permissions()
			 	permissions = p.get('read_only')
			 else:
			 	print "Permissions can be set using the --permissions flag. See --help for more information"
			 	return
		else:
			permissions = self.args.permissions
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
				return
		else:
			project = projects.tortus_project(name=project_name, groups={}, args=self.args) #This is a retrieval step...initialises it with existing data
		group_obj = TortusGroup(project.name)
		if self.args.template:
			template = self.args.template
			file_path = self.page.get_file_path(template, template=1)
			if self.args.central_page:
				self.central_page(project, name, file_path)
			else:
				self.page.add_from_file(file_path, project, name, 'user', permissions)		
		elif self.args.filenames:
			for fname in self.args.filenames:
				if name is None:
					name = os.path.splitext(fname)[0]
				file_path = self.page.get_file_path(fname, file=1)
				if self.args.central_page:
					self.central_page(project, name, file_path)
				else:
					self.page.add_from_file(file_path, project, name, 'user', permissions)
		elif self.args.url:
			self.page.process_url_page(self.args)	

if __name__ == "__main__":
	command = Tortus()
	command.run()
