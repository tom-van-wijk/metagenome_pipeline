#!/usr/bin/env python


# Name:         groot_index_db.py
# Author:       Tom van Wijk - RIVM Bilthoven
# Date:         24-06-2019
# Licence:      GNU General Public License v3.0 (copy provided in directory)

# For detailed information and instruction on how to install and use this software
# please view the included "READNE.md" file in this repository


# import python libraries
from argparse import ArgumentParser
import os
import sys


# Function to parse the command-line arguments
# Returns a namespace with argument keys and values
def parse_arguments(args):
	parser = ArgumentParser(prog="groot_index_db.py")
	parser.add_argument("-t", "--threads", dest = "threads",
		action = "store", default = 6, type = int,
		help = "Number of threads to be used (default=6)")
	parser.add_argument("-l", "--length", dest = "length",
		action = "store", default = 150, type = int,
		help = "Length of query reads (default=150)")
	return parser.parse_args()


# MAIN function
def main():
	# parse command line arguments
	args = parse_arguments(sys.argv)
	for db in ["arg-annot", "resfinder", "card", "groot-db", "groot-core-db"]:
		os.system("rm -rf %s/%s_index_l-%s" % (os.environ['META_DB'], db, str(length)))
		os.system("groot index -i %s/%s.90 -p %s -l %s -o %s/%s_index_l-%s" % (os.environ['META_DB'],
																		db,
																		str(args.threads),
																		str(args.length),
																   		os.environ['META_DB'],
																		db,
																   		str(args.length)))
	

main()
