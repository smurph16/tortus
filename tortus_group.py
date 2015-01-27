"""Tortus Group Class for accessing groups- adding, modifying and
deleting groups"""

from MoinMoin.web.contexts import ScriptContext
from MoinMoin.Page import Page
from MoinMoin.PageEditor import PageEditor
from default import *
from nat_sort import natsorted
import re

class TortusGroup():

	def __init__(self, project):
		#Are their variables?
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
		@param name: the group pattern to be counted"""
		if name =="default":
			count = self.group_count(re.compile('([0-9]+)Group'.format))
			return '{0}Group'.format(count+1)
		else:
			count = self.group_count(re.compile('{0}Project\/([0-9]+)Group'.format(self.project)))
			return '{0}Project/{1}Group'.format(self.project, count+1) #{0}Project

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
			print "The file could not be found"
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


		# 				name = self.get_group_name(group_name)
		# 				group_created = self.create_group_page(name, text)
		# 				if group_created == 0:
		# 					groups_created += " * [[{0}]]\n".format(name)
		# 					string_to_write= '{0}{1}{0}'.format(self.format_string, name)
		# 					fout.write('{0}{1}'.format(string_to_write, text))
		# 					all_groups.write('{0}{1}'.format(string_to_write, text))
		# 				text = ""
		# all_groups.close()
		# return groups_created

	# if no file paths are provided, prompt for one

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

	# def _natural_sort(l):
	# 	"""returns the natural sorting order of a list"""
	# 	convert = lamba text: int(text) if text.isdigit() else text.lower()
	# 	alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
	# 	return sorted (1, key = alphanum_key)  

	def repr_groups(self, groups):
		format_string = '----------------------------------------'
		newline = "\n"
		text = ""
		for group_name in natsorted(groups.keys()):
			text += "\n#{0}\n{1}\n-{0}\n{2}\n".format(format_string, group_name, newline.join(groups[group_name]))
		return text

	def create_groups(self, groups, name, project, projects): #Groups is a dictionary with key name and value members as a list
		"""creates groups """
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
				print self.get_user_group_name(moin_group_name)
				failed_groups.append(self.get_user_group_name(moin_group_name))
			elif created_page == 0 and name == "":
				created_groups[group] = groups[group]
			else:
				created_groups[self.get_user_group_name(moin_group_name)] = group
		#project = projects.tortus_project(# This is due to changing the name to Boo Project...need to add a method
		for group in created_groups:
			project.groups.update(created_groups)
		project.write_project_group_file()
		projects.update_groups(project, 'groups') #Why doesn't this work?
		self.create_print_actions(created_groups, failed_groups)
		#Write to json file

	def create_print_actions(self, created_groups, failed_groups):
		for group in failed_groups:
			print "Failed to create group {}".format(group)
		text = "Created the following groups: "
		#print len(created_groups)
		text += self.repr_groups(created_groups)
		print text

	def delete_groups(self, groups, project, projects):
		deleted_groups = []
		failed_groups = []
		for group in groups:
			name = "{0}/{1}".format(project.name, group) #May need to map here as well to a separate function
			#Map to MoinMoin name
			moin_name = self.get_moin_name(name)
			# Remove the group from the MoinMoin wiki
			removed = self.remove_group(moin_name)
			if removed == 1:
				failed_groups.append(name)
			else:
				deleted_groups.append(name)
		for group in deleted_groups:
			name = group.decode('utf-8')
			project.groups.pop(name)
		projects.update() #Remove access to projects //Could run in command script
		self.delete_print_actions(deleted_groups, failed_groups)

	def remove_group(self, name):
		#Find the group files....could do this with PageEditor(request, pagename).deletePage()
		# """Remove a single group from the pages directory
		# @param name: the name of the group to be removed"""
		# group_page_path = os.path.join(data_folder, 'pages', name)
		# if os.path.exists(group_page_path):
		# 	shutil.rmtree(group_page_path)
		# 	return 0
		# else: 
		# 	return 1 ????implementation choice
		print name
		pg_obj = TortusPage()
		pg_obj.delete_page(name)

	def delete_print_actions(self, deleted_groups, failed_groups):
		for group in failed_groups:
			print "Failed to remove group {0}".format(group)
		for group in deleted_groups:
			print "Deleted group with name {0}".format(group)

	def modify_page(self, page_name, members):
		#Should I be just removing a group and adding a group or should I modify the text???
		page = Page(self.request, page_name)
		if page.exists():
			acl = page.getACL(self.request)
			print acl
			text = "{0}{1}\n[[{2}]]".format(acl, members, self.project)
			try:
				page_ed = PageEditor(self.request, page_name)
				page_ed.saveText(text, 0)
				return 0
			except page_ed.Unchanged:
				print "Page not changed"
				return 1
	
	def modify_groups(self, groups, project, projects):
		modified_groups = {}
		failed_groups = []
		for group, members in groups.iteritems():
			moin_name = self.get_moin_name(group)
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
		for group in failed_groups:
			print "Failed to remove group {0}".format(group)
		for group, members in modified_groups.iteritems():
			print "Modified group {0} with members {1}".format(group, members)

	def get_moin_name(self, name):
		return "{0}/{1}".format(self.project, name)

	def get_user_group_name(self, moin_name):
		pattern = re.compile(".+Project/([a-zA-Z0-9]+)Group")
		match = pattern.match(moin_name)
		return match.group(1)


# my_group = TortusGroup('pro')
# groups_dict = my_group.process_modified_group_file('/usr/local/share/moin/tortus/examples/modified_group_file.txt')
# print groups_dict