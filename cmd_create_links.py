"""---------------------------------------------------------
Command - Create Page
------------------------------------------------------------

This command allows instructors to specify the links that should appear in the task-bar"""

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
import argparse, os

class Tortus(TortusScript):

	def __init__(self):

		self.parser = argparse.ArgumentParser()
		self.request = ScriptContext()
		self.parser.add_argument(
			"--pages", 
			help="the name of the page to create a link to", nargs="*")
		self.parser.add_argument(
			"--all", 
			help="flag if all users should have this page as a quicklink", 
			action="store_true")
		self.parser.add_argument(
			"--group_names", 
			help="the name of the groups to create a quicklink for", 
			action="store", 
			nargs="*")
		self.parser.add_argument(
			"--user_names", 
			help="the name of the users to create a quicklink for", 
			nargs="*")
		self.parser.add_argument(
			"--filename", 
			help="the names of the files containing pages to add quicklinks for")
		self.parser.add_argument(
			"--project", 
			help="specify the name of a project which all members should have in their task-bar")
		self.args = self.parser.parse_args()
		self.opts = vars(self.parser.parse_args())
		self.page = TortusPage()

	def run(self):
		arghelper = ArgHelper(self.opts, self.parser)
		arghelper.check_users()
		project, projects = arghelper.get_project(1)
		self.group_obj = TortusGroup(project.name)
		ids = self.process_user_ids(project, self.args)
		arghelper.check_links()
		pages = self.args.pages
		if self.args.filename:
			pages = get_links_from_file(self.args.filename)
		self.add_link(ids, pages, project)

		#if a file is specified, read the pages from a file and process the args for who

	def process_user_ids(self, project, args):
		"""Add a link in the users task-bar to a specific page
		@param page_name: the name of the page to add a quick link to
		@args: command line arguments"""
		user_ids = None
		if args.all:
			user_ids = user.getUserList(self.request)
		elif args.group_names:
			group_names = [TortusGroup(project).get_moin_name(group) for group in args.group_names]
			user_ids = self.group_obj.retrieve_members(group_names) #Retrieve members is in groups
		elif args.user_names:
			user_ids =[user.getUserId(self.request, member) for member in args.user_names] 
		elif args.project:
			user_ids = [user.getUserId(self.request, member) for member in project.get_members()]
		return user_ids
	
	def get_links_from_file(self, path):
		pages = []
		try:
			with open (path, 'r') as f:
				for line in f:
					pages.append(line)
		except IOError:
			print "The file could not be found"
		return pages

	def add_link(self, user_ids, pages, project):
		t_page = TortusPage()
		if user_ids is not None:
			for uid in user_ids:
				if user.User(self.request, uid).exists():
					for page in pages:
						page = self.page_name(page, project)
						t_page.add_quick_link(uid, page)

	def page_name(self, page, project): #Move to tortus_group
		if page.find("Project"):
			return page
		else:
			return "{}Project/{}".format(project.name, page)

if __name__ == "__main__":
	command = Tortus()
	command.run()