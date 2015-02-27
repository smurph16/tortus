#!/usr/bin/env python

"""---------------------------------------------------------
Command - Create Page
------------------------------------------------------------

This command allows users to create pages from the command line"""

import path
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
		user_acls, group_acls = self.get_acls(permissions)
		group_obj = TortusGroup(project.name)
		page = TortusPage()
		arghelper.check_for_page()
		name = arghelper.check_name()
		if self.args.template:
			page.template(self.args.template, permissions, project, name, user_acls, group_acls)	
		elif self.args.filenames:
			page.filenames(self.args.filenames, permissions, project, name, user_acls, group_acls)
		elif self.args.url:
			page.process_url(self.args.url, project, permissions, name, user_acls, group_acls)

	def get_acls(self, permissions):
		'''Retrieves the correct permissions to add to each page
		@param permissions: the default or specified permissions from the user'''
		#Have I accounted for the case when the user specifies their own permissions
		user_acls = {}
		group_acls = {}
		if self.args.user_names:
			user_acls.update({(user, get_permissions(user_name=user).get('user_write_only')) for user in self.args.user_names})
		if self.args.show_to_all:
			uids = user.getUserList(self.request)
			accounts = [user.User(self.request, uid).name for uid in uids]
			user_acls.update({(account, get_permissions(user_name=account).get('user_write_only')) for account in accounts})
			self.user_copy(accounts, project, page_name, file_path, homepage)
		if self.args.group_names:
			group_acls.update({(group, get_permissions(group_name=get_name(self.args.project, group_name=group).get('instructor_group_page')).get('group_write_only')) for group in self.args.group_names})
		return (user_acls, group_acls)

if __name__ == "__main__":
	command = Tortus()
	command.run()
