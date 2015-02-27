"""---------------------------------------------------------
Command - Create Groups
------------------------------------------------------------

This command allows users to create groups from the command line"""

import path
from tortus_command import TortusScript
from tortus_project import TortusProjectCollection
from tortus_page import TortusPage
from tortus_group import TortusGroup
from MoinMoin.web.contexts import ScriptContext
from MoinMoin import user #Don't think that I need this
from default import *
from helper import ArgHelper
import argparse, os	

class Tortus(TortusScript):

	def __init__(self):
		import argparse
		self.request = ScriptContext()
		self.parser = argparse.ArgumentParser()
		self.parser.add_argument(
			"--project", help="the name of the project groups are being created for")
		self.parser.add_argument(
			"--group_name", help="the name of the group to create, delete or modify", action="store")
		self.parser.add_argument(
			"--member_names", help="members of the group to be added, deleted or modified", nargs='*', action="store")
		self.parser.add_argument(
			dest="filenames", help="the names of the files storing the groups to be modified", nargs='*')
		self.parser.add_argument(
			"--permissions", default="instructor_read_only", help="""specify the permissions for the group pages
			Default: instructor_read_only""")
		self.parser.add_argument(
		"--group_prefix", help="a prefix for naming groups") #Do I need this?
		self.args = self.parser.parse_args()
		self.opts = vars(self.args)
		
	def run(self): 
		arghelper = ArgHelper(self.opts, self.parser)
		arghelper.check_create()
		project, projects = arghelper.get_project(1)
		group_obj = TortusGroup(project.name)
		if self.args.group_prefix:
			name = self.args.group_prefix
		elif self.args.group_name: #Error check here
			name = self.args.group_name
		else:
			name = project.name #Default 
		grps_to_create = []
		if self.args.filenames:
			for fname in self.args.filenames:
				if group_obj.process_group_file(fname) is not None:
					grps_to_create.extend(group_obj.process_group_file(fname))
				else:
					print "Could not create any groups."
					return
		elif self.args.member_names:
			grps_to_create.append([member for member in self.args.member_names])
		group_obj.create_groups(grps_to_create, name, project, projects)

if __name__ == "__main__":
	command = Tortus()
	command.run()
