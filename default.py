#This is where the master group file is stored
all_groups_path = '/usr/local/share/moin/tortus/all_groups.txt'

#This is the location of where the  data folder is stored for the MoinMoin wiki
data_folder = '/usr/local/share/moin/eduwiki/data'

#This is where pages created by the instructor are stored. This is not where pages are stored for the actual wiki
page_path = '/usr/local/share/moin/tortus/pages'

#This is where templates for easy page creation are stored. 
template_path = '/usr/local/share/moin/adminconfig/pages/templates'

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
