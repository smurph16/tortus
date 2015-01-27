"""--------------------------------------------------------------------------------------
	Accessing groups
--------------------------------------------------------------------------------------

This program allows groups to be added, deleted and modified.  Pages created with these
actions are usually only for organisation purposes"""

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

class AccessingGroups(TortusScript):

	format_string = '\n----------------------------------------\n'
	#To Do
	#Add ability to compare files
	#Add ability to create project page for each group
	#Edit group counter so as not to overwrite groups


	def create_group_page(self, page_name, members, group=0):
		"""Create a group page with the given members and group name
		@param page_name: the name of the page_name
		@param members: members to be added to the group
		@param group: if 1, categorise as group page (default: 0)"""
		if group == 1:	
			text = "##category: Group\n{0}{1}".format(get_permissions().get('instructor_read_only'), members)
		else :
			text = "##category: User\n{0}{1}".format(get_permissions().get('instructor_read_only'),members) #change this
		#text += members
		print PageEditor(self.request, page_name).saveText(text, 0)
		print "Group successfully created with name: {0}".format(page_name)
		print "Members:\n%s" % members
		return 0 #Need this to maintain integrity but currently not implemented....need to check page exists?

	#list comprehension for group file
	def process_group_file(self, path, group_name="default"):
	# if file path/paths are provided, process each one...use formatter for this
		"""Process the file passed to the command line and separate
		into groups. 
		@param path: the file path containing the groups
		@param group_name: the generic group_name for the groups""" 
		all_groups = open(all_groups_path, 'a')
		groups_created = ""
		text = ""
		with open(path, 'r+') as fin:
			grouped_file = self.process_path(path)
			with open(grouped_file, "w") as fout:
				for line in fin:
					if not line == "\n":
						line = " * {0}".format(line)
						text += line
					elif line == "\n":
						name = self.get_group_name(group_name)
						group_created = self.create_group_page(name, text)
						if group_created == 0:
							groups_created += " * [[{0}]]\n".format(name)
							string_to_write= '{0}{1}{0}'.format(self.format_string, name)
							fout.write('{0}{1}'.format(string_to_write, text))
							all_groups.write('{0}{1}'.format(string_to_write, text))
						text = ""
		all_groups.close()
		return groups_created

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

						#need to update all groups file
								
						#create_group_page(name, members)
						#write_to_group_file(name, members)

	#Create groups ---> default text file? command line...is it necessary ---> naming...default add to user number, otherwise provide names in file ----> project pages as well?
	#Remove groups ---> must flag with text-file, command line arguments or all  ???Is this a user group? default command line arguments

	#Specify options first on the command line
	def __init__(self):
		import argparse
		self.request = ScriptContext() 	
		self.parser = argparse.ArgumentParser()
		self.parser.add_argument(dest="filenames", help="the names of the files storing the groups to be modified", nargs='*')
		self.args = self.parser.parse_args()

	def command_line_processing(self):
		if not self.args.filenames:
			print "Must specify a path to a file containing modified groups"
		modify = 1
		for fname in self.args.filenames:
			modify_groups(fname)

	def run(self): 
		self.request.user.may = isRoot()
		self.command_line_processing()

	def format_members(self, members):
		formatted_members = [" * {0}".format(member) for member in members]
		return formatted_members

if __name__ == "__main__":
	command = AccessingGroups()
	command.run()

	# Read the file
	# Store the 
