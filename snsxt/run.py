#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Runs a series of analysis tasks

Originally designed as an extension to the sns pipeline output, with the flexibility of added ad hoc extra analysis tasks for downstream processing
"""
# ~~~~~ LOGGING ~~~~~~ #
import os
from util import log

import logging

# path to the script's dir
scriptdir = os.path.dirname(os.path.realpath(__file__))
scriptname = os.path.basename(__file__)
script_timestamp = log.timestamp()
# path to parent dir 2 levels above this script
snsxt_parent_dir = os.path.realpath(os.path.dirname(os.path.dirname(__file__)) )
# /ifs/data/molecpathlab/scripts/snsxt/

# dir for logs
log_dir = os.path.join(snsxt_parent_dir, 'logs')
# timestamped subdir for logs
# log_subdir = os.path.join(snsxt_parent_dir, 'logs', script_timestamp)

# set a timestamped log file for debug log
log_file = os.path.join(log_dir, '{0}.{1}.log'.format(scriptname, script_timestamp))
email_log_file = os.path.join(log_dir, '{0}.{1}.email.log'.format(scriptname, script_timestamp))

def logpath():
    """
    Returns the path to the main log file; needed by the logging.yml config file

    This generates dynamic output log file paths & names

    Returns
    -------
    logging.FileHandler
        a Python logging FileHandler object configured with a log file path set dynamically at program run time
    """
    global log_file
    return(log.logpath(logfile = log_file))

def email_logpath():
    """
    Returns the path to the email log file; needed by the logging.yml config file

    This generates dynamic output log file paths & names

    Returns
    -------
    logging.FileHandler
        a Python logging FileHandler object configured with a log file path set dynamically at program run time
    """
    return(log.logpath(logfile = email_log_file))

# load the logging config
config_yaml = os.path.join(scriptdir, 'logging.yml')
basic_yaml = os.path.join(scriptdir, "basic_logging.yml")
if __name__ == "__main__":
    logger = log.log_setup(config_yaml = config_yaml, logger_name = "run")
else:
    logger = log.log_setup(config_yaml = basic_yaml, logger_name = "run")

extra_handlers = [h for h in log.get_all_handlers(logger)]
"""
Python logging Filehandlers to be passed throughout the program, in order to keep all submodules logging to the same file(s) set by `logpath()` and  `email_logpath()`
"""

logger.debug("snsxt program is starting at location: {0}".format(os.path.realpath(os.path.expanduser(__file__))))
# print the paths to the log files to the log
log.print_filehandler_filepaths_to_log(logger)

# ~~~~~ LOAD CONFIGS ~~~~~ #
import config
# update program-wide config with extra items from this script
config.config['snsxt_parent_dir'] = snsxt_parent_dir # snsxt/
config.config['snsxt_dir'] = scriptdir # snsxt/snsxt/
config.config['extra_handlers'] = extra_handlers
config.config['sns_repo_dir'] = os.path.join(config.config['snsxt_dir'], config.config['sns_repo_dir']) # snsxt/snsxt/sns
configs = config.config
"""
The main configurations dictionary to use for settings throughout the program. The `sns_repo_dir` value is modified at program run time, by preprending the  `snsxt_dir` path (path to this script's directory). Other dict keys are set at program run time as well, including `snsxt_parent_dir`, `snsxt_dir`, and `extra_handlers`
"""


default_targets = os.path.join(snsxt_parent_dir, 'targets.bed')
"""
A .bed formatted file to use by default as the target regions for variant calling
"""

default_probes = os.path.join(snsxt_parent_dir, 'probes.bed')
"""
A .bed formatted file to use by default for CNV analysis. Must have only 3 tab-delimited columns.
"""

default_task_list = os.path.join(snsxt_parent_dir, "task_lists", "default.yml")
"""
The YAML formatted task list containing analysis tasks to be run by default
"""

# ~~~~ LOAD MORE PACKAGES ~~~~~~ #
# system modules
import sys
import argparse
import yaml
import collections
import json

# this program's modules
from util import tools
from util import find
from util import qsub
from util import mutt
from sns_classes.classes import SnsWESAnalysisOutput
import run_tasks
import job_management
import validation
import cleanup
import setup_report
import sns_tasks
import mail
import _exceptions as _e

# add log file to email output
mail.email_files.append(log_file)

# add handlers to run_tasks
run_tasks.extra_handlers = [h for h in extra_handlers]

# ~~~~~ FUNCTIONS ~~~~~~ #
def startup():
    """
    Configures global attributes of other modules, and performs other actions, when the program starts up

    Todo
    ----
    Integrate this with the rest of the program
    """
    # add log file to email output
    mail.email_files.append(log_file)

    # add handlers to run_tasks
    run_tasks.extra_handlers = [h for h in extra_handlers]


def get_task_list(task_list_file):
    """
    Reads the task_list from a YAML formatted file

    Parameters
    ----------
    task_list_file: str
        the path to a YAML formatted file from which to read analysis tasks

    Returns
    -------
    dict
        a dictionary containing the contents of the YAML `task_list_file`

    """
    logger.debug('Loading tasks from task list file: {0}'.format(os.path.abspath(task_list_file)))

    # read the YAML as an OrderedDict
    _mapping_tag = yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG
    def dict_representer(dumper, data):
        return(dumper.represent_dict(data.items()))
    def dict_constructor(loader, node):
        return(collections.OrderedDict(loader.construct_pairs(node)))
    yaml.add_representer(collections.OrderedDict, dict_representer)
    yaml.add_constructor(_mapping_tag, dict_constructor)

    # get the list of tasks to run
    if task_list_file:
        with open(task_list_file, "r") as f:
            task_list = yaml.load(f)
    else:
        task_list = {}
    logger.debug('task_list config loaded: {0}'.format(task_list))
    return(task_list)


def main(**kwargs):
    """
    Main control function for the program

    Parameters
    ----------
    kwargs: dict
        dictionary containing args to run the program, expected to be passed from `parse()` and passed on to `run_sns_tasks()` and `run_sns_tasks()`

    Keyword Arguments
    -----------------
    analysis_id: str
        an identifier for the analysis (e.g. the NextSeq run ID)
    results_id: str
        a sub-identifier for the analysis (e.g. a timestamp)
    task_list_file: str
        the path to a YAML formatted file containing analysis tasks to be run
    debug_mode: bool
        prevents the program from halting if errors are found in qsub log output files; defaults to `False`. `True` = do not stop for qsub log errors, `False` = stop if errors are found
    fastq_dirs: list
        a list of paths to directories to use as input data locations for a new `sns` analysis. These directories should contain .fastq.gz files within two levels from the top level of the dir (e.g. at most 2 subdirs deep). The .fastq.gz files contained in these directories should keep the exact filenames output by the NextSeq; sample parsing will take place automatically.
    targets_bed: str
        path to a .bed formatted file to use as the target regions for variant calling
    probes_bed: str
        path to a .bed formatted file to use as the probes for CNV analysis
    pairs_sheet: str
        path to a .csv samplesheet to use for matching tumor and normal samples in the paired variant calling analysis steps. See GitHub for example.

    """
    # update configs with the passed args
    config.config['parsed'].update(kwargs)

    # get the args that were passed
    analysis_id = kwargs.pop('analysis_id', None)
    task_list_file = kwargs.pop('task_list_file', default_task_list)
    results_id = kwargs.pop('results_id', None)
    debug_mode = kwargs.pop('debug_mode', False)
    fastq_dirs = kwargs.pop('fastq_dirs', [])
    targets_bed = kwargs.pop('targets_bed', default_targets)
    probes_bed = kwargs.pop('probes_bed', default_probes)
    pairs_sheet = kwargs.pop('pairs_sheet', None)
    analysis_dir = kwargs.pop('analysis_dir', None)

    # make sure that analysis_dir was passed
    logger.debug('analysis_dir passed to script: {0}'.format(analysis_dir))
    if not analysis_dir:
        raise _e.ArgumentError(message = 'No analysis_dir passed', errors = '')

    # make sure the analysis_dir exists
    if not tools.item_exists(analysis_dir):
        raise _e.AnalysisFileMissing(message = 'analysis_dir does not exist!', errors = '')

    # get the full path to the analysis_dir
    analysis_dir = os.path.realpath(os.path.expanduser(analysis_dir))
    logger.info('Analysis directory will be: {0}'.format(analysis_dir))

    # rebuild the kwargs with only the items chosen to pass on
    kwargs = {
    'analysis_id': analysis_id,
    'task_list_file': task_list_file,
    'results_id': results_id,
    'debug_mode': debug_mode,
    'fastq_dirs': fastq_dirs,
    'targets_bed': targets_bed,
    'probes_bed': probes_bed,
    'pairs_sheet': pairs_sheet
    }
    # update configs with the main args
    config.config['main'].update(kwargs)

    # get the task list contents
    task_list = get_task_list(task_list_file)

    # try to run all the tasks for the analysis
    try:
        # check if 'sns' is in the task list
        if task_list.get('sns', None):
            # check if there are items there
            if task_list['sns']:
                logger.debug('sns tasks:\n{0}'.format(task_list['sns'].items()))
                run_tasks.run_sns_tasks(task_list, analysis_dir, **kwargs)

        # check if there are downstream snsxt tasks
        if task_list.get('tasks', None):
            # check if there are items there
            if task_list['tasks']:
                logger.debug('downstream snsxt tasks:\n{0}'.format(task_list['tasks'].items()))
                run_tasks.run_snsxt_tasks(task_list, analysis_dir, **kwargs)

        # check if the report should be setup
        if task_list.get('setup_report', None):
            # TODO: move report out of this function and into main as part of cleanup
            logger.debug('Starting report setup')
            setup_report.setup_report(output_dir = analysis_dir, analysis_id = analysis_id, results_id = results_id)
    except:
        # run this if an exception is caught
        logger.exception('Encountered an exception while running tasks')
        job_management.kill_background_jobs()
        mail.email_error_output(message_file = email_log_file)
    else:
        # run this if no exception is caught
        mail.email_output(message_file = email_log_file)
    finally:
        # run this no matter what
        # run cleanup
        cleanup.save_configs(analysis_dir = analysis_dir)




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

        snsxt$ snsxt/run.py -d mini_analysis-controls/ -f mini_analysis-controls/fastq/ -a mini_analysis -r results1 -t task_lists/dev.yml --pairs_sheet mini_analysis-controls/samples.pairs.csv_usethis

    """
    # ~~~~ GET SCRIPT ARGS ~~~~~~ #
    # create the top-level parser
    parser = argparse.ArgumentParser(description='snsxt: sns bioinformatics pipeline extension program')

    # optional flags
    parser.add_argument("-a", "--analysis_id", default = None, type = str, dest = 'analysis_id', metavar = 'analysis_id', help="Identifier for the analysis")
    parser.add_argument("-t", "--task-list", default = default_task_list, dest = 'task_list_file', help="YAML formatted tasks list file to control which downstream analysis tasks get run")
    parser.add_argument("-r", "--results_id", default = None, type = str, dest = 'results_id', metavar = 'results_id', help="Identifier for the analysis results, e.g. timestamp used to differentiate multiple sns pipeline outputs for the same sequencing run raw analysis input files")
    parser.add_argument("--debug_mode", default = False, action = "store_true", dest = 'debug_mode', help="Skip analysis output validation and error checking before running downstream snsxt pipeline steps")
    parser.add_argument('-f', '--fastq_dir', dest = "fastq_dirs", nargs='*' , help = "Directories containing .fastq files to use in a new sns analysis")
    parser.add_argument('--targets', dest = 'targets_bed', help = 'Targets .bed file with regions for analysis', default = default_targets)
    parser.add_argument('--probes', dest = 'probes_bed', help = 'Probes .bed file with regions for CNV analysis', default = default_probes)
    parser.add_argument('--pairs_sheet', dest = 'pairs_sheet', help = '"samples.pairs.csv" samplesheet to use for paired analysis', default = None)

    # required flags
    parser.add_argument('-d', '--analysis_dir', dest = "analysis_dir", help = "Path to the to use for the analysis. For a new sns analysis, this will become the output directory. For an existing sns analysis output, this will become the input directory", required = True)

    # parse the args and run the default parser function
    args = parser.parse_args()

    main(**vars(args))


# ~~~~ RUN ~~~~~~ #
if __name__ == "__main__":
    parse()
