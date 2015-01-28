from MoinMoin.web.contexts import ScriptContext
from MoinMoin.PageEditor import PageEditor
from MoinMoin.Page import Page
from MoinMoin.datastruct.backends import wiki_dicts #take this import away
from default import *
from MoinMoin import user, wikiutil
from MoinMoin.user import User, getUserList
from urlparse import urlparse
import os.path
import argparse


class TortusPage(object): # inherit from Page?
	"""Tortus - Page class
	This class is used for manipulation and creation of user pages. It does
	something"""
	def __init__(self):
		self.request = ScriptContext()

	def add_from_file(self, file_path, project, name, ctx, perm=""):
		"""Add a new page to the moinmoin wiki from a file
		@param file_path: the file to create the page from
		@param name: the name of the page to be created
		@param ctx: the type of page to be added. One of 'user' or 'organisation'
		@param perm: permissions for the page""" #Do I need this?
		name = "{0}Project/{1}".format(project.name, name)
		if Page(self.request, name).exists(): #should use isUnderlayPage/isDataPage
			print "A page with the name {0} already exists".format(name)
			return 1 #Need name here but doesn't give correct permissions. Could pass them in here?
		try:
			with open (file_path) as f:
				text = "{0}\n".format(perm)
				text += f.read()
				text += "\n<<Navigation(children)>>"
				PageEditor(self.request, name).saveText(text, 0)
				print "A page was created with the name {0}".format(name)
				return 0
		except IOError:
			print "The file {0} could not be found in the location specified. Please check that the file is in the pages folder".format(name)
			return 1

	def process_url_page(self, args):
		"""Create a quick link for a page created in the browser
		@param args: command line arguments"""
		wiki_data = os.path.basename(os.path.dirname(data_folder))
		url_parts = urlparse(args.url)
		page_name = (url_parts[2].rpartition(wiki_data + '/')[2]).rsplit('/')
		string = '(2f)' # magic number
		page_name = string.join(page_name)
		if not Page(self.request,page_name).exists():
			print "The url you have provided is not a page that has already been created"
			return
		permissions = get_permissions()
		text = "{0}\n".format(permissions.get(args.permissions, 'read_only'))
		#print "this is it" + text 
		text += Page(self.request, page_name).get_raw_body()
		print text
		print PageEditor(self.request, page_name).saveText(text, 0)
		process_user_link(page_name, args)

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
		if not u.isQuickLinkedTo(page_name):
			u.addQuicklink(page_name)

	def delete_page(self, name):
		#Delete from project file
		#Delete from MoinMoin record
		#Delete from json project file
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
			print "Page for %s already exists or account is disabled or user does not exist." % account.name

	def get_page_path(self, account_name, project_name, page_name):
		#This is where I would get some page path
		page_path = "{0}/{1}".format(account_name, page_name)
		return page_path


