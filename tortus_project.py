from MoinMoin.web.contexts import ScriptContext
from MoinMoin.PageEditor import PageEditor
from MoinMoin.Page import Page
from MoinMoin.datastruct.backends import wiki_dicts #take this import away
from tortus_page import TortusPage
from tortus_group import TortusGroup
from default import *
from MoinMoin import user, wikiutil
from MoinMoin.user import User, getUserList
from urlparse import urlparse
import os.path, argparse, re, time, shutil, json
from search import search_pages, print_toc, create_page

class ProjectDoesNotExistError:
	"""Raised when project is not found"""

class TortusProjectCollection(dict):
	def __init__( self, *arg, **kw ):
         super( TortusProjectCollection, self ).__init__( *arg, **kw )
     
	def tortus_project( self, *arg, **kw ):
		moin_name = self.get_moin_name(kw['name'])
		name = kw['name']
		if os.path.getsize(json_file) > 0:
			with open (json_file, 'r') as f:
				if self.project_exists(name) == 0:
					json_data = json.load(f)
					project = TortusProject(json_data["projects"][name])
				else:
					project = TortusProject( *arg, **kw )
					self.record(project)
		else:
			project = TortusProject( *arg, **kw )
			self.record(project)
		self[project.name]= project
		return project

	def record(self, project):
    	#Load json data
		with open (json_file, 'r+') as f:
			if os.path.getsize(json_file) > 0:
				exists = self.project_exists(project.name)
				f.seek(0)
				if exists == 2: #The projects object doesn't exist
					json_data = self.json_create_project_structure()
					json_data["projects"].update(self.json_default(project))
					json.dump(json_data, f)
				elif exists == 1: #Only the project itself doesn't exist
					json_data = json.load(f)
					json_data["projects"].update(self.json_default(project)) #Do I want to lose the data?
					f.seek(0)
					json.dump(json_data, f) 
				elif exists == 0: #The project already exists
					json_data = json.load(f)
					json_project = json_data["projects"][project.name]
			else:
				json_data = self.json_create_project_structure()
				json_data["projects"].update(self.json_default(project))
				json.dump(json_data, f)
			
	def json_create_project_structure(self):
		json_data = {"projects":{}} 
		return json_data
	
	def project_exists(self, project_name):
		"""Determines whether a project exists
		@param project_name: the name of the project
		@returns int:
			0: project_exists
			1: projects dictionary exists
			2: no projects exist
			3: JSON object could not be found"""
		#Change to try, except
		if os.path.getsize(json_file) == 0:
			return 2 #Why didn't this work?
		with open (json_file, 'r') as f:
			exists = 3
			try:
				json_data = json.load(f)
				if json_data.has_key("projects"):
						if json_data["projects"].has_key(project_name):
							exists = 0
						else:
							exists = 1
				else:
					exists = 2
			except ValueError:
					print "A JSON Object could not be found in that file"
		return exists

	def get_moin_name(self, name):
		"""Gets the moin_name of the project
		@param name: the moin name of a project"""
		pattern = re.compile(project_regex)
		if pattern.match(name):
			map_name = name
		else:
			map_name = "{0}Project".format(name)
		return map_name

	def json_default(self, project):
		project_dict = {project.name:{}}
		dict_copy = project.__dict__
		dict_copy.pop('args') #Better to write custom json encoder
		project_dict[project.name].update(dict_copy)
		return project_dict

	def update_groups(self, project, arg):
		with open (json_file, 'r+') as f:
			if os.path.getsize(json_file) > 0:
				exists = self.project_exists(project.name)
				f.seek(0)
				if exists == 0: #The project already exists
					json_data = json.load(f)
					f.seek(0)
					#print json_data["projects"][project.name][arg]
					#print getattr(project, arg)
					json_data["projects"][project.name][arg] = getattr(project, arg)
					f.truncate()
					json.dump(json_data, f)
				else:
					"Cannot update because this project doesn't exist"
			else:
				"Cannot update because this project doesn't exist"
# 	def default(self, obj):
# 		if isinstance()

class TortusProject(object): # inherit from Page?
	"""Tortus -  class
	This class is used for manipulation and creation of user pages. It does
	something"""
	def __init__(self, *args, **kwargs):
		#As soon as a project is created it has to have organisation pages, user pages
		#Every Page in a project must be classified as one of these three options
		for dictionary in args:
		    for key in dictionary:
		        setattr(self, key, dictionary[key])
		for key in kwargs: 
		    setattr(self, key, kwargs[key])
		self.moin_name = self.get_moin_name(self.name)
		#self.pages = Tree() #implement file structure tree here
		tortus_page_obj = TortusPage()
		if self.create_project_files():
			print "here"
			self.groups = {}
			p = get_permissions()
			permissions = p.get('instructor_read_only')
			tortus_page_obj.add_from_file(
				os.path.join(template_path, 'instructor_project_homepage'), self, get_name(self.name).get('instructor_project_homepage'),'organisation', permissions)
			permissions = p.get('read_only')
			tortus_page_obj.add_from_file(
				os.path.join(template_path, 'student_project_homepage'), self, get_name(self.name).get('instructor_student_homepage'), 'organisation', permissions)
		else:
			pass
			#self.groups = json_stuff
		#self.central_page

	def __repr__(self):
		return '<TortusProject(%s)>'%self.name

	def get(self, key, default=None):
		"""
        Return the dictionary named <key> if key is in the backend,
        else default. If default is not given, it defaults to None, so
        that this method never raises a DictDoesNotExistError."""
		try:
			return self[key]
		except ProjectDoesNotExistError:
			return default

	def create_project_files(self):
		project_path = os.path.join(project_files, self.name)
		if not os.path.exists(project_path):
			os.makedirs(project_path)
			os.mkdir(os.path.join(project_path, 'groups'))
			os.mkdir(os.path.join(project_path, 'groups', 'revisions'))
			os.mkdir(os.path.join(project_path, 'pages'))
			return True
		return False

	def write_project_group_file(self):
		"""Generate a file containing all the groups in the project"""
		tortus_group_obj = TortusGroup(self.name)
		text = tortus_group_obj.repr_groups(self.groups)
		group_path = os.path.join(project_files, self.name, 'groups')
		if not os.path.exists(group_path):
			os.makedirs(group_path)
		elif os.path.isfile(os.path.join(group_path, 'groups')):
			self.create_copy(os.path.join(group_path, 'groups'))
		with open (os.path.join(group_path,'groups'), 'w') as project_groups:
			project_groups.write(text)

	def create_copy(self, path):
		"""Create a copy of the project groups file for back-up"""
		string = time.ctime(os.path.getmtime(path))
		modification = '_' + string.replace(' ', '-')
		file_name = "{0}{1}".format('groups', modification)
		retain_file = os.path.join(os.path.dirname(path), 'revisions', file_name)
		try:
			shutil.copy(path, retain_file)
		except shutil.Error as e:
			print 'A revision file was not made. Error %s' % e
		except OSError as e:
			print 'A revision file was not made. Error: %s' % e
		except IOError as e:
			print ("Error: a revision file was not made. %s" % e.strerror)

	def get_moin_name(self, name):
		pattern = re.compile(project_regex)
		if pattern.match(name):
			map_name = name
		else:
			map_name = "{0}Project".format(name)
		return map_name

	def get_name(self, name):
		return self.name

	def get_members(self):
		members = set()
		for group in self.groups:
			members |= set(self.groups[group])
		return members

	def update_contents(self, members):
		for name in members:
			groups = ["t:{}ProjectHomepage/{}GroupHomepage".format(self.name, group) for group in self.groups if name in self.groups[group]]
			group_needle = " or ".join(groups)
			needle = "t:{} or {}".format(name, group_needle)
			if search_pages(needle): #Try Except
				graph, reverse_dict = search_pages(needle)
				print_toc(graph, reverse_dict)
				with open ('temp.txt', 'r') as page:
					text = page.read()
					create_page(text, name)
