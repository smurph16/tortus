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

	def print_actions(self, group_obj, created_groups, failed_groups):
		for group in failed_groups:
			print "Failed to create group {}".format(group)
		text = "Created the following groups: \n"
		#print len(created_groups)
		group_obj.repr_groups(created_groups)
		text += group_obj.repr_groups(created_groups)
		print text

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

		name = None
		if not (self.args.filenames or self.args.template or self.args.url):
			self.parser.error ("Please specify a file, url or a template to create a page from")
			return
		if not (self.args.permissions):
			 default_permissions = raw_input("The permissions for this file will be set to default values. Press Y to continue or any other key to halt program\n")
			 if default_permissions == 'Y':
			 	p = get_permissions()
			 	permissions = p.get('read_only')
			 else:
			 	print "Permissions can be set using the --permissions flag. See --help for more information"
			 	return
		else:
			permissions = self.args.permissions
		#This is messy. Tidy it up
		if (self.args.filenames and self.args.template) or (self.args.filenames and self.args.url) or (self.args.url and self.args.template):
			self.parser.error("You can only specify a filename, a template or a url")
			return
		if not (self.args.filenames or self.args.page_name or self.args.url):
			name = raw_input("Please specify a page name: ")
		elif self.args.page_name:
			name = args.page_name
		#elif args.group_names:
			#check execution was completed
			#find group
			#retrieve members
			#call quicklinks
		if self.args.project:
			project_name = self.args.project
		else:
			default_project = raw_input("This page will belong to the project DefaultProject. Please Y to proceed or any other key to cancel: ")
			if not default_project == "Y":
				return
			project_name = "default"
		projects = TortusProjectCollection()
		if not (projects.project_exists(project_name) == 0): #Make the project if it doesn't exist
			mk_prj = raw_input("This project does not exist yet. If you would like to create it, please Y to proceed or any other key to cancel: ")
			if mk_prj == 'Y':
				project = projects.tortus_project(name =project_name, groups={}, args=self.args)
			else:
				return
		else:
			project = projects.tortus_project(name=project_name, groups={}, args=self.args) #This is a retrieval step...initialises it with existing data
		group_obj = TortusGroup(project.name)
		if self.args.template:
			template = self.args.template
			file_path = self.page.get_file_path(template, template=1)
			if self.args.central_page:
				self.central_page(project, name, file_path)
			else:
				self.page.add_from_file(file_path, project, name, 'user', permissions)		
		elif self.args.filenames:
			for fname in self.args.filenames:
				if name is None:
					name = os.path.splitext(fname)[0]
				file_path = self.page.get_file_path(fname, file=1)
				if self.args.central_page:
					self.central_page(project, name, file_path)
				else:
					self.page.add_from_file(file_path, project, name, 'user', permissions)
		elif self.args.url:
			self.page.process_url_page(self.args)



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