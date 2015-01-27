from MoinMoin.web.contexts import ScriptContext
request = ScriptContext()
from MoinMoin.PageEditor import PageEditor
from MoinMoin.Page import Page
from MoinMoin.datastruct.backends import wiki_dicts
from accessing_groups import AccessingGroups
from authorisation import login
from default import *
from MoinMoin import user, wikiutil
from MoinMoin.user import User, getUserList
from urlparse import urlparse
import os.path
import argparse


current_directory = os.path.dirname(os.path.abspath(__file__))
print current_directory
pages_directory = os.path.join(current_directory, 'pages')

def add_new_page(file_path, args, name): #args is too generic
	#Read from file, process text and create the page....add to pages?
	"""Add a new page to the moinmoin wiki
	@param file_path: the file to create the page from
	@param args: the command line arguments
	@param name: the name of the page to be specified"""
	if Page(request, name).exists(): #should use isUnderlayPage/isDataPage
		print "A page with the name {0} already exists".format(name)
		return 1
	try:
		with open (file_path) as f:
			permissions = get_permissions(name) #??why did i put name here
			text = "{0}\n".format(permissions.get(args.permissions, 'read_only'))
			print text
			text += f.read()
			print PageEditor(request, name).saveText(text, 0)
			print "A page was created with the name {0}".format(name)
			process_user_ids(name, args)
			return 0
	except IOError:
		print "The file {0} could not be found in the location specified. Please check that the file is in the pages folder".format(name)
		return 1

def process_user_link(page_name, args): #args is 
	"""Add a link in the users task-bar to a specific page
	@param page_name: the name of the page to add a quick link to
	@args: command line arguments"""
	user_ids = None
	if args.show_to_all:
		user_ids = getUserList(request)
	elif args.group_names:
		user_ids = retrieve_members(args.group_names)
	if user_ids is not None:
		for uid in user_ids:
			add_quick_link(uid, page_name)

def process_url_page(args):
	"""Create a quick link for a page created in the browser
	@param args: command line arguments"""
	wiki_data = os.path.basename(os.path.dirname(data_folder))
	url_parts = urlparse(args.url)
	page_name = (url_parts[2].rpartition(wiki_data + '/')[2]).rsplit('/')
	print page_name
	string = '(2f)' # magic number
	page_name = string.join(page_name)
	print page_name
	if not Page(request, page_name).exists():
		print "The url you have provided is not a page that has already been created"
		return
	permissions = get_permissions()
	#print permissions.get('read_only')
	#print args.permissions
	text = "{0}\n".format(permissions.get(args.permissions, 'read_only'))
	#print "this is it" + text 
	text += Page(request, page_name).get_raw_body()
	print text
	print PageEditor(request, page_name).saveText(text, 0)
	process_user_link(page_name, args)

	# page_path = os.path.join(data_folder, 

    #path_parts = url_parts[2].rpartition('/')
    #print('URL: {}\nreturns: {}\n'.format(i, path_parts[2]))

	#if not Page(request, name).exists():

def get_file_path(name, file=0, template=0):
	"""Retrieve the file from the pages pages_directory
	@param name: the name of the file to retrieve
	@param file: Set to 1 if the page is a custom page 
	@param template: Set to 1 if the page is a template"""
	file_path = ""
	if file == 1:
		file_path = os.path.join(pages_directory, name)
	if template == 1:
		file_path = os.path.join(template_path, name)
	return file_path

def add_quick_link(uid, page_name):
	#group pages added by default
	#command line arguments
	"""Add a quick link to a user's task-bar
	@param uid: the user id of the user
	@page_name: the name of the page to add quicklink to"""
	u = user.User(request, uid)
	if not u.isQuickLinkedTo(page_name): #may need to be a list
		u.addQuicklink(page_name)



parser = argparse.ArgumentParser()
parser.add_argument("--page_name", help="the name of the page being created")
#parser.add_argument("-u", "--user", help="specify that a user page is being created", action="store_true")
#parser.add_argument("-a", "--admin", help="specify that an admin group is being created", action="store_true")
parser.add_argument("-all", "--show_to_all", help="flag if all users should have this page as a quicklink", action="store_true")
parser.add_argument("--group_names", help="the name of the groups to create a quicklink for", action="store", nargs="*")
parser.add_argument(dest="filenames", help="the names of the files to create pages from", nargs='*')
parser.add_argument("--template", help="if a page should be created for each group with the project template....specify template?") #efault="homework_template"
parser.add_argument("--permissions", help="specify the permissions for the page. ", choices=['instructor_read_only', 'read_only', 
	'user_write_only', 'group_write_only'])
parser.add_argument("--url", help="the url of the page you would like to push to users")

def command_line_processing():	
    #create group
	#global user
	args = parser.parse_args()
	print "Page_Name: %s" % args.page_name
	#print "User: %d" % args.user
	#print "Admin: %d" % args.admin
	print "show_to_all: %d" % args.show_to_all
	print "Group_Name: %s" % args.group_names
	print args.permissions
	print args.template
	print args.filenames
	name = None
    # One of create, modify or delete must be specified
	if not (args.filenames or args.template or args.url):
		parser.error ("Please specify a file, url or a template to create a page from")
		return
	if not (args.permissions):
		 default_permissions = raw_input("The permissions for this file will be set to read_only. Press Y to continue or any other key to halt program\n")
		 if default_permissions == 'Y':
		 	args.permissions = 'read_only'
		 else:
		 	print "Permissions can be set using the --permissions flag. See --help for more information"
	#This is messy. Tidy it up

	if (args.filenames and args.template) or (args.filenames and args.url) or (args.url and args.template):
		parser.error("You can only specify a filename, a template or a url")
		return
	if not (args.filenames or args.page_name or args.url):
		name = raw_input("Please specify a page name: ")
	elif args.page_name:
		name = args.page_name
	#if (args.user and args.admin):
		#parser.error("You cannot create a page with both admin and user permissions. Admin members are automatically given rights on user pages")
		#return
	#if args.admin:
		#admin = 1
	#elif args.user:
		#user = 1
	#elif args.group_names:
		#check execution was completed
		#find group
		#retrieve members
		#call quicklinks
	if args.template:
		template = args.template
		file_path = get_file_path(template, template=1)
		add_new_page(file_path, args, name)		
	elif args.filenames:
		for fname in args.filenames:
			if name is None:
				name = os.path.splitext(fname)[0]
				print name
			file_path = get_file_path(fname, file=1)
			add_new_page(file_path, args, name)
	elif args.url:
		process_url_page(args)
	#elif args.template
# HomePage Template
#parser.add_argument("--template", help="if a page should be created for each group with the project template....specify template?")

def run():
	#Remove this line
	login('here') # This doesn't work
	command_line_processing()

if __name__ == "__main__":
	run()
