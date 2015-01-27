# -*- coding: iso-8859-1 -*-
"""
MoinMoin - creates pages for existing user/group accounts

@copyright: 2009 MoinMoin:ReimarBauer
@license: GNU GPL, see COPYING for details.

-----------------------------------------------------------
Command - Create CentralPage
-----------------------------------------------------------
"""

from MoinMoin import user
from MoinMoin.Page import Page
from MoinMoin.PageEditor import PageEditor
from MoinMoin.script import MoinScript
from MoinMoin.mail.sendmail import encodeSpamSafeEmail
from tortus_command import TortusScript
from tortus_page import TortusPage
from MoinMoin.web.contexts import ScriptContext
from default import *
import argparse, os

class Tortus(TortusScript):

    def __init__(self):

        self.parser = argparse.ArgumentParser()
        self.request = ScriptContext()
        self.parser.add_argument("--page_name", help="the name of the page being created")
        self.parser.add_argument("-all", "--show_to_all", help="flag if all users should have this page as a quicklink", action="store_true")
        self.parser.add_argument("--group_names", help="the name of the groups to create a quicklink for", action="store", nargs="*")
        self.parser.add_argument(dest="filenames", help="the names of the files to create pages from", nargs='*')
        self.parser.add_argument("--template", help="if a page should be created for each group with the project template....specify template?") #efault="homework_template"
        self.parser.add_argument("--permissions", help="specify the permissions for the page. ", choices=['instructor_read_only', 'read_only', 
        'user_write_only', 'group_write_only'])
        self.parser.add_argument("--url", help="the url of the page you would like to push to users")
        self.parser.add_argument("--subpage", help="")
        self.args = self.parser.parse_args()
        self.page = TortusPage()

    def run(self):
            
        name = None

        # One of create, modify or delete must be specified
        if not (self.args.filenames or self.args.template or self.args.url):
            self.parser.error ("Please specify a file, url or a template to create a page from")
            return
        if not (self.args.permissions):
             default_permissions = raw_input("The permissions for this file will be set to read_only. Press Y to continue or any other key to halt program\n")
             if default_permissions == 'Y':
                self.args.permissions = 'read_only'
             else:
                print "Permissions can be set using the --permissions flag. See --help for more information"
        #This is messy. Tidy it up
        if (self.args.filenames and self.args.template) or (self.args.filenames and self.args.url) or (self.args.url and self.args.template):
            self.parser.error("You can only specify a filename, a template or a url")
            return
        if not (self.args.filenames or self.args.page_name or self.args.url):
            name = raw_input("Please specify a page name: ")
        elif self.args.page_name:
            name = args.page_name
        #elif args.group_names:
            #check execution was completed
            #find group
            #retrieve members
            #call quicklinks
        if self.args.template:
            template = self.args.template
            file_path = self.page.get_file_path(template, template=1)
            print file_path
            self.page.add_from_file(file_path, self.args, name)     
        elif self.args.filenames:
            for fname in self.args.filenames:
                if name is None:
                    name = os.path.splitext(fname)[0]
                    print name
                file_path = self.page.get_file_path(fname, file=1)
                self.page.add_from_file(file_path, self.args, name)
        elif self.args.url:
            self.page.process_url_page(self.args)
    #elif args.template
# HomePage Template
#parser.add_argument("--template", help="if a page should be created for each group with the project template....specify template?")
        

if __name__ == "__main__":
    command = Tortus()
    command.run()

class (MoinScript):


    def __init__(self, argv, def_values):
        MoinScript.__init__(self, argv, def_values)

        self.parser.add_option(
            "-u", "--user", dest="homepage_creator",
            help="User as whom the homepage creation operation will be performed as."
            )

        self.parser.add_option(
            "-t", "--template_page", dest="template_page",
            help="The template page which should be used for the homepage creation"
            )

        self.parser.add_option(
            "-n", "--name", dest="user_homepage",
            help="The name of the user the homepage should be created for."
            )

        self.parser.add_option(
            "-g", "--group", dest="name_of_group_page",
            help="The name of the group page to select users for creating their homepages."
            )

        self.parser.add_option(
            "-a", "--all-users", dest="all_users", action="store_true",
            help="The name of the group page to select users for creating their homepages."
            )

    def write_homepage(self, account, homepage_text):
        # writes the homepage
        if account.exists() and not account.disabled and not Page(self.request, account.name).exists():
            userhomepage = PageEditor(self.request, account.name)
            try:
                userhomepage.saveText(homepage_text, 0)
                print "Central page created for %s." % account.name
            except userhomepage.Unchanged:
                print "You did not change the page content, not saved!"
            except userhomepage.NoAdmin:
                print "You don't have enough rights to create the %s page" % account.name
        else:
            print "Page for %s already exists or account is disabled or user does not exist." % account.name

    def mainloop(self):
        # we don't expect non-option arguments
        self.init_request()
        request = self.request
        # Checks for a template page and sets homepage_default_text
        if self.options.template_page and Page(self.request, self.options.template_page).exists():
            homepage_default_text = Page(self.request, self.options.template_page).get_raw_body()
            # replace is needed because substitution is done for request.user
            # see option --user
            homepage_default_text = homepage_default_text.replace('@ME@', "%(username)s")
            homepage_default_text = homepage_default_text.replace('@EMAIL@', "<<MailTo(%(obfuscated_mail)s)>>")
        else:
            homepage_default_text = '''#acl %(username)s:read,write,delete,revert Default
#format wiki

== %(username)s ==

Email: <<MailTo(%(obfuscated_mail)s)>>
## You can even more obfuscate your email address by adding more uppercase letters followed by a leading and trailing blank.

----
CategoryHomepage
'''
        # Check for user
        if self.options.homepage_creator:
            uid = user.getUserId(request, self.options.homepage_creator)
            request.user = user.User(request, uid)
        # Check for Group definition
        members = []
        if self.options.user_homepage:
            members = [self.options.user_homepage, ]
        elif self.options.name_of_group_page:
            members = request.groups.get(self.options.name_of_group_page, [])
        elif self.options.all_users:
            uids = user.getUserList(request)
            members = [user.User(request, uid).name for uid in uids]

        if not members:
            print "No user selected!"
            return

        # loop through members for creating homepages
        for name in members:
            uid = user.getUserId(request, name)
            account = user.User(request, uid)
            homepage_text = homepage_default_text % {
                                                 "username": account.name,
                                                 "obfuscated_mail": encodeSpamSafeEmail(account.email)
                                                 }
            self.write_homepage(account, homepage_text)
