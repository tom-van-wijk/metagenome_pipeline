#!/usr/bin/env python


# Name:         groot_download_db.py
# Author:       Tom van Wijk - RIVM Bilthoven
# Date:         24-06-2019
# Licence:      GNU General Public License v3.0 (copy provided in directory)

# For detailed information and instruction on how to install and use this software
# please view the included "READNE.md" file in this repository


# import python libraries
import os
import sys


# MAIN function
def main():
	os.system("mkdir -p %s" % os.environ['META_DB'])
	for db in ["arg-annot", "resfinder", "card", "groot-db", "groot-core-db"]:
		os.system("rm -rf %s/%s.90" % (os.environ['META_DB'], db))
		os.system("groot get -d %s -i 90 -o %s" % (db, os.environ['META_DB']))	
	

main()
