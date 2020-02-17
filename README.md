# metagenome_pipeline

**Licence:	GNU General Public License v3.0 (copy provided in directory)**<br />
Author:		Tom van Wijk<br />
Contact:	tom_van_wijk@hotmail.com<br />

### DESCRIPTION

This pipeline is developed to automate the quality control, processing and analysis
of large datasets of metagenome samples. Currently only Illumina paired-end data is supported.<br />

### REQUIREMENTS

-	Linux operating system. This software is developed on Linux Ubuntu 16.04<br />
	**Experiences when using different operating systems may vary.**
	A minimum of 8 cpu's and 64 GB of RAM are recommended
-	python v2.7.x
-	python libraries as listed in the import section of metagenome_pipeline.py
-	FastQC v0.11.7+ https://www.bioinformatics.babraham.ac.uk/projects/fastqc/
-	MultiQC v1.5+ https://multiqc.info/
-	Seqkit 0.10.1+ https://bioinf.shenwei.me/seqkit/download/
-	MetaPhlan2 v2.7.7+ https://bitbucket.org/biobakery/metaphlan2/src/default/
-	GROOT resistome profiler https://github.com/will-rowe/groot


### INSTALLATION

-	Clone the metagenome_pipeline repository to the desired location on your system.<br />
	`git clone https://github.com/Papos92/metagenome_pipeline.git`
-	Add the location of the metagenome_pipeline repository to the PATH variable:<br />
	`export PATH=$PATH:/path/to/metagenome_pipeline`<br />
	(It is recommended to add this command to your ~/.bashrc file)
-	Create path variable META_DB to the GROOT reference subdirectory:<br />
	`export META_DB=/path/to/metagenome_pipeline/groot_db`<br />
	(It is recommended to add this command to your ~/.bashrc file)
-	Download the GROOT reference databases by running `groot_download_db.py`<br />
	This will download the following reference databases to the groot_db directory:<br />
	`arg-annot`, `card`, `groot-core-db`, `groot-db` and `resfinder`.<br />
-	Index the GROOT reference databases by running `groot_index_db.py` <br />
	With default parameters, this will generate the index files for 2x150 bp data.<br />

### USAGE

Start the pipeline with the following command:

`dada2_amplicon_pipeline.py -i 'inputdir' -o 'outputdir' -t 'threads' -d 'database' -l 'length'`

-	**'inputdir':**	location of input directory. (required)<br />
			Should only contain the compressed (.fastq.gz) sequence files containing the
			raw sequences of the forward and reverse reads.	For each sample,
			these fastq files need to be named with an '_R1' or '_R2' tag respectively
			and  be furthermore identical.

-	**'outputdir':**	location of output directory. (optional)<br />
			When not defined, a subdirectory with a timestamp will be created inside the
			input directory.<br />

-	**'threads':**	Number of cpu threads used.<br />
			default = 6<br />

-	**'database':**	Reference database for GROOT resistome profiler.<br />
			Using the recommended default option will run this analysis twice with
			both the `resfinder` and `card` databases and store the results in separate directories.
			Other options that can be used in this parameter are:<br/>
			`arg-annot`, `card`, `groot-core-db`, `groot-db` and `resfinder`.<br />
			To redownload the database or download more databases when they are supported by groot
			in future updates, please use the `groot_download_db.py` script in this repository.<br />

-	**'length'**	Length of the reads in the dataset.<br />
			Default = 150. This needs to be accurate by amargin of max. 10 bp.<br />
			This value is referenced to use the correct database index file during the GROOT analysis. <br/>
			If you wish to use a different read length index. Please generate an index file for the
			databases with the `groot_index_db.py` script in this repository. <br />
