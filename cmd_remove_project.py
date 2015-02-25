#Tasks
#Remove Project
'''	1. Remove the project files
	2. Clean the json file
	3. Remove the pages relating to that project
	4. Regenerate the table of contents for users
'''

"""---------------------------------------------------------
Command - Remove...project
------------------------------------------------------------

This command allows users to remove a project using the command line"""

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
import argparse, os, re, sys, json, shutil, io
from search import search_pages, print_toc, create_page, find_groups, traverse_pages
#from search import 

class Tortus(TortusScript):

	def __init__(self):

		self.parser = argparse.ArgumentParser()
		self.request = ScriptContext()
		self.parser.add_argument(
			"--quick-link", #?? 
			help="flag if all users should have this page as a quicklink", 
			action="store_true")
		self.parser.add_argument(
			"--project", 
			help="the project to remove")
		self.args = self.parser.parse_args()
		self.opts = vars(self.parser.parse_args())
		self.page = TortusPage()

	def run(self):
		arghelper = ArgHelper(self.opts, self.parser)
		project, projects = arghelper.get_project()
		matches = traverse_pages(project.name, 1)
		groups = find_groups(matches)
		members = []
		for groups in groups.values():
			members.extend(groups)
		members = set(members) # update contents for these people
		self.remove_project_files(project, projects, matches)
		project.update_contents(members)
		self.group_obj = TortusGroup(project.name)
			

	def remove_project_files(self, project, projects, matches):
		exists = projects.project_exists(project.name)
		if exists == 0:
			with open (json_file, 'r+') as f:
				try:
					json_data = json.load(f)
					json_data["projects"].pop(project.name)
					f.seek(0)
					f.truncate()
  					json.dump(json_data, f)
					shutil.rmtree(os.path.join(project_files, project.name))
					page = TortusPage()
					for match in matches:
						moin_name = re.sub('\(2f\)', '/', match)
						page.delete_page(moin_name)
						try:
							shutil.rmtree(os.path.join(data_folder, 'pages', match))
						except OSError:
							print "The page {} doesn't exist".format(match)
							pass
				except KeyError:
					print "The project does not exist"
					return None

if __name__ == "__main__":
	command = Tortus()
	command.run()