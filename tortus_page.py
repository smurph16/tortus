from MoinMoin.web.contexts import ScriptContext
from MoinMoin.PageEditor import PageEditor
from MoinMoin.Page import Page
from MoinMoin.datastruct.backends import wiki_dicts #take this import away
from accessing_groups import AccessingGroups
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

	def add_from_file(self, file_path, args, name, ctx):
		"""Add a new page to the moinmoin wiki from a file
		@param file_path: the file to create the page from
		@param args: the command line arguments
		@param name: the name of the page to be created
		@param ctx: the type of page to be added. One of 'user' or 'organisation'"""
		if Page(self.request, name).exists(): #should use isUnderlayPage/isDataPage
			print "A page with the name {0} already exists".format(name)
			return 1
		try:
			print file_path
			with open (file_path) as f:
				permissions = get_permissions() #??why did i put name here
				print args
				text = "{0}\n".format(permissions.get(args.permissions, 'instructor_read_only'))
				print text
				text += f.read()
				print PageEditor(self.request, name).saveText(text, 0)
				print "A page was created with the name {0}".format(name)
				if ctx == 'user':	
					self.process_user_ids(name, args)
				return 0
		except IOError:
			print "The file {0} could not be found in the location specified. Please check that the file is in the pages folder".format(name)
			return 1

	def process_user_ids(self, page_name, args): #args is 
		"""Add a link in the users task-bar to a specific page
		@param page_name: the name of the page to add a quick link to
		@args: command line arguments"""
		user_ids = None
		if args.show_to_all:
			user_ids = getUserList(self.request)
		elif args.group_names:
			user_ids = retrieve_members(args.group_names)
		if user_ids is not None:
			for uid in user_ids:
				add_quick_link(uid, page_name)

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
		PageEditor(self.request, name).deletePage

	

