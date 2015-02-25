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
			help="the name of the users to create a copy of the page for", 
			nargs="*")
		self.parser.add_argument(
			dest="filenames", 
			help="the names of the files to create pages from", 
			nargs='*')
		self.parser.add_argument(
			"--template", 
			help="if a page should be created for each group with the project template")
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
		self.args = self.parser.parse_args()
		self.opts = vars(self.parser.parse_args())
		self.page = TortusPage()

	def run(self):
		arghelper = ArgHelper(self.opts, self.parser)
		project, projects = arghelper.get_project(1)
		permissions = arghelper.get_permissions()
		acls = self.get_acls(permissions)
		group_obj = TortusGroup(project.name)
		page = TortusPage()
		arghelper.check_for_page()
		name = arghelper.check_name()
		if self.args.template:
			page.template(self.args.template, permissions, project, name, acls)	
		elif self.args.filenames:
			page.filenames(self.args.filenames, permissions, project, name, acls)
		elif self.args.url:
			page.process_url(self.args.url, project, permissions, name, acls)

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

if __name__ == "__main__":
	command = Tortus()
	command.run()