#1. Get groups from the json file
#2. Read new groups into a dictionary from the text file
#3. Check for each group
#4. Add to add queue if not present
#5. Add to delete queue if removed
#6. Add to modified members if members modified
#7. Modify the members

"""--------------------------------------------------------------------------------------
	Accessing groups
--------------------------------------------------------------------------------------

This command allows groups to be modified using a text file.

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
from helper import ArgHelper

class DictDiffer(object):
	"""Calculate the differences between dictionaries
	1.Take note of items added
	2.Take note of items removed
	3.Take note of keys that are the same in both with values changed
	4.Take note of keys that are the same in both with values unchanged"""

	def __init__(self, old_dict, new_dict):
		self.new_dict, self.old_dict = new_dict, old_dict
		self.new_set, self.old_set = set(new_dict.keys()), set(old_dict.keys())
		self.intersect = self.new_set.intersection(self.old_set)

	def added(self):
		return dict ((o, self.new_dict[o]) for o in (self.new_set - self.intersect))
	def removed(self):
		return list(self.old_set - self.intersect)
	def changed(self):
		return list(set (o for o in self.intersect if self.old_dict[o] != self.new_dict[o]))
	def changed_set(self):
		return dict(((o, self.new_dict[o]) for o in self.intersect if set(self.old_dict[o]) != set(self.new_dict[o])))
	def unchanged(self):
		return list(set (o for o in self.intersect if self.old_dict[o] == self.current_dict[o]))

class Tortus(TortusScript):

	def __init__(self):
		import argparse
		self.request = ScriptContext()
		self.parser = argparse.ArgumentParser()
		self.parser.add_argument(
			"--project", 
			help="the name of the project groups are being created for")
		self.parser.add_argument(
			"--get_file", 
			help="create a copy of the project groups and store in the current working directory ", 
			action='store_true')
		self.parser.add_argument(
			"--filename", 
			help="the name or path of the files storing the groups to be modified") #Must edit if exists
		self.parser.add_argument(
			"--permissions", 
			default="instructor_read_only", 
			help="specify the permissions for the group pages. Default: instructor_read_only")
		self.args = self.parser.parse_args()
		self.opts = vars(self.parser.parse_args())

	def command_line_processing(self):
		arghelper = ArgHelper(self.opts, self.parser)
		project, projects = arghelper.get_project()
		arghelper.get_group_copy(project.name)
		group_obj = TortusGroup(project.name)
		if not self.args.filename:
			self.parser.error("Must specify path to file containing groups to be modified")
			return
		new_groups = group_obj.process_modified_group_file(self.args.filename)
		d = DictDiffer(project.groups, new_groups)
		groups_to_be_deleted = d.removed() #list
		groups_to_be_created = d.added() #dictionary
		groups_to_be_modified = d.changed_set()
		self.print_actions(groups_to_be_created, groups_to_be_modified, groups_to_be_deleted)
		check_changes = raw_input ("Please Y to proceed or any other key to cancel: ")
		if not check_changes == "Y":
			return
		else:
			group_obj.create_groups(groups_to_be_created, "", project, projects)
			group_obj.delete_groups(groups_to_be_deleted, project, projects)
			group_obj.modify_groups(groups_to_be_modified, project, projects)
	
	def print_actions(self, create_dict, modify_dict, remove_list):
		"The following actions will be carried out in this project"
		if len(create_dict.items()) > 0: 
			for (group, members) in create_dict.iteritems():
				print "Create Group with name {0} and members {1}".format(group, members)
		if len(modify_dict.items()) > 0:
			for (group, members) in modify_dict.iteritems():
				print "Modify Group with name {0} and members {1}".format(group, members)
		if len(remove_list) > 0:	
			for group in remove_list:
				print "Remove Group with name {0}".format(group)

	def run(self): 
		self.command_line_processing()

if __name__ == "__main__":
	command = Tortus()
	command.run()

