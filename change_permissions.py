from default import *
from useful import has_permissions
import re, argparse
from MoinMoin.Page import Page
from MoinMoin.web.contexts import ScriptContext
request = ScriptContext()
from MoinMoin.PageEditor import PageEditor

def change_page_permissions(page_name, permission, user_name="",group_name=""):
	if Page(request, page_name).exists():
		permissions = get_permissions(user_name,group_name)
		if permission in permissions:
			"getting to here"
			text = Page(request, page_name).get_raw_body()
			if has_permissions(page_name):
				text = re.sub(r'#acl.*', permissions.get(permission), text)
			else:
				text = permissions.get(permission) + text
			PageEditor(request, page_name).saveText(text, 0)
		else:
			print "That is not a valid permission set. You must add a custom acl to complete this task"

parser = argparse.ArgumentParser()
parser.add_argument("permission", help="this is the permission to be added/altered for the page")
parser.add_argument("page_name", help="this is the page the permission should be altered for")
parser.add_argument("--user_name", help="this is the user to alter permissions for")
parser.add_argument("--group_name", help="this is the group to alter permissions for")

def command_line_processing():
	args = parser.parse_args()
	if not args.permission:
		parser.error("Please specify the permission to change the page to")
		return
	if not args.page_name:
		parser.error("Please specify the page to alter the permissions for")
		return
	if args.user_name:
		change_page_permissions(args.page_name, args.permission, username=args.user_name)
	elif args.group_name:
		change_page_permissions(args.page_name, args.permission, groupname=args.groupname)	
	else:
		change_page_permissions(args.page_name, args.permission)
def run():
	command_line_processing()

if __name__ == "__main__":
	run()

		#do something

#def add_permission():

# def user_change_to_write(name):

# def group_change_to_read(name):

# def group_change_to_write(name):
