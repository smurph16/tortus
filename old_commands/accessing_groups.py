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

	def create_single_group(self, members, group_name="default"):
		"""Process members specified in command line to create a single group_name
		@param members: the members to be added to the group
		@param group_name: the name of the group to be created (Default: [0-9]+Group)""" 
		text = ""
		for member in members:
			line = " * {0} \n".format(member)
			text += line
		if group_name == "default":
			name = self.get_group_name(group_name)
		else:
			name = '{0}Group'.format(group_name)
		# if not group_name == "default":
		# 	name = "{0}Group".format(group_name)
		# else:	
		# 	name = "{0}Group".format(group_count()+1)
		group_created = self.create_group_page(name, text)
		if group_created == 0:
			self.write_to_group_file(name, text)

	def write_to_group_file(self, name, text):
		"""Add group to all groups file
		@param: the name of the group
		@param the text with the members to be written to the file"""
		with open(all_groups_path, 'a') as all_groups:
			string_to_write = "{0}name{0}".format(self.format_string)
			all_groups.write(string_to_write)
			all_groups.write(text)

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

	# if no file paths are provided, prompt for one
	def process_path(self, path):
		"""Return a path to a record of the created groups_created
		@param path: the text file containing the groups"""
		(file_name, file_extension) = os.path.splitext(path)
		file_name = "{0}_grouped{1}".format(file_name, file_extension)
		grouped_file = os.path.join(os.path.dirname(os.path.abspath(path)), file_name)
		return grouped_file

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
		self.parser.add_argument("--create_group", help="signify that you want to create a group", action="store_true")
		self.parser.add_argument("--project_name", help="the name of the project groups are being created for")
		self.parser.add_argument("-all", "--clear_all_groups", help="delete all user groups", action="store_true")
		self.parser.add_argument("--remove_group", help="delete groups specified. Default is given from command line", action="store_true")
		#parser.add_argument("-u", "--user", help="specify that a user group is being manipulated", action="store_true")
		#parser.add_argument("-a", "--admin", help="specify that an admin group is being manipulated", action="store_true")
		self.parser.add_argument("--modify_group", help="change the construction of the groups", action="store_true")
		self.parser.add_argument("--group_name", help="the name of the group to create, delete or modify", action="store", nargs="*")
		self.parser.add_argument("--member_names", help="members of the group to be added, deleted or modified", nargs='*', action="store")
		self.parser.add_argument(dest="filenames", help="the names of the files storing the groups to be modified", nargs='*')
		self.parser.add_argument("--createProjectPage", help="if a page should be created for each group....specify template?")
		self.parser.add_argument("--categorise", help="if a group should be created containing the new groups", action="store")
		self.parser.add_argument("--prefix", help="a prefix for naming groups") #should this be handled by categorise?
		self.args = self.parser.parse_args()


	def command_line_processing(self):
		#print "Create_group: %d" % args.create_group
		#print "Remove_all_groups: %d" % args.clear_all_groups
		#print "Remove_group: %d" % args.remove_group
		#print "Modify_group: %d" % args.modify_group
		#print "Group_Name: %s" % args.group_name
		#print "Prefix: %s" % args.prefix
		#print args.filenames
		#print args.member_names

	    # One of create, modify or delete must be specified
		if not (self.args.create_group or self.args.remove_group or self.args.modify_group):
			self.parser.error ("No action requested. Please specify 	--create_group or --remove_group or --modify_group")
			return
	    # Create argument	
		if self.args.create_group:
			from groups.create_group import Groups
			create = Groups()
			create.run()
			# #self.create_group_args(self.args)
	  #   	# Group to be created on command line or with text file
			# if not (self.args.member_names or self.args.filenames):
			# 	self.parser.error("Must specify member names in command line or path to file containing names")
			# 	return	
	  #   	# Store name if default not wanted
			# if self.args.group_name and len(self.args.group_name) > 1:
			# 	print "You can only specify one group name for creating a group"
			# 	return
			# #This is messy...clean it up	
			# elif self.args.group_name:
			# 	name = self.args.group_name[0]
			# 	print "Creating group %s" % name
			# elif not (self.args.group_name or self.args.prefix):
			# 	name = "default"
			# elif self.args.prefix:
			# 	name = self.args.prefix
			# 	print name
			# #create = 1
			# groups_created = ""	
			# for fname in self.args.filenames:
			# 	groups_created += self.process_group_file(fname, name)
			# 	print "processed a_file"
			# if self.args.filenames and self.args.categorise:
			# 	self.create_group_of_groups(self.args.categorise, groups_created)
			# elif self.args.filenames and self.args.prefix:
			# 	self.create_group_of_groups(self.args.prefix, groups_created)
			# if self.args.member_names:
			# 	self.create_single_group(self.args.member_names, name)

	    # Remove argument
		elif self.args.remove_group:
	    	#One of user or admin must be specified
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
			self.create_copy()
	    # Modify argument
		elif self.args.modify_group:
			if not self.args.filenames:
				print "Must specify a path to a file containing modified groups"
			modify = 1
			for fname in self.args.filenames:
				modify_groups(fname)


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

	def group_count(self, pattern):
		"""The number of groups with a particular name pattern
		@param: the pattern of the name"""
		groups = self.request.groups
		count = 0
		for group in groups:
			temp_group = groups.get(group)
			match_obj = pattern.match(temp_group.name)
			if match_obj is not None: 
				if int(match_obj.group(1)) > count:
					count = int(match_obj.group(1))
		return count

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

	def retrieve_members (group_names):
		"""Get the user ids of the members of a list of groups
		@param group_names: the list of groups"""
		groups = self.request.groups
		uIDs= []
		for gname in group_names:
		#returns a list of user ids to add a quick link to
			group = groups.get(gname)
			if group is not None:	
				for member in group:
					uid = user.getUserId(request, member)
					if user.User(request, uid).exists():
						uIDs.append(uid)
					else:
						print ("The user {0} in group {1} does not exist".format(member, group))
			else:
				print "The group {0} does not exist.".format(gname)
		return uIDs

	def get_group_name(self, name):
		"""Determine the next count for a group subset
		@param name: the """
		if name =="default":
			count = self.group_count(re.compile('([0-9]+)Group'))
			return '{0}Group'.format(count+1)
		else:
			count = self.group_count(re.compile('{0}([0-9]+)Group'.format(name)))
			return '{0}{1}Group'.format(name, count+1)

	def create_group_of_groups(self, name, members):
		'''Creates a group page which stores a set of groups for easy handling. A name must be specified for the group.
		Requires categorise flag and must be passed as a file
		@param name: the group category name
		@param members: the groups to be added as members'''
		gname = "{0}Group".format(name)
		if not Page(self.request, gname).exists():
			self.create_group_page(gname, members, 1)
		else:
			text = Page(self.request, gname).get_raw_body()
			text += members
			print PageEditor(self.request, gname).saveText(text, 0)
			print "Edited group file for {0}".format(name)

	def format_members(self, members):
		formatted_members = [" * {0}".format(member) for member in members]
		return formatted_members

if __name__ == "__main__":
	command = AccessingGroups()
	command.run()

	# Read the file
	# Store the 



