"""---------------------------------------------------------
Command - Create File Tree
------------------------------------------------------------

This command allows users to create file trees from the command line"""

import path
from tortus_command import TortusScript
from tortus_page import TortusPage
from MoinMoin.web.contexts import ScriptContext
from MoinMoin import user
from MoinMoin.Page import Page
from MoinMoin.PageEditor import PageEditor
from tortus_project import TortusProjectCollection, TortusGroup
from default import *
from helper import ArgHelper
from urlparse import urlparse
import argparse, os, re, sys
from search import search_pages, print_toc, create_page, traverse_pages

class Tortus(TortusScript):

	def __init__(self):

		self.parser = argparse.ArgumentParser()
		self.request = ScriptContext()
		self.parser.add_argument(
			"--permissions", 
			help="specify the permissions for the page. ", 
			choices=['instructor_read_only', 'read_only', 'user_write_only', 'group_write_only']) #Not yet implemented
		self.parser.add_argument(
			"--url", 
			help="the url of the root directory you would like to push to users", action="store")
		self.parser.add_argument(
			"--project", 
			help="the project to push the page to") #Should be able to deduce from url
		self.args = self.parser.parse_args()
		self.opts = vars(self.parser.parse_args())
		self.page = TortusPage()

	def run(self):
		arghelper = ArgHelper(self.opts, self.parser)
		project, projects = arghelper.get_project()
		self.group_obj = TortusGroup(project.name)
		permissions = arghelper.get_permissions()
		if not self.args.url:
			self.parser.error ("You need to specify a url to create the file tree from")
			sys.exit()
		root_dir = self.process_url(self.args.url)
		pages = traverse_pages(root_dir)
		created = self.copy(pages, project)
		central_page = TortusPage()
		uIDs = []
		for name in project.get_members():
			uid = user.getUserId(self.request, name)
			central_page.add_quick_link
			if user.User(self.request, uid).exists():
				uIDs.append(uid)
		project.update_contents(project.get_members())

	def process_url(self, url, level=0):
		wiki_data = os.path.basename(os.path.dirname(data_folder))
		url_parts = urlparse(url)
		page_name = (url_parts[2].rpartition(wiki_data + '/')[2]).rsplit('/')
		file_string = '(2f)' # magic number
		file_name = file_string.join(page_name)
		moin_link = '/'.join(page_name)
		if not Page(self.request, moin_link).exists():
		    print "The url you have provided is not a page that has already been created"
		    sys.exit()
		else:
		    return file_name

	def copy(self, matches, project):
		user_acls = {}
		group_acls = {}
		pg = TortusPage()
		for page in matches:
			page_name = re.sub('\(2f\)', '/', page)
			text = Page(self.request, page_name).get_raw_body()
			user_copy = '##User copy'
			group_copy = '##Group copy'
			if text.find(user_copy) != -1:
				user_acls.update({(user, get_permissions(user_name=user).get('user_write_only')) for user in project.get_members()})
				page_name = re.sub('^.*ProjectHomepage/', '', page_name)
				pg.user_copy(user_acls, project, page_name, page, 1)
			elif text.find(group_copy) != -1:
				group_acls.clear()
				group_acls.update({(group, get_permissions(group_name=get_name(self.args.project, group_name=group).get('instructor_group_page')).get('group_write_only')) for group in project.groups})
				page_name = re.sub('^.*ProjectHomepage/', '', page_name)
				pg.group_copy(group_acls, project, page_name, page, 1)
			else:
				pg.generic_copy(project, page_name)  

if __name__ == "__main__":
	command = Tortus()
	command.run()

