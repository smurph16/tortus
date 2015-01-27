"""--------------------------------------------------------------------------------------
	Accessing groups
--------------------------------------------------------------------------------------

This program allows groups to be deleted.

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
#from admin_config import number_of_projects, number_of_groups
from MoinMoin.web.contexts import ScriptContext
from MoinMoin.Page import Page
from MoinMoin import user, wikiutil
from default import * # alter default file if groups, templates or pages are in a different location
from tortus_command import TortusScript

class isRoot(object):
	def __getattr__(self, name):
		return lambda *args,**kwargs: True

class RemoveGroups(TortusScript):

	format_string = '\n----------------------------------------\n'
	#To Do
	#Add ability to compare files
	#Add ability to create project page for each group

	#This is a bit annoying...It isn't updating..It's completely re-writing the file
	def remove_group(self, name):
		#Find the group files....could do this with PageEditor(request, pagename).deletePage()
		"""Remove a single group from the pages directory
		@param name: the name of the group to be removed"""
		group_page_path = os.path.join(data_folder, 'pages', name)
		if os.path.exists(group_page_path):
			print "Removed Group with name: {}".format(name)
			shutil.rmtree(group_page_path)
		else: 
			print "Unable to find Group with name: {}".format(name)
			return
		self.create_copy()
		self.create_all_groups_version(name)

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
		print "create copy"
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
						#classification = f.readline()
						#if classification = "#user":
							#remove_group(group)
				
			# Create copy
			# create_copy()
			# Clear all_groups file
			#open(all_groups_path, 'w').close()
		else:
			print "Deletion aborted"

	def __init__(self):
		import argparse
		self.request = ScriptContext() 	
		self.parser = argparse.ArgumentParser()
		self.parser.add_argument("--project_name", help="the name of the project groups are being created for")
		self.parser.add_argument("-all", "--clear_all_groups", help="delete all user groups", action="store_true")
		self.parser.add_argument("--group_name", help="the name of the group to create, delete or modify", action="store", nargs="*")
		self.parser.add_argument(dest="filenames", help="the names of the files storing the groups to be modified", nargs='*')
		self.parser.add_argument("--categorise", help="if a group should be created containing the new groups", action="store")
		self.parser.add_argument("--prefix", help="a prefix for naming groups") #should this be handled by categorise?
		self.args = self.parser.parse_args()


	def command_line_processing(self):

		if self.args.clear_all_groups:
			delete_all = 1
			self.remove_all_groups()
			print "Deleting all groups"
    	#Group(s) to be deleted must be specified on command line or in text-file
		elif not (self.args.group_name or self.args.filenames or self.args.prefix):
			self.parser.error("Must specify group name in command line or path to file containing group_names to be deleted")
			return
		delete = 1
		if self.args.group_name:
			for gname in self.args.group_name:
				self.remove_group_process(gname)
		elif self.args.prefix:
			self.remove_group_of_groups(self.args.prefix)
		else:
			for fname in self.args.filenames:
				with open(fname, 'r') as f:
					for gname in f:
						gname = gname.rstrip('\n')
						remove_group_process(gname)
		self.create_copy() #This is in the incorrect spot...move it

	def remove_group_process(self, gname):
		"""Removes a group and edits the all_groups_file
		@param gname: the group to be deleted"""
		self.remove_group(gname)
		print "Deleting group {0}".format(gname)
		text = self.remove_from_all_groups_file(gname)
		self.write_all_groups_file(text)

	def run(self): 
		self.request.user.may = isRoot()
		self.command_line_processing()

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

if __name__ == "__main__":
	remove_group = RemoveGroups()
	remove_group.run()

	# Read the file
	# Store the 