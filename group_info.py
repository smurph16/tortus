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
from helper import ArgHelper
import argparse, os	

class Tortus(TortusScript):

#How many groups
#List groups
#Find all groups with x members
#What group is blah in
#Who is in blah group

	def __init__(self):
		import argparse
		self.request = ScriptContext()
		self.parser = argparse.ArgumentParser()
		self.parser.add_argument(
			"--project", help="the name of the project")
		self.parser.add_argument(
			"--group_name", help="the name of the group to determine information about", action="store")
		self.parser.add_argument(
			"--member", help="determine which group the member is in", nargs='*', action="store")
		self.parser.add_argument(
			"--list", help="list all groups in a particular project", action="store_true")
		self.parser.add_argument(
			"--number", help="the number of groups in a specified project", action="store_true")
		self.parser.add_argument(
			"--count", help="lists the groups with that number of members", action="store")
		self.args = self.parser.parse_args()
		self.opts = vars(self.args)


	def command_line_processing(self):
		arghelper = ArgHelper(self.opts, self.parser)
		project, projects = arghelper.get_project()
		group_obj = TortusGroup(project.name)
		if self.args.list:
			text = group_obj.repr_groups(project.groups)
			print text
		elif self.args.group_name:
			try:
				print project.groups.get(self.args.group_name) 
			except KeyError:
				print "That isn't a valid group name"
		elif self.args.member:
			print [group for group in project.groups if self.args.member in group]
			sys.exit()
		elif self.args.number:
			print len(project.groups)
		elif self.args.count:
			grps = [group for group in project.groups if (len(project.groups[group]) == int(self.args.count))]
			print grps

	def run(self): 
		self.command_line_processing()

if __name__ == "__main__":
	command = Tortus()
	command.run()
