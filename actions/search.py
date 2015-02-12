from MoinMoin.web.contexts import ScriptContext
from MoinMoin.search import searchPages
request = ScriptContext()
from MoinMoin.Page import Page
from MoinMoin import search
from MoinMoin.PageEditor import PageEditor
import pprint, collections

def getFromDict(dataDict, mapList):
	return reduce(lambda d, k: d[k], mapList, dataDict)

def setInDict(dataDict, mapList, value):
	if not dataDict:
		getFromDict(dataDict, mapList[:-1])[mapList[-1]] = value
	if getFromDict(dataDict, mapList[:-1]).has_key(mapList[-1]):
		return dataDict
	else:
		getFromDict(dataDict, mapList[:-1])[mapList[-1]] = value
	return dataDict

needle = "t:battabo332 or t:7GroupHomepage"
search_result = search.searchPages(request, needle)
levels = {}
pages = []
search_result.hits
graph = {}
index = graph
reverse_dict = {}
for title in search_result.hits:
	pages = title.page_name.split('/') #Add a conditional here...only want to exclude the first level if it is a user
	print pages
	if reverse_dict.has_key(pages[-1]):
		reverse_dict[pages[-1]].append(title.page_name)
	else:
		reverse_dict[pages[-1]] = [title.page_name]
	for i in xrange(0,len(pages)):
		data = setInDict(graph, pages[0:i+1], {})
	graph = data
print "reverse_dict"
print reverse_dict
pprint.pprint(graph)
name = 'battabo332'


# def keypaths(nested):
# 	for key, value in nested.iteritems():
# 		if isinstance(value, collections.Mapping) and len(value) != 0:
# 			print "is instance and length greater than zero"
# 			print value
# 			for subkey, subvalue in keypaths(value):
# 				#print [key]
# 				yield [key] + subkey, subvalue
# 		else:
# 			#print [key], value
# 			yield [key], value
# print list(keypaths(graph))
#reverse_dict = {keypath[0][-1]:keypath[0][:-1] for keypath in list(keypaths(graph))}
#print reverse_dict

# reverse_dict = {}
# for keypath, value in keypaths(graph):
# 	reverse_dict.setdefault(keypath[-1], []).append(keypath[:-1])

# print reverse_dict

# 7 and 10 or 9
#print reverse_dict

	# for i in xrange(len(pages)):
	# 	if index.has_key(pages[i]):
	# 		index = index[pages[i]]
	# 	else:
	# 		index[pages[i]] = {}

#Check the level 
# FieryProject, ExtraHelp

# if graph.has_key(pages[0]):
# 	if graph[0].has_key(pages[1])
# 		if graph[0][1].has_key[page[2]]
# return graph[0][1]


# def find_place(graph, pages):
# 	for i in xrange(len(pages)):
# 		if graph.has_key(pages[i]):
# 			graph = graph[key]
# 		else:
# 			return 

# 		return graph.index(key)
# 	else:
# 		return -1

# 	return index

# 	# if not graph.has_key(pages[-1]):
# 	# 	graph[pages[-1]] = []
# 	# if len(pages) < 2:
# 	# 	continue
# 	# elif graph.has_key(pages[-2]):
# 	# 	graph[pages[-2]].append(pages[-1])
# 	# else:
# 	# 	graph[pages[-2]] = [pages[-1]]
# print graph


class SectionPath(object):
    """Represents a path through the sections of a document tree."""

    def __init__(self, init_path):
        self.path = init_path

    def child(self):
        return SectionPath((1, self.path))
    child = property(child)

    def sibling(self):
        head, tail = self.path
        return SectionPath((head + 1, tail))
    sibling = property(sibling)

    def __str__(self):
        result = []
        path = self.path
        while path is not None:
            head, tail = path
            result.append(str(head))
            path = tail
        result.reverse()
        result.pop(1)
        return '.'.join(result)

start = SectionPath((1, None))

name = 'battabo332'
def print_toc(graph):
	text = ""
	open ('temp.txt', 'w').close()
	def recurse(sections, path, text, reverse_dict):
		for section in sections:
			# Unpack each tree node as (string, list) tuple.
			title, children = section, sections[section]
			print title
			#print reverse_dict[title]
			try:
				link = reverse_dict[title][0] 
				print link#Broken when there is two key values...returns the first one by default
				with open ('temp.txt', 'a') as page:
					text = '{}. [[{} | {}]]<<BR>>'.format(path, link.encode('utf-8'), title) 
					page.write(text)
				print '{}. [[{} | {} ]]<<BR>>'.format(path, link.encode('utf-8'), title)  
			except KeyError:
				pass
			# Print the current section number and its title.
			# Converting "path" to a string yields the section number.
			
			# Call this function recursively for each child, passing the
			# "child" property of the path.
			recurse(children, path.child, text, reverse_dict)
			# Advance the path to the next sibling.
			path = path.sibling
		# Call the recursive function, using the "start" path to begin
		# generating section numbers starting at "1".
	recurse(graph, start, "", reverse_dict)
	print text
        
    # Pass the recursive tree structure into the table of contents printer.
text = print_toc(graph)

def create_page(text, page_name):
	if Page(request, page_name).exists(): #should use isUnderlayPage/isDataPage
	    print "A page with the name {0} already exists".format(page_name)
	    #Do you want to continue
	    n_text = PageEditor(request, page_name).get_raw_body()
	    n_text += text
	    PageEditor(request, page_name).saveText(n_text, 0)
	    print "A page was created with the name {0}".format(page_name) #Is there already a table of contents there?
	else:    
		try: #Should be checking if permissions exist?
			PageEditor(request, page_name).saveText(text, 0)
			print "A page was created with the name {0}".format(page_name)
		except:
			pass
text = ""			
with open ('temp.txt', 'r') as page:
	text += page.read()
create_page(text, "whittamoo")

# def dfs(graph, starting_folder):
# 	text = ""
# 	stack = []
# 	visited = {}
# 	for key in graph.iterkeys():
# 		visited[key] = False
# 	level = 1
# 	path = []
# 	stack.append((starting_folder, level))
# 	while stack:
# 		page, level = stack.pop()
# 		if not visited[page]:
# 			text += format_link(page, level)
# 			level += 1
# 			stack.extend([(neighbour, level) for neighbour in graph[page] if not visited[neighbour]])
# 	print text
# 	return text

# def format_link(page_name, level):
# 	formatter = "=" * level
# 	return "{}[[{}]]\n".format(formatter, page_name)



#passed a starting folder
# startingfolder = "FieryProjectHomepage"
# contents = dfs(graph, startingfolder)
# create_page(contents, "binger")



# def traverse(startingfolder):
# 	pass

# def dfs_iterative(adjLists, starting_folder):
# 	stack = []
# 	stack.append(s)
# 	n = len(adjLists) #number of keys in the dictionary
# 	visited = []
# 	for i in range(0,n):
# 	    visited.append(False)
	     
# 	while(len(stack)>0):
# 	    v = stack.pop()
# 	    if(not visited[v]):
# 	        visited[v] = True
# 	        print(v, " ", end='')

# 	        # auxiliary stack to visit neighbors in the order they appear
# 	        # in the adjacency list
# 	        # alternatively: iterate through the adjacency list in reverse order
# 	        # but this is only to get the same output as the recursive dfs
# 	        # otherwise, this would not be necessary
# 	        stack_aux = []
# 	        for w in adjLists[v]:
# 	            if(not visited[w]):
# 	                stack_aux.append(w)
# 	        while(len(stack_aux)>0):
# 	            stack.append(stack_aux.pop())
                     

# class Node:
# 	def __init__(self, value):
# 		self.value = value
# 		self.adjacent_nodes = []


# 	#How many hits are there?
# 	#Number of slashes will tell you? 
# 	#pages.append(title.page_name)

# 	#weird = [title.page_name.rsplit('/', i) for i in xrange(title.page_name.count('/')+1)]
# 	#print weird
# 	#once.append(weird[:1])
# 	#pages = title.page_name.split('/')
# 	i = title.page_name.count('/')

# 	if levels.has_key(i):
# 		levels[i].add(title.page_name)
# 	else: 
# 		levels[i] = set([title.page_name])		
# 	print title.page_name
# print levelsif levels.has_key(i):
# 		levels[i].add(title.page_name)
# 	else: 
# 		levels[i] = set([title.page_name])	

# text = ""
# for i in xrange(max(levels.keys(), key=int))
# 	for page in levels[i]:
# 		text += format_link(page, i)
# 		if page in levels[i+1]
# #for page in level[i]:

# 	if page in levels.

# def check_page(page_name):


# def iterative_dfs(graph, start, path=[]):
#   '''iterative depth first search from start'''
#   q=[start]
#   while q:
#     v=q.pop(0)
#     if v not in path:
#       path=path+[v]
#       q=graph[v]+q
#   return path

# DFS(G,v)   ( v is the vertex where the search starts )
#          Stack S := {};   ( start with an empty stack )
#          for each vertex u, set visited[u] := false;
#          push S, v;
#          while (S is not empty) do
#             u := pop S;
#             if (not visited[u]) then
#                visited[u] := true;
#                for each unvisited neighbour w of u
#                   push S, w;
#             end if
#          end while
#       END DFS()

# #for each page in level 1 conduct a depth first search
# 	stack = []
# 	for page in search_result.hits:
# 		visited[page.page_name] = false
# 		stack.append(page.page_name)
# 		if stack:
# 			page = 


# def make_link(g,node1,node2): #function to construct the graph in JSOn like format
#     if node1 not in G:
#         G[node1]={}
#     (G[node1])[node2]=1
#     if node2 not in G:
#         G[node2]={}
#     (G[node2])[node1]=1
 
# G={} #initializing the empty grapgh
# connections = [('A','B'),('A','C'),('A','E'),('B','D'),('B','F'),('C','G'),('E','F')] #tuples representing the connections
 
# for x,y in connections:make_link(G,x,y) #constructing the graph using tuple representation
 
# print G
 
# def dfs(G,node,traversed):
#     traversed[node]=True #mark the traversed node
#     print "traversal:"+ node
#     for neighbour_nodes in G[node]: #take a neighbouring node
#         if neighbour_nodes not in traversed: #condition to check whether the neighbour node is already visited
#             dfs(G,neighbour_nodes,traversed) #recursively traverse the neighbouring node
 
# def start_traversal(G):
#     traversed = {} #dictionary to mark the traversed nodes
#     for node in G.keys(): #G.keys() returns a node from the graph in its iteration
#         if node not in traversed: #you start traversing from the root node only if its not visited
#             dfs(G,node,traversed); #for a connected graph this is called only once
 
# start_traversal(G)

# def dfs(i, ):
# 	unvisited = []

# 	for node in levels[i]: #page in this level
# 		if levels.has_key[i+1]: #while
# 			unvisited = unvisited.extend([page for page in level[i+1] if node in page]) #add all the unvisited pages
# 			while unvisited:

# 		else:


# 		unvisited 
# visted = []

	




