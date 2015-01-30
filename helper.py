from tortus_project import TortusProjectCollection, TortusProject
from default import *
import sys, os, shutil

class ArgHelper:

    def __init__(self, args, parser):
        self.options = args #dictionary
        self.parser = parser

    def get_permissions(self):
        if not self.options['permissions'] is not None:
             default_permissions = raw_input(
                "The permissions for this file will be set to default values. Press Y to continue or any other key to halt program: ")
             if default_permissions == 'Y':
                permissions = 'read_only'
             else:
                print "Permissions can be set using the --permissions flag. See --help for more information"
                sys.exit()
        else:
            permissions = self.options['permissions']
        return permissions


    def is_valid_file(parser, arg):
        if not os.path.isfile(arg):
            parser.error('The file {} does not exist!'.format(arg))
        else:
            # File exists so return the filename
            return arg

    def check_for_page(self):
        elements = ['filenames', 'template', 'url']
        filtered_options = {k:v for k, v in self.options.items() if (k in elements)}
        if len([filtered_options[k] for k in filtered_options.keys() if not (filtered_options[k])]) != 2:
            self.parser.error ("Please specify exactly one file, url or a template to create a page from")
            sys.exit()

    def check_name(self):
        if (self.options['template'] and self.options['page_name'] is None):  
            name = raw_input("Please specify a page name: ")
        else:
            name = self.options['page_name']
        return name

    def get_project(self):
        if self.options['project'] is not None:
            project_name = self.options['project']
        else:
            default_project = raw_input(
                "This action will be carried out on the project DefaultProject. Press Y to proceed or any other key to cancel: ")
            if not default_project == "Y":
                sys.exit()
            project_name = "default"
        projects = TortusProjectCollection()
        if not (projects.project_exists(project_name) == 0): #Make the project if it doesn't exist
            mk_prj = raw_input(
                "This project does not exist yet. If you would like to create it, press Y to proceed or any other key to cancel: ")
            if mk_prj == 'Y':
                project = projects.tortus_project(
                    name =project_name, groups={}, args=self.options)
            else:
                return
        else:
            project = projects.tortus_project(
                name=project_name, groups={}, args=self.options)
        return (project, projects)

    def check_delete(self):
        if not (self.options['group_names'] or self.options['filenames']):
            self.parser.error("Must specify group_name in command line or path to file groups to be deleted")
            sys.exit()

    def check_create(self):
        if not (self.options['member_names'] or self.options['filenames']):
            self.parser.error("Must specify member names in command line or path to file containing names")
            sys.exit()

    def get_group_copy(self, name): #Should this be in some other class tortus_page?
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

