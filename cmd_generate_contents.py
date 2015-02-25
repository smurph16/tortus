from MoinMoin.web.contexts import ScriptContext
from tortus_command import TortusScript
from tortus_page import TortusPage
from tortus_group import TortusGroup
from helper import ArgHelper
request = ScriptContext()
import argparse


class Tortus(TortusScript):

	def __init__(self):

		self.parser = argparse.ArgumentParser()
		self.request = ScriptContext()
		# self.parser.add_argument(
		# 	"--page_name", 
		# 	help="the name of the page being created")
		self.parser.add_argument(
			"--all", 
			help="flag if all project members should be updated", 
			action="store_true")
		self.parser.add_argument(
			"--user_names", 
			help="the names of the users whose contents pages should be updated", 
			action="store", nargs="*")
		self.parser.add_argument(
			"--project", 
			help="the project to push the page to")
		self.args = self.parser.parse_args()
		self.opts = vars(self.parser.parse_args())
		self.page = TortusPage()

	def run(self):
		arghelper = ArgHelper(self.opts, self.parser)
		project, projects = arghelper.get_project()
		self.group_obj = TortusGroup(project.name)
		if not (self.args.user_names or self.args.all):
			self.parser.error("You must specify which contents pages to update")
			sys.exit()
		if self.args.user_names:
			members = self.args.user_names
		else:
			members = project.get_members()
		project.update_contents(members)

if __name__ == "__main__":
	command = Tortus()
	command.run()