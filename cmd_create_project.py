#!/usr/bin/env python

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
	'''The tortus class provides a common access point for the commands. It controls
	the program flow from the command line'''
	
	def __init__(self):

		self.parser = argparse.ArgumentParser()
		self.request = ScriptContext()
		self.parser.add_argument(
			"--project", 
			help="the name of the project being created", 
			action="store") 
		self.parser.add_argument(
			"--permissions", 
			help="the permissions for the central page")
		self.args = self.parser.parse_args()
		self.opts = vars(self.args)
		self.page = TortusPage()

	def run(self):	
		arghelper = ArgHelper(self.opts, self.parser)
		if not (self.args.project):
			self.parser.error ("Please specify a name for the project")
			sys.exit()
		permissions = arghelper.get_permissions()
		project, projects = arghelper.get_project(1)

if __name__ == "__main__":
	command = Tortus()
	command.run()
