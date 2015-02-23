"""Tortus Group Class for accessing groups- adding, modifying and
deleting groups"""

from MoinMoin.web.contexts import ScriptContext
from MoinMoin.Page import Page
from MoinMoin.PageEditor import PageEditor
from default import *
from nat_sort import natsorted
from MoinMoin import user
from tortus_page import TortusPage
import re, os, shutil

class TortusGroup():
	"""Tortus Group Class"""

	def __init__(self, project):
		self.project = project #What project does it belong to...check it exists
		self.request = ScriptContext()

	def create_group_page(self, page_name, members):
		"""Create a group page with the given members and group name
		@param page_name: the name of the page_name
		@param members: members to be added to the group
		@param group: if 1, categorise as group page (default: 0)"""
		#page_name = "{0}/{1}".format(self.project, page_name)
		if Page(self.request, page_name).exists():
			print "A page with the name {0} already exists".format(page_name)
			return 1
		text = "{0}{1}\n[[{2}Project]]".format(get_permissions().get('instructor_read_only'), members, self.project)
		try:
			page_ed = PageEditor(self.request, page_name)
			page_ed.saveText(text, 0)
			return 0
		except page_ed.Unchanged:
			print "Page not changed"
			return 1
	
	def format_members(self, members):
		"""
		Format members for the group page to represent as MoinMoin group
		@param members: a list of the members to format"""
		newline = "\n"
		formatted_members = [" * {0}".format(member) for member in members]
		return newline.join(formatted_members)

	def group_count(self, pattern): # Should I be checking the generic groups?
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

	def retrieve_members (self, group_names):
		"""Get the user ids of the members of a list of groups
		@param group_names: the list of groups"""
		groups = self.request.groups
		uIDs= []
		for gname in group_names:
		#returns a list of user ids to add a quick link to
			group = groups.get(gname)
			if group is not None:	
				for member in group:
					uid = user.getUserId(self.request, member)
					if user.User(self.request, uid).exists():
						uIDs.append(uid)
					else:
						print ("The user {0} in group {1} does not exist".format(member, group.name))
			else:
				print "The group {0} does not exist.".format(gname)
		return uIDs

	def get_group_name(self, name):
		"""Determine the next count for a group subset
		@param name: the group pattern to be counted"""
		if name =="default":
			count = self.group_count(re.compile('^([0-9]+)Group'))	
			return '{0}Group'.format(count+1)
		elif name == self.project:
			count = self.group_count(re.compile('{0}Project\/([0-9]+)Group'.format(self.project)))
			return '{0}Project/{1}Group'.format(self.project, count+1) #{0}Project
		else:
			if re.search('(\d+)$', name) is not None:
				return '{0}Project/{1}Group'.format(self.project, name)
			count = self.group_count(re.compile('{0}Project\/{1}([0-9]+)Group'.format(self.project, name)))
			return '{0}Project/{1}{2}Group'.format(self.project, name, count+1)

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
			PageEditor(self.request, gname).saveText(text, 0)
			print "Edited group file for {0}".format(name)

	#list comprehension for group file
	def process_group_file(self, path):
	# if file path/paths are provided, process each one...use formatter for this
		"""Process the file passed to the command line and separate
		into groups. Note: You must have a newline at the end of the file. Add one?
		@param path: the file path containing the groups
		@param group_name: the generic group_name for the groups""" 
		#project_groups = with open(all_groups_path, 'a') 
		#groups_created = ""
		#text = ""
		members = []
		groups = []
		try:
			with open(path, 'r+') as fin:
			#grouped_file = self.process_path(path)
			#with open(grouped_file, "w") as fout:
				for line in fin:
					if not line == "\n":
						members.append(line.strip())
						#text += line
					elif line == "\n":
						groups.append(members)
						members = []
		except IOError:
			print "The file at {0} could not be found ".format(path)
			return
		return groups

	def process_delete_group_file(self, path):
		"""Processes a file containing one group to be deleted on each line
		@param path: """
		groups = []
		try:
			with open(path, 'r+') as fin:
				for line in fin:
					groups.append(line.strip())
		except IOError:
			print "The file could not be found"
			return
		return groups

	def process_modified_group_file(self, path):
		"""Process a file containing groups which may have been modified or deleted"""
		groups = {}
		try:
			with open(path, 'r') as fin:
				f_pattern = re.compile('#-{40}\n.+\n-{41}[^#----------]*', re.M)
				matches = re.findall(f_pattern, fin.read())
				if matches:
					for group in matches:
						previous_line = ""
						revised_members = []
						for line in group.split('\n'):
							if previous_line.startswith("#-------------------"):
								name = line
								previous_line = "done"
								continue
							elif not previous_line == "done":
								previous_line = line
							member_pattern = re.compile("^[a-zA-Z0-9@.]+$")
							if re.match(member_pattern, line):
								revised_members.append(line)
						groups[name] = revised_members
		except IOError:
			print "The file could not be found"
		return groups

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

	def repr_groups(self, groups):
		"""Create representation of group name and members to display to user
		@param groups: a dictionary containing group_names as keys and group_members in a list as values"""
		format_string = '----------------------------------------'
		newline = "\n"
		text = ""
		for group_name in natsorted(groups.keys()):
			text += "\n#{0}\n{1}\n-{0}\n{2}\n".format(format_string, group_name, newline.join(groups[group_name]))
		return text

	def create_groups(self, groups, name, project, projects): #Groups is a dictionary with key name and value members as a list
		"""Creates group for a specific project
		@param groups: a data structure containing the groups to be added. Dictionary if names are already specified, list of lists of members
		otherwise
		@param name: name pattern for group(s) if name is not set
		@param project: the project to add the groups
		@param projects: collection of all projects"""
		group_dict = {}
		created_groups = {}
		failed_groups = []
		for group in groups:
			if name != "":
				moin_group_name = self.get_group_name(name) #List being passed in
				formatted_members = self.format_members(group)
			else:
				moin_group_name = self.get_group_name(group) #Dict being passed in 
				formatted_members = self.format_members(groups[group])
			created_page = self.create_group_page(moin_group_name, formatted_members)
			if created_page == 1 and name == "":
				failed_groups.append(group)
			elif created_page == 1:
				failed_groups.append(self.get_user_group_name(moin_group_name))
			elif created_page == 0 and name == "":
				created_groups[group] = groups[group]
			else:
				created_groups[self.get_user_group_name(moin_group_name)] = group
		for group in created_groups:
			project.groups.update(created_groups)
		project.write_project_group_file()
		projects.update_groups(project, 'groups') #Why doesn't this work?
		self.create_print_actions(created_groups, failed_groups)

	def create_print_actions(self, created_groups, failed_groups):
		"""Print created and failed groups to the command line
		@param: created_groups: dictionary of created groups
		@param: failed_groups: list of groups that were not created"""
		for group in failed_groups:
			print "Failed to create group {}".format(group)
		if created_groups:
			text = "Created the following groups: "
		#print len(created_groups)
			text += self.repr_groups(created_groups)
			print text

	def delete_groups(self, groups, project, projects):
		"""Delete groups from a specific project
		@param groups: a list of groups to be deleted
		@param project: the project to delete the groups from
		@param projects: the collection of projects"""
		deleted_groups = []
		failed_groups = []
		for group in groups:
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
		self.delete_print_actions(deleted_groups, failed_groups)

	def remove_group(self, name): #This should be hidden?
		"""Remove a single group page from the MoinMoin wiki
		@param name: the MoinMoin page name of the group to be deleted"""
		#Find the group files....could do this with PageEditor(request, pagename).deletePage()
		# """Remove a single group from the pages directory
		# @param name: the name of the group to be removed"""
		group_page_path = os.path.join(data_folder, 'pages', re.sub('/', '(2f)', name))
		if os.path.exists(group_page_path):
			shutil.rmtree(group_page_path) #Tortus Page delete option?
			return 0
		else: 
		 	return 1
		
	def delete_print_actions(self, deleted_groups, failed_groups):
		"""Print deleted and failed groups to the command line
		@param: deleted_groups: list of deleted groups
		@param: failed_groups: list of groups that were not deleted"""
		for group in failed_groups:
			print "Failed to remove group {0}".format(group)
		for group in deleted_groups:
			print "Deleted group with name {0}".format(group)

	def modify_page(self, page_name, members): #Hidden as well
		#Should I be just removing a group and adding a group or should I modify the text???
		"""Modify a page to containg different users. This changes the groups in the MoinMoin backend
		@param: page_name: the MoinMoin page_name of the page to be modified
		@param: members: the new members to be stored on the page"""
		page = Page(self.request, page_name)
		if page.exists():
			if page.get_meta():
				acl = page.get_meta()[0][1]
			text = "#{0}{1}\n[[{2}]]".format(acl, self.format_members(members), self.project)
			# try
			page_ed = PageEditor(self.request, page_name)
			page_ed.saveText(text, 0)
			return 0
			# except page_ed.Unchanged:
			# 	print "Page not changed"
			# 	return 1
	
	def modify_groups(self, groups, project, projects):
		"""Modify groups from a specific project
		@param groups: a dictionary of groups to be modified. Keys contain group names. Values contain list of group members
		@param project: the project to modify the groups from
		@param projects: the collection of projects"""
		modified_groups = {}
		failed_groups = []
		for group, members in groups.iteritems():
			moin_name = self.get_moin_name(project.name, group)
			modified = self.modify_page(moin_name, members)
			if modified == 1:
				failed_groups.append
			else:
				modified_groups[group] = members
		for group in modified_groups:
			project.groups[group] = modified_groups[group]
		project.write_project_group_file()
		projects.update_groups(project, 'groups')
		self.modify_print_actions(modified_groups, failed_groups)

	def modify_print_actions(self, modified_groups, failed_groups):
		"""Print modified and failed groups to the command line
		@param: modified_groups: dictionary of modified groups
		@param: failed_groups: list of groups that were not modified"""
		for group in failed_groups:
			print "Failed to remove group {0}".format(group)
		for group, members in modified_groups.iteritems():
			print "Modified group {0} with members {1}".format(group, members)

	def get_moin_name(self, project, name):
		"""Maps the user's(change this) page name to the MoinMoin page name for page editing
		@param name: the user's name for the group"""
		return "{0}Project/{1}Group".format(project, name)

	def get_user_group_name(self, moin_name):
		"""Maps the MoinMoin page name to the user's name for the group
		@param moin_name: the MoinMoin page name"""
		pattern = re.compile(".+Project/([a-zA-Z0-9]+)Group")
		match = pattern.match(moin_name)
		if match:
			return match.group(1)
		else:
			return moin_name


# my_group = TortusGroup('pro')
# groups_dict = my_group.process_modified_group_file('/usr/local/share/moin/tortus/examples/modified_group_file.txt')
# print groups_dict