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
from helper import ArgHelper
from search import traverse_pages
from urlparse import urlparse
import argparse, os

class Tortus(TortusScript):
	'''This class provides the common access point for all the tortus commands'''
	def __init__(self):

		self.parser = argparse.ArgumentParser()
		self.request = ScriptContext()
		self.parser.add_argument(
			"--page_name", 
			help="the name of the page being created")
		self.parser.add_argument(
			"--show_to_all", 
			help="flag if all users should have this page as a quicklink", 
			action="store_true")
		self.parser.add_argument(
			"--group_names", 
			help="the name of the groups to create a quicklink for", 
			action="store", 
			nargs="*")
		self.parser.add_argument(
			"--user_names", 
			help="the name of the users to create a central page for", 
			nargs="*")
		self.parser.add_argument(
			dest="filenames", 
			help="the names of the files to create pages from", 
			nargs='*')
		self.parser.add_argument(
			"--template", 
			help="if a page should be created for each group with the project template") #efault="homework_template"
		self.parser.add_argument(
			"--permissions", 
			help="specify the permissions for the page. ", 
			choices=['instructor_read_only', 'read_only', 'user_write_only', 'group_write_only'])
		self.parser.add_argument(
			"--url", 
			help="the url of the page you would like to push to users")
		self.parser.add_argument(
			"--project", 
			help="the project to push the page to")
		self.parser.add_argument(
			"--central_page", 
			help="flag to create a page for each user or group", 
			action="store_true")
		self.parser.add_argument(
			"--path", 
			help = "creates the page as a subpage. Subpage path is taken as space separated list", 
			nargs="*")
		self.args = self.parser.parse_args()
		self.opts = vars(self.parser.parse_args())
		self.page = TortusPage()

	def run(self):
		arghelper = ArgHelper(self.opts, self.parser)
		project, projects = arghelper.get_project(1)
		permissions = arghelper.get_permissions()
		acls = self.get_acls(permissions)
		group_obj = TortusGroup(project.name)
		arghelper.check_for_page()
		name = arghelper.check_name() #page name
		if self.args.template:
			self.template(self.args.template, permissions, project, name, acls)	
		elif self.args.filenames:
			self.filenames(self.args.filenames, permissions, project, name, acls) #What if a name is specified
		elif self.args.url:
			self.process_url(self.args.url, project, permissions, name, acls) #permissions

	def get_acls(self, permissions):
		'''Retrieves the correct permissions to add to each page
		@param permissions: the default or specified permissions from the user'''
		#Have I accounted for the case when the user specifies their own permissions
		acls = {}
		if self.args.user_names:
			acls.update({(user, get_permissions(user_name=user).get('user_write_only')) for user in self.args.user_names})
		if self.args.show_to_all:
			uids = user.getUserList(self.request)
			accounts = [user.User(self.request, uid).name for uid in uids]
			acls.update({(account, get_permissions(user_name=account).get('user_write_only')) for account in accounts})
			self.user_copy(accounts, project, page_name, file_path, homepage)
		if self.args.group_names:
			acls.update({(group, get_permissions(group_name=get_name(self.args.project, group_name=group).get('instructor_group_page')).get('group_write_only')) for group in self.args.group_names})
		return acls

	def template(self, template, permissions, project, name, acls = {}):	
		'''''Creates the page from a template
		@param template: the name of the page to be copied
		@param project: the project to add the page to
		@param name: the name of the new page
		@param acls: a dictionary with users or group keys and permission values '''
		if permissions == 'default':
			perm = get_permissions().get('read_only')
		else: 
			perm = get_permissions().get(permissions, 'read_only') 
		file_path = self.page.get_file_path(template, template=1)
		if acls:
			self.distribute_page(project, name, file_path, acls)
		else:
			self.page.add_from_file(file_path, project, get_name(project.name, name).get('generic_project_page'), 'user', perm)      
	
	def filenames(self, filenames, permissions, project, name="", acls= {}):
		'''Creates a page from a file
		@param filenames: the files that the pages should be created from
		@param project: the project to add the page to
		@param name: the name of the new page. Default extracts name from filename
		@param acls: a dictionary containing users or groups and the corresponding permissions'''
		for fname in filenames:
			if name is None:
				name = os.path.splitext(fname)[0]
			file_path = self.page.get_file_path(fname, file=1)
			if acls: #Fix this
				self.distribute_page(project, name, file_path, acls)
			else:
				if permissions == 'default':
					perm = get_permissions("").get('read_only')
				else: 
					perm = get_permissions("").get(permissions, 'read_only') 
				self.page.add_from_file(file_path, project, get_name(project.name, name).get('generic_project_page'), 'user', perm)

	def distribute_page(self, project, page_name, file_path, acls, homepage=0):
        # Checks for a template page and sets homepage_default_text
		"""Creates a copy of a page for each user or group
		@param project: the project the page and users belong to
		@param page_name: the name of the page that will be added for each user
		@param file_path: the path to the file or template containing the contents of the page
		@param homepage: set to 1 if the page will be the homepage for a user"""
		if self.args.user_names or self.args.show_to_all:
			self.user_copy(acls, project, page_name, file_path, homepage)
		elif self.args.group_names:
			for group in self.args.group_names:
				group_name = get_name(project.name, page_name, group_name=group).get('student_group_page')
				temp_group = self.request.groups.get(get_name(project.name, page_name, group_name=group).get('instructor_group_page'))
				if (temp_group and temp_group.member_groups):
					acls.extend({(group, get_permissions(group_name=temp_group.name).get('group_write_only')) for group in temp_group.member_groups})
					acls.pop(group)
			self.group_copy(acls, project, page_name, file_path)
		if not acls:
			print "No accounts selected for copy of page!"
			return
	
	def user_copy(self, acls, project, page_name, file_path, homepage=0):
		"""Creates a copy of a page for each user in members
		@param members: a list of members a copy should be made for
		@param project: the project the page should be created for
		@param page_name: the name of the page to be copied
		@param file_path: the path to the page to be copied"""
		for member in acls:
			# if homepage == 1:
			# 	if self.args.template:
			# 		self.page.get_file_path(template, template =1)
			# 		text = Page(self.request, self.args.template).get_raw_body()
			# else:
			# 	text = '''#acl %(user_name)s:read,write,delete,revert Default'''  #This is off
			# self.page.write_homepage(account, project.name, text)
			if homepage == 0: #This needs to change to an else
				perm = acls.get(member)
				pg_name = get_name(project.name, page_name, user_name=member).get('student_project_page')
				if self.args.url:
					self.page.add_from_file(file_path, project, pg_name, 'url', perm)
				else:
					self.page.add_from_file(file_path, project, pg_name, 'user', perm)

	def group_copy(self, acls, project, page_name, file_path):
		"""Creates a copy of a page for each group in accounts 
		@param accounts: a list of groups a copy should be created for
		@param project: the project the page should be created for
		@param page_name: the name of the page to be copied
		@param file_path: the path of the page to be copied"""
		for group in acls:
			perm = acls.get(group)
			pg_name = get_name(project.name, page_name, group_name=group).get('student_group_page')
			if self.args.url:
				self.page.add_from_file(file_path, project, pg_name, 'url', perm)
			else:
				self.page.add_from_file(file_path, project, pg_name, 'user', perm)

	def process_url(self, url, project, permissions, name, acls):
		'''''Creates the page from a url
		@param url: the url of the page to be copied
		@param project: the project to add the page to
		@param name: the name of the new page
		@param acls: a dictionary with users or group keys and permission values '''
		if permissions == 'default':
			perm = get_permissions().get('read_only') #Read only
		else: 
			perm = get_permissions().get(permissions, 'read_only') 
		wiki_data = os.path.basename(os.path.dirname(data_folder))
		url_parts = urlparse(url)
		page_name = (url_parts[2].rpartition(wiki_data + '/')[2]).rsplit('/')
		file_string = '(2f)'
		file_name = file_string.join(page_name)
		file_path = os.path.join(data_folder,'pages',file_name)
		if acls:
			self.distribute_page(project, name, file_path, acls)
		else:
			self.page.add_from_file(file_path, project, name, 'url', perm)
		page_link = '/'.join(page_name)
		if not Page(self.request, page_link).exists():
		    print "The url you have provided is not a page that has already been created"

if __name__ == "__main__":
	command = Tortus()
	command.run()