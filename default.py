#This is where the configuration directory is stored
config_dir = '/usr/local/share/moin/eduwiki'

#This is the url of the wiki
wiki_url = 'http://localhost/eduwiki'

#This is where the master group file is stored
all_groups_path = '/usr/local/share/moin/tortus/all_groups.txt'

#This is the location of where the  data folder is stored for the MoinMoin wiki
data_folder = '/usr/local/share/moin/eduwiki/data'

#This is where pages created by the instructor are stored. This is not where pages are stored for the actual wiki
page_path = '/usr/local/share/moin/tortus/pages'

#This is where templates for easy page creation are stored. 
template_path = '/usr/local/share/moin/tortus/pages/templates'

#This is where the wiki config file is located
wiki_config = '/usr/local/share/moin/wikiconfig.py'

#This is where the Group regex can be altered. If you change it here you must also change it in wikiconfig.py
group_regex = u'(?P<all>(?P<key>\\S+)Group)'

#This is where the Group regex can be altered. If you change it here you must also change it in wikiconfig.py
project_regex = '^\w+Project$'

#This is where project files will be produced.
project_files = '/usr/local/share/moin/projects'

#This is where the persistent json files are kept
json_file = "/usr/local/share/moin/persistent/json_project.json"

#This is the username regex. It controls an individuals access to pages
username_regex = '[a-z]{4}[0-9]{4}'

#This is where default permissions can be changed
def get_permissions(user_name="",group_name=""):
	permissions = {
	#pages that only contain organisation information such as members of different groups
	'instructor_read_only': '#acl AdminGroup:read,write,delete,revert,admin EditorGroup:read,write,revert All:\n', 
	#pages that only instructors or tutors can edit such as instructional pages or lecture notes
	'read_only': '#acl AdminGroup:read,write,delete,revert,admin EditorGroup:read,write,revert All:read\n',
	#pages that all can read but only the user it belongs to can write to
	'user_write_only': '#acl AdminGroup:read,write,delete,revert,admin EditorGroup;read,write,revert {0}:read,write All:read\n'.format(user_name),
	#pages that all can read but only users that belong to the group can write to
	'group_write_only':'#acl AdminGroup:read,write,delete,revert,admin EditorGroup:read,write,revert {0}:read,write All:read\n'.format(group_name)
	}
	return permissions

