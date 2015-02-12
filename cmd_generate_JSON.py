#Tasks
#Generate json
'''
	1. Get every page from the pages directory
	2. Find any page that has Project in it
	3. Assign groups to projects
	4. Generate a new json object in a clean json file

#How do I fix the project files...rewrite the group file...who cares about revisisons
#Delete any projects that aren't in your json file now
#Add any projects that are
#How to handle user pages

#Tasks
#Remove Project
	1. Remove the project files
	2. Clean the json file
	3. Remove the pages relating to that project
	4. Regenerate the table of contents for users
'''

"""---------------------------------------------------------
Command - Generate JSON file
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
		self.args = self.parser.parse_args()
		self.opts = vars(self.parser.parse_args())
		self.page = TortusPage()

	def run(self):
		arghelper = ArgHelper(self.opts, self.parser)
		projects = TortusProjectCollection()
		json_data = projects.json_create_project_structure()
		pattern = re.compile('.*Project$')
		projects = [project for project in os.listdir(os.path.join(data_folder, 'pages')) if re.search(pattern, project)]
		print projects
		for project in projects:
			project_name = re.sub("Project", "", project)
			matches = traverse_pages(project_name, 1)
			groups = find_groups(matches)
			p = {project_name: {"name":project_name, "moin_name":project, "groups":groups}}
			json_data["projects"].update(p)
		with open (json_file, 'w') as f:
			f.truncate()
			f.seek(0)
			json.dump(json_data, f)

	def remove_project_files(self, project, projects, matches):
		exists = projects.project_exists(project.name)
		if exists == 0:
			with open (json_file, 'r+') as f:
				try:
					json_data = json.load(f)
					print json_data
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
		
	def update_contents(self, members, project):
		for name in members:
			needle = "t:{}".format(name)
			if search_pages(needle): #Try Except
				graph, reverse_dict = search_pages(needle)
				print graph
				print_toc(graph, reverse_dict)
				with open ('temp.txt', 'r') as page:
					text = page.read()
					create_page(text, name)

if __name__ == "__main__":
	command = Tortus()
	command.run()

