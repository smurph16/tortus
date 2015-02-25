from MoinMoin.web.contexts import ScriptContext
from MoinMoin.PageEditor import PageEditor
from MoinMoin.Page import Page
from MoinMoin.datastruct.backends import wiki_dicts #take this import away
from default import *
from MoinMoin import user, wikiutil
from MoinMoin.user import User, getUserList
from urlparse import urlparse
import os.path, argparse, re


class TortusPage(object): # inherit from Page?
	"""Tortus - Page class
	This class is used for manipulation and creation of user pages"""
	def __init__(self):
		self.request = ScriptContext()

	def add_from_file(self, file_path, project, name, ctx, perm=""):
		"""Add a new page to the moinmoin wiki from a file
		@param file_path: the file to create the page from
		@param name: the name of the page to be created
		@param ctx: the type of page to be added. One of 'user' or 'organisation'
		@param perm: permissions for the page""" #Do I need this?
		if Page(self.request, name).exists(): #should use isUnderlayPage/isDataPage
			print "A page with the name {0} already exists".format(name)
			return 1 #Need name here but doesn't give correct permissions. Could pass them in here?
		if ctx == 'url':
			#try: 
			text  = "{0}\n".format(perm)
			text += Page(self.request, self.get_moin_name(file_path)).get_raw_body()
			PageEditor(self.request, name).saveText(text, 0)
			print "A page was created with the name {0}".format(name)
			return 0
		else:
			try:
				with open (file_path) as f:
					text = "{0}\n".format(perm)
					text += f.read()
					PageEditor(self.request, name).saveText(text, 0)
					print "A page was created with the name {0}".format(name)
					return 0
			except IOError:
				print (
					"The file {0} could not be found in the location specified. The file should be in the pages folder".format(file_path)
					)
				return 1

	def process_url(self, url, project, permissions, name, acls):
		'''''Creates the page from a url
		@param url: the url of the page to be copied
		@param project: the project to add the page to
		@param name: the name of the new page
		@param acls: a dictionary with users or group keys and permission values '''
		if permissions == 'default':
			perm = get_permissions().get('read_only') #Read only
		else: 
			perm = get_permissions().get(permissions, 'read_only') 
		wiki_data = os.path.basename(os.path.dirname(data_folder))
		url_parts = urlparse(url)
		page_name = (url_parts[2].rpartition(wiki_data + '/')[2]).rsplit('/')
		file_string = '(2f)'
		file_name = file_string.join(page_name)
		file_path = os.path.join(data_folder,'pages',file_name)
		if acls:
			self.distribute_page(project, name, file_path, acls)
		else:
			self.page.add_from_file(file_path, project, name, 'url', perm)
		page_link = '/'.join(page_name)
		if not Page(self.request, page_link).exists():
		    print "The url you have provided is not a page that has already been created"

	def template(self, template, permissions, project, name, acls = {}):	
		'''''Creates the page from a template
		@param template: the name of the page to be copied
		@param project: the project to add the page to
		@param name: the name of the new page
		@param acls: a dictionary with users or group keys and permission values '''
		if permissions == 'default':
			perm = get_permissions().get('read_only')
		else: 
			perm = get_permissions().get(permissions, 'read_only') 
		file_path = self.page.get_file_path(template, template=1)
		if acls:
			self.distribute_page(project, name, file_path, acls)
		else:
			self.page.add_from_file(file_path, project, get_name(project.name, name).get('generic_project_page'), 'user', perm)      
	
	def filenames(self, filenames, permissions, project, name="", acls= {}):
		'''Creates a page from a file
		@param filenames: the files that the pages should be created from
		@param project: the project to add the page to
		@param name: the name of the new page. Default extracts name from filename
		@param acls: a dictionary containing users or groups and the corresponding permissions'''
		for fname in filenames:
			if name is None:
				name = os.path.splitext(fname)[0]
			file_path = self.page.get_file_path(fname, file=1)
			if acls: #Fix this
				self.distribute_page(project, name, file_path, acls)
			else:
				if permissions == 'default':
					perm = get_permissions("").get('read_only')
				else: 
					perm = get_permissions("").get(permissions, 'read_only') 
				self.page.add_from_file(file_path, project, get_name(project.name, name).get('generic_project_page'), 'user', perm)

	def user_copy(self, acls, project, page_name, file_path, url=0):
		"""Creates a copy of a page for each user in members
		@param members: a list of members a copy should be made for
		@param project: the project the page should be created for
		@param page_name: the name of the page to be copied
		@param file_path: the path to the page to be copied"""
		if acls:
			for member in acls:
				perm = acls.get(member)
				pg_name = get_name(project.name, page_name, user_name=member).get('student_project_page')
				if url == 1:
					self.add_from_file(file_path, project, pg_name, 'url', perm)
				else:
					self.add_from_file(file_path, project, pg_name, 'file', perm)
#successful 
#failed

	def group_copy(self, acls, project, page_name, file_path, url=0):
		"""Creates a copy of a page for each group in accounts 
		@param accounts: a list of groups a copy should be created for
		@param project: the project the page should be created for
		@param page_name: the name of the page to be copied
		@param file_path: the path of the page to be copied"""
		for group in acls:
			perm = acls.get(group)
			pg_name = get_name(project.name, page_name, group_name=group).get('student_group_page')
			if url == 1:
				self.add_from_file(file_path, project, pg_name, 'url', perm)
			else:
				self.add_from_file(file_path, project, pg_name, 'file', perm)

	def generic_copy(self, project, page_name):
		"""Displays the text on generic pages in an individuals path"""
		successful = []
		failed = []
		p = get_permissions()
		permissions = p.get('read_only')
		text = permissions
		text += "<<Include({0})>>".format(page_name)
		for name in project.get_members():
			pg_name = self.get_page_path(name, project.name, page_name)
			if Page(self.request, pg_name).exists():
				failed.append(name) 
			else:
				PageEditor(self.request, pg_name).saveText(text, 0)
				print "A page was created with the name {0}".format(pg_name)
				successful.append(name)

	def distribute_page(self, project, page_name, file_path, acls, homepage=0):
		# Checks for a template page and sets homepage_default_text
		"""Creates a copy of a page for each user or group
		@param project: the project the page and users belong to
		@param page_name: the name of the page that will be added for each user
		@param file_path: the path to the file or template containing the contents of the page
		@param homepage: set to 1 if the page will be the homepage for a user"""
		if self.args.user_names or self.args.show_to_all:
			self.user_copy(acls, project, page_name, file_path, homepage)
		elif self.args.group_names:
			for group in self.args.group_names:
				group_name = get_name(project.name, page_name, group_name=group).get('student_group_page')
				temp_group = self.request.groups.get(get_name(project.name, page_name, group_name=group).get('instructor_group_page'))
				if (temp_group and temp_group.member_groups):
					acls.extend({(group, get_permissions(group_name=temp_group.name).get('group_write_only')) for group in temp_group.member_groups})
					acls.pop(group)
			self.group_copy(acls, project, page_name, file_path)
		if not acls:
			print "No accounts selected for copy of page!"
			return

	def get_file_path(self, name, file=0, template=0):
		"""Retrieve the file from the pages_directory
		@param name: the name of the file to retrieve
		@param file: Set to 1 if the page is a custom page 
		@param template: Set to 1 if the page is a template"""
		file_path = ""
		if file == 1:
			file_path = os.path.join(page_path, name)
		if template == 1:
			file_path = os.path.join(template_path, name)
		return file_path

	def add_quick_link(self, uid, page_name):
		#group pages added by default
		#command line arguments
		"""Add a quick link to a user's task-bar
		@param uid: the user id of the user
		@page_name: the name of the page to add quicklink to"""
		u = user.User(self.request, uid)
		if not u.isQuickLinkedTo(page_name) and Page(self.request, page_name).exists():
			u.addQuicklink(page_name)

	def remove_quick_link(self, uid, page_name):
		"""Remove a quick link from a user's task-bar
		@param uid: the user id of the user
		@page_name: the name of the page to remove a quicklink from"""
		u = user.User(self.request, uid)
		if u.isQuickLinkedTo(page_name):
			u.removeQuickLink(page_name)

	def delete_page(self, name):
		if not Page(self.request, name).exists(): #should use isUnderlayPage/isDataPage
			print "A page with the name {0} doesn't exist".format(name)
			return 1
		PageEditor(self.request, name).deletePage()
		return 0

	def write_homepage(self, account, project_name, homepage_text):
	# writes the homepage
		homepage = "{0}/{1}".format(project_name, account.name)
		if account.exists() and not account.disabled and not Page(self.request, homepage).exists(): #account exists?
			userhomepage = PageEditor(self.request, homepage)
			try:
				userhomepage.saveText(homepage_text, 0)
				print "Central page created for %s." % account.name
			except userhomepage.Unchanged:
				print "You did not change the page content, not saved!"
			except userhomepage.NoAdmin:
				print "You don't have enough rights to create the %s page" % account.name
		else:
			print """Page for %s already exists or account is disabled or
			user does not exist.""" % account.name

	def get_page_path(self, account_name, project_name, page_name):
		#This is where I would get some page path
		page_path = "{0}/{1}".format(account_name, page_name)
		return page_path

	def get_moin_name(self, name):
		return re.sub('\(2f\)', '/', name)

	def process_user_ids(self, project, args):
		"""Add a link in the users task-bar to a specific page
		@param page_name: the name of the page to add a quick link to
		@args: command line arguments"""
		user_ids = None
		if args.all:
			user_ids = user.getUserList(self.request)
		elif args.group_names:
			group_names = [TortusGroup(project).get_moin_name(group) for group in args.group_names]
			user_ids = self.group_obj.retrieve_members(group_names) #Retrieve members is in groups
		elif args.user_names:
			user_ids =[user.getUserId(self.request, member) for member in args.user_names] 
		elif args.project:
			user_ids = [user.getUserId(self.request, member) for member in project.get_members()]
		return user_ids

	def add_link(self, user_ids, pages, project):
		for uid in user_ids:
			if user.User(self.request, uid).exists():
				for page in pages:
					page = self.page_name(page, project)
					self.add_quick_link(uid, page)

