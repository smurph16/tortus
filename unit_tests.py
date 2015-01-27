import unittest
from accessing_groups import *

class GroupsTest(unittest.TestCase):
	"""Tests for groups.py"""
	def setUp(self):
		#self.
	def test_create_group_page(self):
		self.

def create_group_page(group_name, members):
    pagename = group_name
    	text = "#acl AdminGroup:read,write,delete,revert,admin " + pagename + ":read,write All: read\n #Category:User\n"
    	text += members
    	print PageEditor(request, pagename).saveText(text, 0)
    #project_pagename = 
    ##acl Project/AdminGroup:admin,read,write,delete,revert Project/ReadWriteGroup:read,write Project/ReadGroup:read
    	print "Group successfully created with name: %s" % pagename
    	print "Members:\n%s" % members
    	return 0

def create_single_group(members, group_name="default"):
	text = ""
	for member in members:
		line = " * {0} \n".format(member)
		text += line
	if not group_name == "default":
		name = group_name
	else:
		name = "%dGroup" % group_count()
	group_created = create_group_page(name, text)
	if group_created == 0:
		all_groups = open(all_groups_path, 'a')
		string_to_write = '\n-----------------------------------------------\n' + name + '\n-----------------------------------------------\n'
		all_groups.write(string_to_write)
		all_groups.write(text)
		all_groups.close()	

def process_group_file(path, group_name="default"):
# if file path/paths are provided, process each one
	global all_groups_path
	all_groups = open(all_groups_path, 'a')
	number_of_groups = group_count()
	text = ""
	bullet = " * "
	with open(path, 'r+') as fin:
		grouped_file = process_path(path)
		with open(grouped_file, "w") as fout:
			for line in fin:
				if not line == "\n":
					line = bullet + line
					text += line
				if line == "\n":
					if not group_name == "default":
						name = group_name
					else:
						name = "%dGroup" % number_of_groups
					group_created = create_group_page(name, text)
					if group_created == 0:
						string_to_write = '\n-----------------------------------------------\n' + name + '\n-----------------------------------------------\n'
						fout.write(string_to_write)
						fout.write(text)
						all_groups.write(string_to_write)
						all_groups.write(text)
						number_of_groups += 1
					text = ""
	all_groups.close()

	#fin.close()
# if no file paths are provided, prompt for one
def process_path(path):
	(file_name, file_extension) = os.path.splitext(path)
	file_name = file_name + "_grouped" + file_extension
	grouped_file = os.path.join(os.path.dirname(os.path.abspath(path)), file_name)
	return grouped_file

#This is a bit annoying...It isn't updating..It's completely re-writing the file
def remove_group(name):
	#Find the group files
	group_page_path = os.path.join("/usr/local/share/moin/eduwiki/data/pages", name)
	if os.path.exists(group_page_path):
		print "Removed Group with name: %s" % name
		shutil.rmtree(group_page_path)
	else: 
		print "Unable to find Group with name: %s" % name
		return
	create_copy()
	create_all_groups_version(name)

def create_all_groups_version(name):
	global all_groups_path
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
				elif line == "-----------------------------------------------\n": 
					count += 1
					if count == 2:
						writing = True
	shutil.move(all_groups_revised, all_groups)

def edit_all_groups_file(name):
	global all_groups_path
	all_groups_file = open (all_groups_path, 'r+')
	all_groups = all_groups_file.read()
	pattern = '-{47}\n%s\n[^-{47}]*'%name
	print pattern
	pattern = re.compile('-{47}\n%s\n-{47}[^-{47}]*'%name, re.M)
	result = pattern.match(all_groups)
	print "match found", result
	new_text = re.sub(pattern, "", all_groups)
	print new_text
	return new_text

def write_all_groups_file(text):
	global all_groups_path
	all_groups_file = open (all_groups_path, 'w')
	all_groups_file.write(text)
	all_groups_file.close()

def create_copy():
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

def remove_all_groups():
	global all_groups_path
	check = raw_input("Are you sure you want to remove all user groups from this wiki? This action cannot be undone...easily: Type Y to continue with deletion ")
	if check == "Y":
		# Remove pages
		# Create copy
		create_copy()
		# Clear all_groups file
		open(all_groups_path, 'w').close()
	else:
		print "Deletion aborted"

#Create groups ---> default text file? command line...is it necessary ---> naming...default add to user number, otherwise provide names in file ----> project pages as well?
#Remove groups ---> must flag with text-file, command line arguments or all  ???Is this a user group? default command line arguments

#Specify options first on the command line
parser = argparse.ArgumentParser()
parser.add_argument("--create_group", help="signify that you want to create a group", action="store_true")
parser.add_argument("--project_name", help="the name of the project groups are being created for")
parser.add_argument("-all", "--clear_all_groups", help="delete all user groups", action="store_true")
parser.add_argument("--remove_group", help="delete groups specified. Default is given from command line", action="store_true")
parser.add_argument("-u", "--user", help="specify that a user group is being manipulated", action="store_true")
parser.add_argument("-a", "--admin", help="specify that an admin group is being manipulated", action="store_true")
parser.add_argument("--modify_group", help="change the construction of the groups", action="store_true")
parser.add_argument("--group_name", help="the name of the group to create, delete or modify", action="store", nargs="*")
parser.add_argument("--member_names", help="members of the group to be added, deleted or modified", nargs='*', action="store")
parser.add_argument(dest="filenames", help="the names of the files storing the groups to be modified", nargs='*')
parser.add_argument("--createProjectPage", help="if a page should be created for each group....specify template?")


def command_line_processing():
    #create group
	global user
	args = parser.parse_args()
	print "Create_group: %d" % args.create_group
	print "Remove_all_groups: %d" % args.clear_all_groups
	print "Remove_group: %d" % args.remove_group
	print "User: %d" % args.user
	print "Admin: %d" % args.admin
	print "Modify_group: %d" % args.modify_group
	print "Group_Name: %s" % args.group_name
	print args.filenames
	print args.member_names

    # One of create, modify or delete must be specified
	if not (args.create_group or args.remove_group or args.modify_group):
		parser.error ("No action requested. Please specify 	--create_group or --remove_group or --modify_group")
		return
    # Create argument	
	if args.create_group:
    	# One of user or admin must be specified
		if not (args.user or args.admin):
			parser.error("Must specify whether it is an admin or user group you want to create (-u or -a)")
			return
		alter_environment(args)
    	# Group to be created on command line or with text file
		if not (args.member_names or args.filenames):
			parser.error("Must specify member names in command line or path to file containing names")
			return	
    	# Store name if default not wanted
		if args.group_name and len(args.group_name) > 1:
			print "You can only specify one group name for creating a group"
			return
		#This is messy...clean it up	
		elif args.group_name:
			name = args.group_name[0]
			print "Creating group %s" % name
		if not args.group_name:
			name = "default"
		create = 1
		for fname in args.filenames:
			process_group_file(fname)
			print "processed a_file"
		if args.member_names:
			create_single_group(args.member_names, name)

    # Remove argument
	elif args.remove_group:
    	#One of user or admin must be specified
		if not (args.user or args.admin):
			parser.error("Must specify whether it is an admin or user group you want to remove (-u or -a)")
			return
		if args.clear_all_groups:
			delete_all = 1
			print "Deleting all groups"
    	#Group(s) to be deleted must be specified on command line or in text-file
		elif not (args.group_name or args.filenames):
			parser.error("Must specify group name in command line or path to file containing group_names to be deleted")
			return
		delete = 1
		if args.group_name:
			for gname in args.group_name:
				print "gname" + gname
				remove_group(gname)
				print "Deleting group %s" % gname
				text = edit_all_groups_file(gname)
				write_all_groups_file(text)
		#else:
			#for fname in args.filenames:
		create_copy()
    # Modify argument
	elif args.modify_group:
		modify = 1

def run(): 

	# if "--remove_multiple_groups" in sys.argv: remove_multiple = 1
	# if remove_multiple == 1:
	# 	remove_multiple_groups()
	# if "--user_group" in sys.argv: user_page = 1
	user_group = 1 #Edit this configuration
	command_line_processing()

def alter_environment(env):
	global user, admin, instructor
	if env.user:
		user = 1
	if env.admin:
		admin = 1
	#if env.instructor:
		#instructor = 1

def group_count():
	groups = request.groups
	count = 0
	pattern = re.compile('[0-9]+Group')
	for group in groups:
		temp_group = groups.get(group)
		#print temp_group
		if pattern.match(temp_group.name) is not None: 
			count += 1
	print temp_group.name
	print "count: %d" % count
	return count
	
if __name__ == "__main__":
	run()


	# Read the file
	# Store the 

