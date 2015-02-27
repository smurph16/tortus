from tortus_project import TortusProjectCollection, TortusProject
from default import *
import sys, os, shutil

class ArgHelper:
    """This class adds common functionality for the commands"""

    def __init__(self, args, parser):
        self.options = args #dictionary
        self.parser = parser

    def get_permissions(self):
        """Sets the default permissions for an action
        @return permissions: the permission key for the action"""
        if not self.options['permissions'] is not None:
             default_permissions = raw_input(
                "The permissions for this file will be set to default values. Press Y to continue or any other key to halt program: ")
             if default_permissions == 'Y':
                permissions = 'default'
             else:
                print "Permissions can be set using the --permissions flag. See --help for more information"
                sys.exit()
        else:
            permissions = self.options['permissions']
        return permissions


    def is_valid_file(arg):
        """Check that the file given is a valid path
        @....""" #Currently not doing this at this point. ? Should it be done here
        if not os.path.isfile(arg):
            self.parser.error('The file {} does not exist!'.format(arg))
        else:
            # File exists so return the filename
            return arg

    def check_for_page(self):
        """Check that a page to add has been specified through an argument"""
        elements = ['filenames', 'template', 'url']
        filtered_options = {k:v for k, v in self.options.items() if (k in elements)}
        if len([filtered_options[k] for k in filtered_options.keys() if not (filtered_options[k])]) != 2:
            self.parser.error ("Please specify exactly one file, url or a template to create a page from")
            sys.exit()

    def check_name(self):
        """Check that a name has been specified for a page through an argument. The
        name will be deduced if a filename or url has been provided instead"""
        if (self.options['template'] and self.options['page_name'] is None):  
            name = raw_input("Please specify a page name: ")
        else:
            name = self.options['page_name']
        return name

    def get_project(self, create=0):
        """Retrieve a project to perform an action on. If the project doesn't exist,
        it is created. If a project is not specified the default project can be used
        @return: tuple containing specified project and collection of projects"""
        if self.options['project'] is not None:
            project_name = self.options['project']
        else:
            default_project = raw_input(
                "This action will be carried out on the project DefaultProject. Press Y to proceed or any other key to cancel: ")
            if not default_project == "Y":
                sys.exit() #That didn't work
            project_name = "default"
        projects = TortusProjectCollection()
        if not (projects.project_exists(project_name) == 0) and create == 0:
            print "This project does not exist yet."
            sys.exit()
        if not (projects.project_exists(project_name) == 0): #Make the project if it doesn't exist
            mk_prj = raw_input(
                "This project does not exist yet. If you would like to create it, press Y to proceed or any other key to cancel: ")
            if mk_prj == 'Y':
                project = projects.tortus_project(
                    name =project_name, groups={}, args=self.options)
            else:
                sys.exit()
        else:
            project = projects.tortus_project(
                name=project_name, groups={}, args=self.options)
        return (project, projects)

    def check_delete(self):
        """Checks if group_names or a file containing group names has been given as an argument""" #Too many here
        if not (self.options['group_names'] or self.options['filenames'] or self.options['all'] or self.options['group_prefix']):
            self.parser.error("Must specify group_name in command line or path to file groups to be deleted")
            sys.exit()

    def check_create(self):
        """Checks if member names or filenames have been specified to create groups with"""
        if not (self.options['member_names'] or self.options['filenames']):
            self.parser.error("Must specify member names in command line or path to file containing names")
            sys.exit()

    def get_group_copy(self, name): #Should this be in some other class tortus_page?s
        """Creates a copy of the current groups in a project and places it in the current directory
        for the user to modify
        @param name: the name of the project the groups are being modified from"""
        if self.options['get_file']:
            groups_path = os.path.join(project_files, name, 'groups', 'groups')
            retain_file = os.path.join(os.getcwd(), "{0}_groups.txt".format(name))
            try:
                shutil.copyfile(groups_path, retain_file)
                print retain_file
            except shutil.Error as e:
                print 'A groups file was not made. Error %s' % e
            except OSError as e:
                print 'A groups file was not made. Error: %s' % e
            except IOError as e:
                print ("Error: The groups file could not be found: %s" % e.strerror)
            finally:
                sys.exit()

    def check_users(self):
        """Check that members to add a link to have been specified through an argument"""
        elements = ['all', 'project', 'group_names', 'user_names']
        filtered_options = {k:v for k, v in self.options.items() if (k in elements)}
        users = [filtered_options[k] for k in filtered_options.keys() if not (filtered_options[k])]
        if not len(users) < 4: 
            self.parser.error("Please specify at least one of project, group_names, user_names")
            sys.exit()

    def check_links(self):
        if not (self.options['filename'] or self.options['pages']):
            self.parser.error("Please specify pages or a filename containing pages to link")
            sys.exit()
