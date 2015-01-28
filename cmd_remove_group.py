
"""--------------------------------------------------------------------------------------
	Accessing groups
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

class Tortus(TortusScript):

	def __init__(self):
		import argparse
		self.request = ScriptContext()
		self.parser = argparse.ArgumentParser()
		self.parser.add_argument("--project", help="the name of the project groups are being created for")
		self.parser.add_argument("--group_names", help="the name of the groups to delete", action="store", nargs='*')
		self.parser.add_argument(dest="filenames", help="the names of the files storing the groups to be deleted", nargs='*')
		self.parser.add_argument("--categorise", help="if a group should be created containing the new groups", action="store") #Must edit if exists
		self.parser.add_argument("--permissions", default="instructor_read_only", help="specify the permissions for the group pages. Default: instructor_read_only")
		self.parser.add_argument("--group_prefix", help="delete all groups with this prefix") #Do I need this?
		self.args = self.parser.parse_args()

	def command_line_processing(self):
		if not (self.args.group_names or self.args.filenames):
			self.parser.error("Must specify group_name in command line or path to file groups to be deleted")
			return
		if self.args.project:
			project_name = self.args.project
		else:
			default_project = raw_input("This group will be deleted from the project DefaultProject. Please Y to proceed or any other key to cancel: ")
			if not default_project == "Y":
				return
			project_name = "default"
		projects = TortusProjectCollection()
		if not (projects.project_exists(project_name) == 0): #Check for project files?
			print "This project does not exist yet. Groups cannot be deleted from it"
			return #Exit if project shouldn't be created
		#Get the project again/
		project = projects.tortus_project(name=project_name, groups={}, args=self.args) #This is a retrieval step...initialises it with existing data
		group_obj = TortusGroup(project_name)
		groups_to_be_deleted = []
		if self.args.group_names:
			for grp in self.args.group_names:
				groups_to_be_deleted.append(grp) #This isn't the name
		elif self.args.group_prefix:
			pass
			#Not yet implemented
		elif self.args.filenames:
			for fname in self.args.filenames:
				if group_obj.process_delete_group_file(fname) is not None:
					groups_to_be_deleted.extend(group_obj.process_delete_group_file(fname))
				else:
					print "Could not delete any groups."
					return
		deleted_groups = []	
		failed_groups = []
		for group in groups_to_be_deleted:
			name = "{0}Project/{1}Group".format(project.name, group)
			removed = self.remove_group(name)
			#formatted_members = group_obj.format_members(group)
			if removed == 1:
				failed_groups.append(group)
			else:
				deleted_groups.append(group)
		for group in deleted_groups:
			name = group.decode('utf-8')
			try:
				project.groups.pop(name)
			except KeyError:
				failed_groups.append(group)
				deleted_groups.remove(group)
		project.write_project_group_file()
		projects.update_groups(project, 'groups')
		self.print_actions(group_obj, deleted_groups, failed_groups)
				 #need get groups method

	def run(self): 
		self.command_line_processing()

	def remove_group(self, name):
		#Find the group files....could do this with PageEditor(request, pagename).deletePage()
		# """Remove a single group from the pages directory
		# @param name: the name of the group to be removed"""
		# group_page_path = os.path.join(data_folder, 'pages', name)
		# if os.path.exists(group_page_path):
		# 	shutil.rmtree(group_page_path)
		# 	return 0
		# else: 
		# 	return 1
		pg_obj = TortusPage()
		pg = Page(self.request, name)
		if pg.exists():
			pg_obj.delete_page(name) # This doesn't work
			print name
			return 0
		else:
			return 1

		#self.create_copy()
		#self.create_all_groups_version(name)

	def print_actions(self, group_obj, deleted_groups, failed_groups):
		""""""
		for group in failed_groups:
			print "Failed to remove group {}".format(group)
		for group in deleted_groups:
			print "Deleted group with name {0}".format(group)

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

if __name__ == "__main__":
	command = Tortus()
	command.run()


	
	def create_all_groups_version(self, name):
		"""Create a new version of the all_groups file after removed group
		@param name: the name of the removed_group""" #Needed when verification of modified file is implemented
		writing = True
		count = 0
		with open(all_groups_path,'r+') as all_groups:
			with open(os.path.join(os.path.dirname(all_groups_path), 'all_groups_revised.txt'), 'w') as all_groups_revised:	
				for num, line in enumerate(all_groups):
					if writing:
						if line.strip() == name:
							writing = False
						else:
							all_groups_revised.write(line)
					elif line == "----------------------------------------\n": 
						count += 1
						if count == 2:
							writing = True
		#Needs to change so that all groups file gets overwritten

	def remove_from_all_groups_file(self, name):
		"""Remove the deleted group from the all_groups file
		@param name: the name of the group to be deleted"""
		all_groups_file = open (all_groups_path, 'r+')
		all_groups = all_groups_file.read()
		pattern = re.compile('-{40}\n%s\n-{40}[^----------]*'%name, re.M)
		#result = pattern.match(all_groups)
		#print "match found", result
		new_text = re.sub(pattern, "", all_groups)
		return new_text

	def write_all_groups_file(self, text):
		"""Write the remaining groups back to the all_groups_file
		@param text: the all_groups"""
		with open(all_groups_path, 'w') as all_groups_file:	
			all_groups_file.write(text)
			all_groups_file.close()

	def create_copy(self):
		"""Create a copy of the all_groups file for back-up"""
		global all_groups_path
		print "Create copy"
		string = time.ctime(os.path.getmtime(all_groups_path))
		modification = '_' + string.replace(' ', '-')
		(file_name, file_extension) = os.path.splitext(all_groups_path)
		file_name = os.path.basename(file_name)
		print file_name
		dir_name = os.path.dirname(all_groups_path)
		file_name = file_name + modification + file_extension
		retain_file = os.path.join(dir_name, 'revisions', file_name)
		try:
			shutil.copy(all_groups_path, retain_file)
		except shutil.Error as e:
			print 'A revision file was not made. Error %s' % e
		except OSError as e:
			print 'A revision file was not made. Error: %s' % e

		#Remove the group from all_groups

	#def remove_multiple_groups():
		#Ideal if I can choose only to write to one file

	def remove_all_groups(self):
		"""Remove all the groups designated as ..... group"""
		global all_groups_path
		check = raw_input("Are you sure you want to remove all user groups from this wiki? This action cannot be undone...easily: Type Y to continue with deletion ")
		if check == "Y":
			# Remove pages
			# for all groups with user tag, remove the page
			groups = self.request.groups
			for group in groups:
				group_page_path = os.path.join("/usr/local/share/moin/eduwiki/data/pages", group)
				if os.path.exists(group_page_path):
					pagename = group
					text = Page(self.request, pagename).get_raw_body()
					if text.split('\n', 1)[0] == "##category: User":
						self.remove_group(group)
						text = self.remove_from_all_groups_file(group)
						self.write_all_groups_file(text)
		else:
			print "Deletion aborted"

	def remove_group_process(self, gname):
		"""Removes a group and edits the all_groups_file
		@param gname: the group to be deleted"""
		self.remove_group(gname)
		print "Deleting group {0}".format(gname)
		text = self.remove_from_all_groups_file(gname)
		self.write_all_groups_file(text)

	# def run(self): 
	# 	self.request.user.may = isRoot()
	# 	self.command_line_processing()

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