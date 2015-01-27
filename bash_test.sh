#!/bin/bash

#Test Create Groups

#1. Create Groups from line separated text file 
python create_group.py test_group.txt

#2. Create Groups from line separated text file with prefix specified
#python accessing_groups.py --create_group test_group.txt --prefix=prefixSpecified

#3 Create a single Group with members specified
#python accessing_groups.py --create_group --member_names Smurph16 frog3456

#4 Create a single Group with name specified
#python accessing_groups.py --create_group --group_name=bLAHblAH --member_names frog3456 tortoise4321

# Create groups with multiple files and default naming
#python accessing_groups.py --create_group test_group.txt test_group2.txt

# Create groups with multiple files and prefix naming
#python accessing_groups.py --create_group --prefix=ProjectVision test_group.txt

# Create groups with default naming and categorise them
#python accessing_groups.py --create_group --categorise=Project3 test_group.txt

# Remove all groups
#python remove_group.py -all 

# Remove group with name
#python accessing_groups.py --remove_group --group_name=5Group

# Remove group from middle of file
#python accessing_groups.py --remove_group --group_name=3Group

# Remove all groups with certain prefix
python accessing_groups.py --remove_group --prefix=ProjectVision

bash change_owner.sh
