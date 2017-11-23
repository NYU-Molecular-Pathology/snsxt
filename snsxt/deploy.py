#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script for preparing a new snsxt analysis directory. Uses ``settings.py`` located in the main repo dir to configure a new analysis based on files from locations on the server. This script will:

- check the ``sequencer_directory`` (e.g. NextSeq output location) for a run matching the provided ID

-


"""
# ~~~~~ LOGGING ~~~~~~ #
import os
import sys
from util import log
# path to this script's dir
scriptdir = os.path.dirname(os.path.realpath(__file__))
# snsxt/snsxt/

parentdir = os.path.dirname(scriptdir) # this script's parent dir
# snsxt/

# name of this script
scriptname = os.path.basename(__file__)
script_timestamp = log.timestamp()
# path to parent dir 2 levels above this script
snsxt_parent_dir = os.path.realpath(os.path.dirname(os.path.dirname(__file__)) )
# /ifs/data/molecpathlab/scripts/snsxt/


# set a timestamped log file for debug log
log_file = os.path.join(snsxt_parent_dir, 'logs', '{0}.{1}.log'.format(scriptname, script_timestamp))
email_log_file = os.path.join(snsxt_parent_dir, 'logs', '{0}.{1}.email.log'.format(scriptname, script_timestamp))

# logging config files
primary_config_yaml = os.path.join(scriptdir, 'logging.yml')
backup_config_yaml = os.path.join(scriptdir, "basic_logging.yml")

# set  log module objects
log.log_file = log_file
log.email_log_file = email_log_file

logpath = log._logpath
"""
Bound function from ``log`` module
"""

email_logpath = log._email_logpath
"""
Bound function from ``log`` module
"""
logger = log.logger_from_configs(name = __name__, primary_config_yaml = primary_config_yaml, backup_config_yaml = backup_config_yaml, logger_name = 'deploy')
log.print_filehandler_filepaths_to_log(logger)

# ~~~~ LOAD MORE PACKAGES ~~~~~~ #
# load the `settings.py` from the parent directory
sys.path.insert(0, parentdir)
import settings
sys.path.pop(0)
import argparse
from util import tools
from util import find
import _exceptions as _e
import shutil


# ~~~~~ FUNCTIONS ~~~~~~ #
def find_sequencer_dir(analysis_id):
    """
    Searches for a ``sequencer_dir`` subdirectory matching the passed ``analysis_id``

    Parameters
    ----------
    analysis_id: str
        ID of sequencer output directory to use as input for the new analysis

    Returns
    -------
    str
        path to the sequencer subdirectory containing the analysis
    """
    sequencer_output_path = os.path.join(settings.sequencer_directory, str(analysis_id))
    if not tools.item_exists(item = sequencer_output_path, item_type = 'dir'):
        raise _e.AnalysisFileMissing(message = 'sequencer_output_path does not exist: {0}'.format(sequencer_output_path), errors = '')
    return(sequencer_output_path)

def fastq_present(search_dir):
    """
    Checks that '.fastq.gz' files are present in a directory

    Parameters
    ----------
    search_dir: str
        path to directory to search

    Returns
    -------
    bool
        ``True`` or ``False`` if any .fastq.gz file was found

    """
    matches = None
    # check that .fastq files are present in the output
    matches = find.find(search_dir = search_dir, inclusion_patterns = ('*.fastq.gz',), search_type = 'file', num_limit = 1)
    return(bool(matches))

def validate_sequencer_dir(sequencer_output_path):
    """
    Runs validations against the sequencing data output directory. Raises an exception if an error is found

    Parameters
    ----------
    sequencer_output_path: str
        path to directory to search
    """
    if not fastq_present(search_dir = sequencer_output_path):
        raise _e.AnalysisFileMissing(message = 'sequencer_output_path does not contain .fastq.gz files: {0}'.format(sequencer_output_path), errors = '')
    # add more validations here

def find_fastq_parent_dir(sequencer_output_path):
    """
    Searches for the subdirectory containing .fastq.gz files. If .fastq.gz files are not found two levels deep in the passed ``sequencer_output_path``, then a subdirectory containing .fastq.gz files will be returned, if found. Otherwise, raises an exception if no .fastq.gz files could be found.

    Parameters
    ----------
    sequencer_output_path: str
        path to directory to search

    Returns
    -------
    str
        path to the directory with .fastq files to use for the ``sns`` analysis

    Notes
    -----
    Ignores 'Undetermined' .fastq files
    """
    inclusion_patterns = ('*.fastq.gz',)
    exclusion_patterns = ('*Undetermined*',)

    # search just the top 2 levels
    matches = []
    matches = find.find(search_dir = sequencer_output_path,
                        inclusion_patterns = inclusion_patterns,
                        exclusion_patterns = exclusion_patterns,
                        search_type = 'file',
                        num_limit = 1,
                        level_limit = 2,
                        match_mode = "any")
    if len(matches) > 0:
        logger.debug('Found .fastq files near the top level of the sequencer_output_path, returning sequencer_output_path: {0}'.format(sequencer_output_path))
        return(sequencer_output_path)

    # search deeper; this might take a while
    logger.debug('.fastq files were not found near the top level of the sequencer_output_path, searching deeper...')
    matches = []
    matches = find.find(search_dir = sequencer_output_path,
                        inclusion_patterns = inclusion_patterns,
                        exclusion_patterns = exclusion_patterns,
                        search_type = 'file',
                        num_limit = 1,
                        match_mode = "any")
    if len(matches) > 0:
        fastq_dir = os.path.dirname(matches[0])
        logger.debug('Found .fastq files in directory: {0}\nThis directory will be used for the sns analysis'.format(fastq_dir))
        return(fastq_dir)
    else:
        raise _e.AnalysisFileMissing(message = 'sequencer_output_path does not contain .fastq.gz files: {0}'.format(sequencer_output_path), errors = '')

def make_results_ID():
    """
    Returns a 'results_id' based on the current timestamp

    Returns
    -------
    str
        a timestamped ID for the results identifier
    """
    return('results_{0}'.format(tools.timestamp2()))

def copy_sequencer_files(analysis_dir, sequencer_output_path, other_files = None):
    """
    Copies files specified in ``settings.py`` from the ``sequencer_output_path`` directory to the ``analysis_dir``

    Parameters
    ----------
    sequencer_output_path: str
        path to the directory containing the sequencer output to search in
    analysis_dir: str
        path to the directory to copy analysis files to
    other_files: list
        a list of other files to copy over to the analysis_dir, or ``None``
    """
    # get the file basenames to search for from the settings
    sequencer_files = settings.sequencer_files.split(',')
    # get the files form the sequencer_dir to copy over
    copy_files = []
    for sequencer_file in sequencer_files:
        logger.debug(sequencer_file)
        inclusion_patterns = (sequencer_file,)
        matches = find.find(search_dir = sequencer_output_path,
                            inclusion_patterns = inclusion_patterns,
                            search_type = 'file',
                            num_limit = 1,
                            match_mode = "any")
        logger.debug(matches)
        if len(matches) > 0:
            copy_files.append(matches[0])

    # include any other files passed
    if other_files:
        for other_file in other_files:
            copy_files.append(other_file)

    # copy all the files over
    for copy_file in copy_files:
        file_basename = os.path.basename(copy_file)
        output_path = os.path.join(analysis_dir, file_basename)
        logger.debug('Copying file from:\n{0}\nto:\n{1}'.format(copy_file, output_path))
        shutil.copy2(copy_file, output_path)


def clone_snsxt(target_dir):
    """
    Creates a ``git`` clone of the ``snsxt`` repo in the target directory

    Parameters
    ----------
    target_dir: str
        path to the location to clone the new copy of the repo
    """
    snsxt_repo_URL = settings.snsxt_repo_URL
    git_clone_command = settings.git_clone_command
    command = '{0} {1}'.format(git_clone_command, snsxt_repo_URL)
    # git clone --recursive https://github.com/NYU-Molecular-Pathology/snsxt.git
    with tools.DirHop(target_dir) as d:
        run_cmd = tools.SubprocessCmd(command = command).run()
        logger.debug(run_cmd.proc_stdout)
        logger.debug(run_cmd.proc_stderr)

def main(**kwargs):
    """
    Main control function for the program

    Parameters
    ----------
    kwargs: dict
        dictionary containing args to run the program, expected to be passed from ``parse()``

    Keyword Arguments
    -----------------

    """
    # get the args that were passed
    analysis_ids = kwargs.pop('analysis_ids', [])
    pairs_sheet = kwargs.pop('pairs_sheet', None)
    sample_sheet = kwargs.pop('sample_sheet', None)

    if not pairs_sheet:
        logger.warning('No tumor-normal pairs_sheet was passed')

    other_files = []

    if pairs_sheet:
        if not tools.item_exists(item = pairs_sheet, item_type = 'file'):
            raise _e.AnalysisFileMissing(message = 'pairs_sheet file does not exist: {0}'.format(pairs_sheet), errors = '')
        else:
            other_files.append(pairs_sheet)

    if sample_sheet:
        if not tools.item_exists(item = sample_sheet, item_type = 'file'):
            raise _e.AnalysisFileMissing(message = 'sample_sheet file does not exist: {0}'.format(sample_sheet), errors = '')
        else:
            other_files.append(sample_sheet)

    for analysis_id in analysis_ids:
        # get the path to the sequencer directory matching the analysis ID
        logger.debug('Getting sequencer_output_path')
        sequencer_output_path = find_sequencer_dir(analysis_id = analysis_id)
        logger.debug('sequencer_output_path is: {0}'.format(sequencer_output_path))

        # validate the directory
        logger.debug('Validating sequencer_output_path ...')
        validate_sequencer_dir(sequencer_output_path = sequencer_output_path)

        # get the path to the .fastq file directory to use
        logger.debug('Finding fastq_dir')
        fastq_dir = find_fastq_parent_dir(sequencer_output_path = sequencer_output_path)
        logger.debug('fastq_dir is: {0}'.format(fastq_dir))

        # make a results_id
        results_id = make_results_ID()
        logger.debug('results_id is: {0}'.format(results_id))

        # make the path the the analysis_dir where the analysis will be prepared
        analysis_dir = tools.mkdirs(path = os.path.join(settings.analysis_dir, analysis_id, results_id), return_path = True)
        logger.debug('analysis_dir will be: {0}'.format(analysis_dir))

        # copy over files found in the sequencer_dir to the analysis dir
        logger.debug('Copying over files for the analysis from sequencer_dir')
        copy_sequencer_files(analysis_dir = analysis_dir, sequencer_output_path = sequencer_output_path, other_files = other_files)

        # make a symlink to the fastq dir from the analysis_dir
        logger.debug('Setting up symlink to fastq_dir inside analysis_dir')
        fastq_linkname = settings.fastq_linkname
        link_path = os.path.join(analysis_dir, fastq_linkname)
        os.symlink(fastq_dir, link_path)

        # clone the repo
        logger.debug('Cloning a new copy of the repo...')
        clone_snsxt(target_dir = analysis_dir)
        snsxt_dir = os.path.join(analysis_dir, 'snsxt')

        # make sure the dir exists
        if not tools.item_exists(item = snsxt_dir, item_type = 'dir'):
            raise _e.AnalysisFileMissing(message = 'snsxt_dir did not get created correctly: {0}'.format(snsxt_dir), errors = '')

        # make a command to use to start the snsxt analysis
        if pairs_sheet:
            snsxt_command_base = 'snsxt/run.py --pairs_sheet {0} -t task_lists/default_pairs.yml'.format(pairs_sheet)
        else:
            snsxt_command_base = 'snsxt/run.py -t task_lists/default.yml'

        snsxt_command = """
cd {0}
{1} -a {2} -r {3} -f {4}/ -d {5}
        """.format(
        snsxt_dir, # 0
        snsxt_command_base, # 1
        analysis_id, # 2
        results_id, # 3
        link_path, # 4
        analysis_dir # 5
        )
        logger.info('Run these commands in a new "screen" session to start the analysis:\n\n{0}\n\n'.format(snsxt_command))




def parse():
    """
    Runs the program based on CLI arguments.
    arg parsing happens here, if program was run as a script

    Returns
    -------
    dict
        a dictionary of keyword arguments to pass to `main()`

    Examples
    --------
    Example script usage::

        snsxt$ snsxt/deploy.py ...

    """
    # ~~~~ GET SCRIPT ARGS ~~~~~~ #
    # create the top-level parser
    parser = argparse.ArgumentParser(description='deploy a new snsxt NGS580 analysis directory')

    # required positional args
    parser.add_argument('analysis_ids', nargs = 1, help="IDs of sequencer output directories to use as input for the new analysis")

    # optional flags
    parser.add_argument('-p', '--pairs_sheet', dest = 'pairs_sheet', help = '"samples.pairs.csv" samplesheet to use for paired analysis', default = None)
    parser.add_argument('-s', '--sample_sheet', dest = 'sample_sheet', help = 'samplesheet associated with the analysis', default = None)

    # parse the args
    args = parser.parse_args()

    main(**vars(args))


# ~~~~ RUN ~~~~~~ #
if __name__ == "__main__":
    parse()
