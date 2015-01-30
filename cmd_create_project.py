"""-------------------------------------------------------
Command - Create Project
------------------------------------------------------------

This command allows users to create projects from the command line"""

from tortus_command import TortusScript
from tortus_page import TortusPage
from MoinMoin.web.contexts import ScriptContext
from default import *
from tortus_project import TortusProjectCollection, TortusProject
from helper import ArgHelper
import argparse, os
import sys

class Tortus(TortusScript):

	def __init__(self):

		self.parser = argparse.ArgumentParser()
		self.request = ScriptContext()
		self.parser.add_argument(
			"--name", 
			help="the name of the project being created") 
		self.parser.add_argument(
			"--permissions", 
			help="the permissions for the central page")
		self.args = self.parser.parse_args()
		self.opts = vars(self.args)
		self.page = TortusPage()

	def run(self):	
		arghelper = ArgHelper(self.opts, self.parser)
		if not (self.args.name):
			self.parser.error ("Please specify a name for the project")
			sys.exit()
		project_name = self.args.name
		permissions = arghelper.get_permissions()
		projects = TortusProjectCollection()
		if projects.project_exists(project_name) == 0:
			print "A project by that name already exists"
			sys.exit()
		else:
			project = projects.tortus_project(name = project_name, groups={}, args=self.args)

if __name__ == "__main__":
	command = Tortus()
	command.run()
