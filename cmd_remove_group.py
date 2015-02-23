
"""--------------------------------------------------------------------------------------
	Deleting groups
--------------------------------------------------------------------------------------

This command allows groups to be deleted.

Detailed Instructions:
======================

    1. Remove a group from the command line by specifying its name

	E.g. python accessing_groups.py --remove_group --group_name=exampleGroup

    2. Remove all groups from the command line that are assigned the category User

	E.g. python remove_group.py -all 

	3. Remove all groups with certain prefix

	E.g. python accessing_groups.py --remove_group --prefix=example_group_prefix"""

from MoinMoin.PageEditor import PageEditor
from MoinMoin.script import MoinScript
import sys, argparse, re, os.path, shutil, time, difflib
from MoinMoin.web.contexts import ScriptContext
from MoinMoin.Page import Page
from MoinMoin import user, wikiutil
from default import * # alter default file if groups, templates or pages are in a different location
from tortus_command import TortusScript
from tortus_project import TortusProjectCollection
from tortus_page import TortusPage
from tortus_group import TortusGroup
import argparse
from helper import ArgHelper

class Tortus(TortusScript):

	def __init__(self):
		import argparse
		self.request = ScriptContext()
		self.parser = argparse.ArgumentParser()
		self.parser.add_argument(
			"--project", 
			help="the name of the project groups are being created for")
		self.parser.add_argument(
			"--group_names", 
			help="the name of the groups to delete", 
			action="store", 
			nargs='*')
		self.parser.add_argument(
			dest="filenames", 
			help="the names of the files storing the groups to be deleted", 
			nargs='*')
		self.parser.add_argument(
			"--all", 
			help="remove all groups in a particular project", 
			action="store_true") #Must edit if exists
		self.parser.add_argument(
			"--permissions", 
			default="instructor_read_only", 
			help="specify the permissions for the group pages. Default: instructor_read_only")
		self.parser.add_argument(
			"--group_prefix", 
			help="delete all groups with this prefix") #Do I need this?
		self.args = self.parser.parse_args()
		self.opts = vars(self.args)

	def command_line_processing(self):
		name = None
		arghelper = ArgHelper(self.opts, self.parser)
		project, projects = arghelper.get_project()
		permissions = arghelper.get_permissions()
		group_obj = TortusGroup(project.name)
		arghelper.check_delete()
		groups_to_be_deleted = []
		if self.args.group_names:
			for grp in self.args.group_names:
				groups_to_be_deleted.append(grp) #This isn't the name
		elif self.args.group_prefix:
			groups_to_be_deleted.extend([group for group in project.groups.keys() if self.args.group_prefix in group])
		elif self.args.all:
			groups_to_be_deleted.extend([group for group in project.groups.keys()])		
		elif self.args.filenames:
			for fname in self.args.filenames:
				if group_obj.process_delete_group_file(fname) is not None:
					groups_to_be_deleted.extend(group_obj.process_delete_group_file(fname))
				else:
					print "Could not delete any groups."
					return
		group_obj.delete_groups(groups_to_be_deleted, project, projects)

	def run(self): 
		self.command_line_processing()

if __name__ == "__main__":
	command = Tortus()
	command.run()
