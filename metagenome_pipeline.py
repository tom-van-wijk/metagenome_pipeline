#!/usr/bin/env python


# Name:         metagenome_pipeline.py
# Author:       Tom van Wijk - RIVM Bilthoven
# Date:         13-10-2019
# Licence:      GNU General Public License v3.0 (copy provided in directory)

# For detailed information and instruction on how to install and use this software
# please view the included "READNE.md" file in this repository


# import python libraries
from argparse import ArgumentParser
import logging
import logging.handlers
import os
import sys
import random


# Function to parse the command-line arguments
# Returns a namespace with argument keys and values
def parse_arguments(args, log):
	log.info("Parsing command line arguments...")
	parser = ArgumentParser(prog="metagenome_pipeline.py")
	parser.add_argument("-i", "--indir", dest = "input_dir",
		action = "store", default = None, type = str,
		help = "Location of input directory (required)",
		required = True)
	parser.add_argument("-o", "--outdir", dest = "output_dir",
		action = "store", default = "inputdir", type = str,
		help = "Location of output directory (default=inputdir)")
	parser.add_argument("-t", "--threads", dest = "threads",
		action = "store", default = 6, type = int,
		help = "Number of threads to be used (default=6)")
	parser.add_argument("-d", "--database", dest = "groot_db",
		action = "store", default = "default", type = str,
		help = "Database for AMR profiling. supported: arg-annot, resfinder, card, groot_db, groot_core_db. Default: resfinder/card")
	parser.add_argument("-l", "--length", dest = "length",
		action = "store", default = 150, type = int,
		help = "Length of query reads (default=150)")
	return parser.parse_args()


# Function creates logger with handlers for both logfile and console output
# Returns logger
def create_logger(logid):
	# create logger
	log = logging.getLogger()
	log.setLevel(logging.INFO)
	# create file handler
	fh = logging.FileHandler(str(logid)+'_metagenome.log')
	fh.setLevel(logging.DEBUG)
	fh.setFormatter(logging.Formatter('%(message)s'))
	log.addHandler(fh)
	# create console handler
	ch = logging.StreamHandler()
	ch.setLevel(logging.INFO)
	ch.setFormatter(logging.Formatter('%(message)s'))
	log.addHandler(ch)
	return log


# takes a lication of input data
# returns a dictionary with sample names as keys and lists of the R1 and R2 file names as values
# returns a list of sample files
def find_files(input_dir):
	sample_dict = {}
	sample_file_list = []
	filelist = list_directory(input_dir, "files", 1)
	for file in filelist:
		if '_R1' in file and file in filelist and file.replace('_R1', '_R2') in filelist:
			R1_file = input_dir+"/"+file
			R2_file = input_dir+"/"+file.replace('_R1', '_R2')
			prefix = file.split("_R1")[0].replace(".","_").replace(" ","_")
			# adding sample to dictionary
			sample_dict[prefix]=[R1_file, R2_file]
			# adding sample files to list
			sample_file_list.append(R1_file)
			sample_file_list.append(R2_file)
	# unzipping fastqc reports
	return sample_dict, sample_file_list


# Function creates a list of files or directories in <inputdir>
# on the specified directory depth
def list_directory(input_dir, obj_type, depth):
	dir_depth = 1
	for root, dirs, files in os.walk(input_dir):
		if dir_depth == depth:
			if obj_type ==  'files':
				return files
			elif obj_type == 'dirs':
				return dirs
		dir_depth += 1


# Function to generate a FastQC rapport of each filepair and a MultiQC report for all data
# Takes a dictionaru containing locations where the .fastq files are located and a output_dir for storage output
def quality_control(sample_dict, output_dir):
	os.system("mkdir -p "+output_dir+"/quality_control/fastqc")
	for key in sorted(sample_dict):
		R1_file = sample_dict[key][0]
		R2_file = sample_dict[key][1]
		print R1_file, R2_file
		# create a fastCQ quality report
		os.system("fastqc "+R1_file+" "+R2_file+" -o "+output_dir+"/quality_control/fastqc")
	# unzipping fastqc reports
	files = list_directory(output_dir+"/quality_control/fastqc", "files", 1)
	for file in files:
		if file.endswith(".zip"):
			os.system("unzip "+output_dir+"/quality_control/fastqc/"+file
					  +" -d "+output_dir+"/quality_control/fastqc/"+file.replace('.zip', ''))
	# create multiqc report
	os.system("multiqc "+output_dir+"/quality_control/fastqc/ -o "+output_dir+"/quality_control")

	
# Function that generates SeqKit statistics off all files in a given list
def data_statistics(filelist, threads, output_dir):
	os.system("mkdir -p "+output_dir+"/data_statistics")
	command = "seqkit stats --all"
	for file in sorted(filelist):
		command += " %s" % file
	command += " -e -j %s -o %s/data_statistics/seqkit_data_statistics.txt" % (str(threads), output_dir)
	print "\n"+command+"\n"
	os.system(command)
	
	
# Function that classifies the raw reads using metaphlan2
# Takes a dictionary with file locations as input
def classify_reads(sample_dict, threads, output_dir):
	os.system("mkdir -p "+output_dir+"/metaphlan2")
	profiles = []
	# classify reads
	for key in sorted(sample_dict):
		os.system("metaphlan2.py %s,%s --bowtie2out %s --nproc %s --input_type fastq > %s" % (sample_dict[key][0],
			sample_dict[key][1],
			output_dir+"/metaphlan2/"+key+"_metagenome.bowtie2.bz2",
			str(threads),
			output_dir+"/metaphlan2/"+key+"_metagenome_profile.txt"))
	# merge profiles
	os.system("merge_metaphlan_tables.py %s/metaphlan2/*_metagenome_profile.txt > %s/metaphlan2/merged_profiles_table.txt" % (output_dir,
																															  output_dir))

# Function to profile AMR genes with groot
# Takes a dictionary with file locations, no. of threads, groot database, read lengths and output dir as input
# Writes output to /outdir/AMR_profiles
def profile_amr(sample_dict, threads, groot_db, length, outdir, log):
	os.system("mkdir -p "+outdir+"/AMR_profiles/temp")
	# validate database and index existance
	dbs = list_directory(os.environ['META_DB'], "dirs", 1)
	valid = "No"
	valid_db = ""
	log.info("checking database:\t"+groot_db)
	for db in dbs:
		if db.startswith(groot_db) == True and db.endswith('l-'+str(length)) == True: # and "_index_" in db == True
			log.info("database found:\t"+db)
			valid = "Yes"
			valid_db = db
	if valid == "No":
		log.warning("Indexed database:\t%s_index_l-%s not found, please consult manual on how to download and index the databases." % (groot_db,
																																   str(length)))
	else:
		# iterate over filepairs in dict to process them with groot
		for key in sorted(sample_dict):
			# command to unzip the filepairs and pipe into groot align
			command = "gunzip -c %s | groot align -i %s -p %s -y %s > %s" % (sample_dict[key][0]+" "+sample_dict[key][1],
				os.environ['META_DB']+"/"+valid_db,
				str(threads),
				outdir+"/logfiles/groot/"+key+"_"+groot_db+"_l-"+str(length)+"_groot-align.log",
				outdir+"/AMR_profiles/"+key+"_"+groot_db+"_l-"+str(length)+"_ARG-reads.bam")
			print "\n"+command
			os.system(command)
			os.system("mv groot-graphs-* "+outdir+"/AMR_profiles/temp/")
			# command to generate groot report from alignment files
			command2 = "groot report -i %s -y %s > %s" % (outdir+"/AMR_profiles/"+key+"_"+groot_db+"_l-"+str(length)+"_ARG-reads.bam",
														outdir+"/logfiles/groot/"+key+"_"+groot_db+"_l-"+str(length)+"_groot-report.log",
														outdir+"/AMR_profiles/"+key+"_"+groot_db+"_l-"+str(length)+"_AMR-profile.txt")
			print "\n"+command2
			os.system(command2)
					
	
# Function closes logger handlers
def close_logger(log):
	for handler in log.handlers:
		handler.close()
		log.removeFilter(handler)


# MAIN function
def main():
	# create logger
	logid = random.randint(99999, 9999999)
	log = create_logger(logid)
	# parse command line arguments
	args = parse_arguments(sys.argv, log)
	# creating output directory
	if args.output_dir == 'inputdir':
		outdir = os.path.abspath(args.input_dir+"/metagenome_pipeline_output")
	else:
		outdir = os.path.abspath(args.output_dir)
	log.info("output directory: "+outdir)
	# create output dir
	os.system("mkdir -p "+outdir+"/logfiles/groot")
	# Create dictionary of input files
	sample_dict, sample_file_list = find_files(args.input_dir)
	print "\n"
	for key in sorted(sample_dict):
		print "%s:\n%s" % (key, sample_dict[key])
	print "\n"+str(sorted(sample_file_list))+"\n"
	# Generate FastQC and MultiQC Quality reports
	quality_control(sample_dict, outdir)
	# Generate Seqkit statistics
	data_statistics(sample_file_list, args.threads, outdir)
	# Classify reads
	classify_reads(sample_dict, args.threads, outdir)
	# Generate AMR profiles
	if args.groot_db == "default":  
		profile_amr(sample_dict, args.threads, "resfinder", args.length, outdir, log)
		profile_amr(sample_dict, args.threads, "card", args.length, outdir, log)
	else:
		profile_amr(sample_dict, args.threads, args.groot_db, args.length, outdir, log)
	# close logger handlers
	log.info("\nClosing logger and finalising metagenome_pipeline.py")
	close_logger(log)
	# move logfile to output directory
	os.system("mv "+str(logid)+"_metagenome.log "+outdir+"/logfiles/")


main()
