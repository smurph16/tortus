"""---------------------------------------------------------
Command - Create Page
------------------------------------------------------------

This command allows instructors to specify the links that should appear in the task-bar"""

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
		page = TortusPage()
		ids = page.process_user_ids(project, self.args)
		arghelper.check_links()
		pages = self.args.pages
		if self.args.filename:
			pages = get_links_from_file(self.args.filename)
		page.add_link(ids, pages, project)

		#if a file is specified, read the pages from a file and process the args for who
	
	def get_links_from_file(self, path):
		pages = []
		try:
			with open (path, 'r') as f:
				for line in f:
					pages.append(line)
		except IOError:
			print "The file could not be found"
		return pages

	def page_name(self, page, project): #Move to tortus_group
		if page.find("Project"):
			return page
		else:
			return "{}Project/{}".format(project.name, page)

if __name__ == "__main__":
	command = Tortus()
	command.run()