#!bin/bash

##These commands should be run from the tortus directory which should be located in your moin directory
##Project name must be specified for all commands
##Pages to be added to the wiki should be placed in a pages directory in the moin directory
##Templates should be added to the wiki in the pages/templates directory.
##See default.py to change these settings

#Create groups from a text file. Each member should be on a new line and each group should be separated by an empty newline
python cmd_create_group.py --project project_name ./examples/test__group_creation.txt

#Create groups from a text file with a specified naming prefix. Format of text file should be as above
python cmd_create_group --project project_name --group_name dragons ./examples/test__group_creation.txt

#Delete groups from a text file. Each group should be on a line of its own
python cmd_remove_group --project project_name ./examples/test_remove_group.txt

#Delete groups with a specified group prefix from a project. Do we need this?
#python cmd_remove_group --project project_name --group_name dragons

#Delete groups with groups specified by name in the command line
python cmd_remove_group --project project_name --group_names 1 2 4

#Modify groups by adding a new group, deleting a group or editing the members. The easiest way to
#do this is to create a copy of the groups file from the project first
python cmd_modify_group --project project_name --get_file
#Make edits and then pass the file to the command again
python cmd_modify_group --project project_name ./groups/groups

#Make a page from file. The page must be stored in the pages file of the tortus directory
python cmd_create_page.py --project project_name newpage.txt

#Make a page copy for each group from file. The page must be stored in the pages file of the tortus directory 
python cmd_create_page.py --project project_name --group_names 3 4 5 --central_page newpage.txt

#Make a page copy for each individual from file. The page must be stored in the pages file of the tortus directory
python cmd_create_page.py --project project_name --user_names member1 member2 --central_page newpage.txt




