"""---------------------------------------------------------
Command - Create Groups
------------------------------------------------------------

This command allows users to create groups from the command line"""

from tortus_command import TortusScript
from tortus_project import TortusProjectCollection
from tortus_page import TortusPage
from tortus_group import TortusGroup
from MoinMoin.web.contexts import ScriptContext
from MoinMoin import user #Don't think that I need this
from default import *
import argparse, os	

class Tortus(TortusScript):

	# def __init__(self):

	# 	self.parser = argparse.ArgumentParser()
	# 	self.request = ScriptContext()
	# 	self.parser.add_argument("--project", help="the name of the project of the page being created")
	# 	self.parser.add_argument("-all", "--copy_for_all", help="flag if all users should have this page as a quicklink", action="store_true")
	# 	self.parser.add_argument("--group_names", help="the name of the groups to create a quicklink for", action="store", nargs="*")
	# 	self.parser.add_argument("--user_names", help="the name of the users to create a central page for")
	# 	self.parser.add_argument(dest="filenames", help="the names of the files to create pages from", nargs='*')
	# 	self.parser.add_argument("--template", help="if a page should be created for each group with the project template....specify template?") #efault="homework_template"
	# 	self.parser.add_argument("--permissions", help="specify the permissions for the page. ", choices=['instructor_read_only', 'read_only', 
	# 	'user_write_only', 'group_write_only'])
	# 	self.parser.add_argument("--url", help="the url of the page you would like to push to users")
	# 	self.parser.add_argument("--subpage", help="")
	# 	self.parser.add_argument("--central_page", help="create a homepage for the user or group", action="store_true")
	# 	self.args = self.parser.parse_args()
	# 	self.page = TortusPage()

	def __init__(self):
		import argparse
		self.request = ScriptContext()
		self.parser = argparse.ArgumentParser()
		self.parser.add_argument("--project", help="the name of the project groups are being created for")
		self.parser.add_argument("--group_name", help="the name of the group to create, delete or modify", action="store")
		self.parser.add_argument("--member_names", help="members of the group to be added, deleted or modified", nargs='*', action="store")
		self.parser.add_argument(dest="filenames", help="the names of the files storing the groups to be modified", nargs='*')
		self.parser.add_argument("--createProjectPage", help="if a page should be created for each group....specify template?")
		self.parser.add_argument("--categorise", help="if a group should be created containing the new groups", action="store")
		self.parser.add_argument("--permissions", default="instructor_read_only", help="specify the permissions for the group pages. Default: instructor_read_only")
		self.parser.add_argument("--group_prefix", help="a prefix for naming groups") #Do I need this?
		self.args = self.parser.parse_args()


	def command_line_processing(self):
		if not (self.args.member_names or self.args.filenames):
			self.parser.error("Must specify member names in command line or path to file containing names")
			return
		if self.args.project:
			project_name = self.args.project
		else:
			default_project = raw_input("This group will belong to the project DefaultProject. Please Y to proceed or any other key to cancel: ")
			if not default_project == "Y":
				return
			project_name = "default"
		projects = TortusProjectCollection()
		if not (projects.project_exists(project_name) == 0): #Make the project if it doesn't exist
			mk_prj = raw_input("This project does not exist yet. If you would like to create it, please Y to proceed or any other key to cancel: ")
			if mk_prj == 'Y':
				project = projects.tortus_project(name =project_name, groups={}, args=self.args)
			else:
				return #Exit if project shouldn't be created
		#Get the project again/
		else:
			project = projects.tortus_project(name=project_name, groups={}, args=self.args) #This is a retrieval step...initialises it with existing data
		group_obj = TortusGroup(project.name)
		if self.args.group_name:
			name = self.args.group_name
		else:
			name = project_name #Default 
		grps_to_create = []
		if self.args.filenames:
			for fname in self.args.filenames:
				if group_obj.process_group_file(fname) is not None:
					grps_to_create.extend(group_obj.process_group_file(fname))
				else:
					print "Could not create any groups."
					return
		elif self.args.member_names:
			grps_to_create.extend([member for member in member_names])
		group_obj.create_groups(grps_to_create, name, project, projects)
		# created_groups = {}	
		# failed_groups = []

		# for group in grps_to_create:
		# 	formatted_members = group_obj.format_members(group)
		# 	group_name = group_obj.get_group_name(name)
		# 	created_page = group_obj.create_group_page(group_name, formatted_members)
		# 	if created_page == 1:
		# 		failed_groups.append(group_name)
		# 	else:
		# 		created_groups[group_name] = group
		# #project = projects.tortus_project(# This is due to changing the name to Boo Project...need to add a method
		# for group in created_groups:
		# 	project.groups.update(created_groups)
		# project.write_project_group_file()
		# projects.update_groups(project, 'groups')
		# self.print_actions(group_obj, created_groups, failed_groups)

#get groups method

	def run(self): 
		self.command_line_processing()

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

if __name__ == "__main__":
	command = Tortus()
	command.run()
