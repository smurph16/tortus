"""-------------------------------------------------------
Command - Create Project
------------------------------------------------------------

This command allows users to create projects from the command line"""

from tortus_command import TortusScript
from tortus_page import TortusPage
from MoinMoin.web.contexts import ScriptContext
from default import *
from tortus_project import TortusProjectCollection, TortusProject
import argparse, os

class Tortus(TortusScript):

	def __init__(self):

		self.parser = argparse.ArgumentParser()
		self.request = ScriptContext()
		self.parser.add_argument("--name", help="the name of the project being created") 
		self.parser.add_argument("--permissions", help="the permissions for the central page")
		self.args = self.parser.parse_args()
		#self.page = TortusPage()

	def run(self):	
		name = None
		if not (self.args.name):
			self.parser.error ("Please specify a name for the project")
			return
		name = "Project{}".format(self.args.name)
		if not (self.args.permissions):
			 	self.args.permissions = 'instructor_read_only'
		projects = TortusProjectCollection()
		if projects.exists(name):
			print "A project by that name already exists"
			return
		else:
			projects.tortus_project(name, self.args)

if __name__ == "__main__":
	command = Tortus()
	command.run()
