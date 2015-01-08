from MoinMoin.web.contexts import ScriptContext
request = ScriptContext()
from MoinMoin.datastruct.backends import wiki_dicts

groups = request.groups
my_list = groups.groups_with_member(u'Smurph16')
for item in my_list:
	print item
frog_list = groups.groups_with_member(u'frog3456')
for item in frog_list:
	print item
print u'WaterGroup' in groups
print repr(groups)
water_group = groups.get('WaterGroup')
print repr(water_group)

homework_group = groups.get('HomeworkGroup')
print repr(homework_group)

for member in homework_group:
	print member
	
