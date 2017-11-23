# default settings for bash and Python scripts
# for attributes that are external to the program

# ~~~~~ DEPLOYMENT SETTINGS ~~~~~ #
# settings used for setting up a new clinical NGS580 analysis

# directory to look for output from the NextSeq
sequencer_directory="/ifs/data/molecpathlab/quicksilver"

# comma-delimited string of filenames to copy from the sequencer_directory over to the analysis dir, if present
sequencer_files="RunParameters.xml,SampleSheet.csv"

# URL to use for cloning the snsxt repo
snsxt_repo_URL="https://github.com/NYU-Molecular-Pathology/snsxt.git"

# command to use when cloning the repo
git_clone_command="git clone --recursive"

# parent directory to create new analysis in
analysis_dir="/ifs/data/molecpathlab/NGS580_WES"

# name of the symlink to create to the fastq dir for an analysis
fastq_linkname="fastq"
