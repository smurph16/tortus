import json

class ProjectEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, TortusProject):
			return {
				'__type__': 'tortus_project',
				'name': obj.name,
				'args':obj.args,
				'groups':obj.groups
			}
		else:
			return JSONEncoder.default(self, obj)

class ProjectDecoder(json.JSONDecoder):
	def __init__(self, *args, **kwargs):
		json.JSONDecoder.__init__(self, object_hook=self.dict_to_object, *args, **kwargs)

	def dict_to_object(self, d):
		print "is this being called"
		list_of_projects = d.pop('projects')
		print list_of_projects
		for project in list_of_projects:
			print type(project)
		if '__type__' not in d:
			return d
		type = d.pop('__type__')
		if type == 'tortus_project':
			return TortusProjectCollection.tortus_project(**d)
		else:
			inst = d
		return inst

data_structure = {
	"projects": {
		"project_name1" : {
			"name": "test_name",
			"args": "args"
		}
	}
}

def dict_to_object(d):
	print d
	list_of_projects = d.pop('projects')
	print list_of_projects
	for project in list_of_projects:
		print type(project)
	if '__type__' not in d:
		return d
	type = d.pop('__type__')
	if type == 'tortus_project':
		return TortusProjectCollection.tortus_project(**d)
	else:
		inst = d
	return inst



#encoded_object = (json.dumps(data_structure, cls=ProjectEncoder))
encoded_object = '''{
    "projects": {
        "project_1": {
            "name": "magic",
            "args": "blahs"
        },
        "project_2": {
            "name": "super",
            "args": "broken"
        },
        "project_3": {
            "name": "special",
            "args": "bingo"
        }
    }
}'''
				
#decode = ProjectDecoder(encoded_object)
inst = json.loads(encoded_object)
print inst['projects']['project_3']['name']