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
		self.parser.add_argument("--project", help="the name of the project groups are being created for")
		self.parser.add_argument(dest="filename", help="the name or path of the files storing the groups to be modified") #Must edit if exists
		self.parser.add_argument("--permissions", default="instructor_read_only", help="specify the permissions for the group pages. Default: instructor_read_only")
		self.args = self.parser.parse_args()

	def command_line_processing(self):
		if not self.args.filename:
			self.parser.error("Must specify  path to file containing groups to be modified")
			return
		if self.args.project:
			project_name = self.args.project
		else:
			default_project = raw_input("These groups will be modified from the project DefaultProject. Please Y to proceed or any other key to cancel: ")
			if not default_project == "Y":
				return
			project_name = "default"
		projects = TortusProjectCollection()
		if not (projects.project_exists(project_name) == 0): #Check for project files?
			print "This project does not exist yet. Groups cannot be modified."
			return #Exit if project shouldn't be created
		#Get the project again/
		project = projects.tortus_project(name=project_name, groups={}, args=self.args) #This is a retrieval step...initialises it with existing data
		group_obj = TortusGroup(project.name)
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

	def process_path(self, path):
		"""Return a path to a record of the created groups_created
		@param path: the text file containing the groups"""
		(file_name, file_extension) = os.path.splitext(path)
		file_name = "{0}_grouped{1}".format(file_name, file_extension)
		grouped_file = os.path.join(os.path.dirname(os.path.abspath(path)), file_name)
		return grouped_file

	def write_homepage(self, account, homepage_text):
	# writes the homepage
		if account.exists() and not account.disabled and not Page(self.request, account.name).exists():
			userhomepage = PageEditor(self.request, account.name)
			try:
				userhomepage.saveText(homepage_text, 0)
				print "Central page created for %s." % account.name
			except userhomepage.Unchanged:
				print "You did not change the page content, not saved!"
			except userhomepage.NoAdmin:
				print "You don't have enough rights to create the %s page" % account.name
		else:
			print "Page for %s already exists or account is disabled or user does not exist." % account.name

	def remove_group_of_groups(self, name):
		"""Remove a subset of groups specified by a name pattern or prefix
		@param name: the name of the subset of groups"""
		groups = self.request.groups
		gname = '{0}Group'.format(name)
		if gname in groups:
			main_group = groups.get(gname)
			print main_group.name
			for member_group in main_group.member_groups:
				print member_group
				if member_group in groups:
					print "in"
					remove_group_process(member_group)
			selfself.remove_group_process(gname)

	def format_members(self, members):
		formatted_members = [" * {0}".format(member) for member in members]
		return formatted_members
	# Read the file
	# Store the  


	def modify_groups(self, modified_groups):
		"""Modify the groups from a modified all_groups_file
		@param modified_groups the text file containing the alterations"""
		with open(all_groups_path, 'r+') as all_groups:
			with open (modified_groups, 'r') as new_groups:
				old_groups = all_groups.read()
				revised_groups = new_groups.read()
				f_pattern = re.compile('-{40}\n.+\n-{40}[^----------]*', re.M)
				match = re.findall(f_pattern, revised_groups)
				if match:
					for group in match:
						previous_line = ""
						members = set()
						revised_members_set = set()
						revised_members_text = ""
						for line in group.split('\n'):
							if previous_line.startswith("-------------------"):
								name = line
								previous_line = "done"
							if previous_line != "done":
								previous_line = line
							if line.startswith(" *"):
								revised_members_text += line + "\n"
								line = re.sub(r" \*\s?", "", line)
								revised_members_set.add(line)
								#revised_members.add(line.split(" *"))
								#revised_members += "\n"
						if Page(self.request, name).exists():
							text = Page(self.request, name).get_raw_body()
							for line in text.split('\n'):
								if line.startswith(" *"):
									members.add(re.sub(r" \*\s?", "", line))
							print members
							if not (revised_members_set-members or members-revised_members_set):
								continue
							for member in (revised_members_set - members):
								print "Adding member {0} to group {1}".format(member, name)
							for member in (members - revised_members_set):
								print "Removing member {0} from group {1}".format(member, name)
							g_pattern = re.compile('^ \*.+\n', re.M)
							match_obj = re.findall(g_pattern, text)
							print len(match_obj	)
							text = re.sub(g_pattern, "", text, count = len(match_obj)-1)
							text = re.sub(g_pattern, revised_members_text, text, count=1)
							print PageEditor(self.request, name).saveText(text, 0)
							#print "members: " + members 
						else:
							self.create_group_page(name, revised_members_text)

if __name__ == "__main__":
	command = Tortus()
	command.run()

