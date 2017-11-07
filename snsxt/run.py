#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Run a series of analysis tasks, as an extension to the sns pipeline output
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

# set a timestamped log file for debug log
log_file = os.path.join(scriptdir, 'logs', '{0}.{1}.log'.format(scriptname, script_timestamp))
email_log_file = os.path.join(scriptdir, 'logs', '{0}.{1}.email.log'.format(scriptname, script_timestamp))

def logpath():
    """
    Return the path to the main log file; needed by the logging.yml
    use this for dynamic output log file paths & names
    """
    global log_file
    return(log.logpath(logfile = log_file))

def email_logpath():
    """
    Return the path for the email log output
    """
    return(log.logpath(logfile = email_log_file))

# load the logging config
config_yaml = os.path.join(scriptdir, 'logging.yml')
logger = log.log_setup(config_yaml = config_yaml, logger_name = "run")
extra_handlers = [h for h in log.get_all_handlers(logger)]
logger.debug("snsxt program is starting at location: {0}".format(__file__))
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

default_targets = os.path.join(snsxt_parent_dir, 'targets.bed')
default_probes = os.path.join(snsxt_parent_dir, 'probes.bed')
default_task_list = os.path.join(snsxt_parent_dir, "task_lists", "default.yml")

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
import job_management
import validation
import cleanup
import setup_report
import sns_tasks
import mail
import _exceptions as _e

# add log file to email output
mail.email_files.append(log_file)

# ~~~~~ FUNCTIONS ~~~~~~ #
def get_task_list(task_list_file):
    """
    Read the task_list from a YAML formatted file
    """
    logger.debug('Loading tasks from task list file: {0}'.format(os.path.abspath(task_list_file)))

    # https://stackoverflow.com/a/21048064/5359531
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


def get_task_class(task_name):
    """
    Get the task's class from the sns_tasks module
    """
    # make sure the task is present in sns_tasks
    if not task_name in dir(sns_tasks):
        logger.error('Task {0} was not found in the sns_tasks module'.format(task_name))
        raise
    else:
        logger.debug('Loading task {0} '.format(task_name))
    # load the task class from the module
    task_class = getattr(sns_tasks, task_name)
    return(task_class)

def run_tasks(tasks, analysis_dir = None, analysis = None, debug_mode = False, **kwargs):
    """
    Run a series of analysis tasks

    analysis = SnsWESAnalysisOutput
    """
    # items output by tasks which should be returned by this function
    tasks_output = {}
    # list of files to send in output email
    tasks_output['email_files'] = []

    if analysis_dir and analysis:
        logger.error('Both analysis_dir and analysis were passed; there can be only one.')
        raise

    if not analysis_dir and not analysis:
        logger.error('Neither analysis_dir nor analysis were passed; there must be one.')
        raise

    # list to capture qsub jobs submitted but not monitored by a task
    background_jobs = []

    # list to capture background output that should be validated after all jobs finish
    background_output_files = []

    for task_name, task_params in tasks.items():
        task_class = get_task_class(task_name)

        # create the task object
        if analysis_dir:
            task = task_class(analysis_dir = analysis_dir, extra_handlers = extra_handlers, **kwargs)
        if analysis:
            # make sure the ana analysis ouput object is valid before continuing
            if not debug_mode:
                if not analysis.is_valid:
                    err_message = 'The analysis did not pass validations\n'
                    validations_message = json.dumps(analysis.validations, indent = 4)
                    logger.error(err_message)
                    raise _e.AnalysisInvalid(message = err_message + validations_message, errors = '')
            task = task_class(analysis = analysis, extra_handlers = extra_handlers)

        # run the task
        if task_params:
            # with the params
            task_output = task.run(**task_params)
        else:
            # without the params
            task_output = task.run()

        # check for files from the task which should be included in email output
        expected_email_files = task.get_expected_email_files()
        logger.debug('task email files: {0}'.format(expected_email_files))
        if expected_email_files:
            for item in expected_email_files:
                # tasks_output['email_files'].append(item)
                mail.email_files.append(item)

        # check the output of the task
        if task_output:
            # check for background qsub jobs output by the task
            task_jobs = []
            for item in task_output:
                if isinstance(item, qsub.Job):
                    task_jobs.append(item)
            # if no task_jobs were produced, validate the task output immediately
            if not task_jobs:
                logger.debug('Validating task output files')
                task.validate_output()
            else:
                # add task jobs to background jobs
                logger.debug('Background qsub jobs were generated by the task and will be monitored at program completion')
                for job in task_jobs:
                    background_jobs.append(job)
                # add task expected output to background output to be validated later
                logger.debug('Expected output files for the task will be validated at program completion')
                task_output_files = task.get_expected_output_files()
                for item in task_output_files:
                    background_output_files.append(item)

    # monitor and validate all background jobs
    if background_jobs:
        logger.debug('Background jobs will be monitored for completion and validated')
        job_management.monitor_validate_jobs(jobs = background_jobs)

    # validate all background output files
    if background_output_files:
        logger.debug('Background task output files will be validated')
        validation.validate_items(items = background_output_files)

    return(tasks_output)




def run_sns_tasks(task_list, analysis_dir, **kwargs):
    """
    Run tasks that start and run the main sns pipeline

    Run each sns task individually, so that all qsub jobs will be completed at every step
    """
    # get the args that were passed
    fastq_dirs = kwargs.pop('fastq_dirs')
    targets_bed = kwargs.pop('targets_bed')
    probes_bed = kwargs.pop('probes_bed')
    pairs_sheet = kwargs.pop('pairs_sheet')

    logger.info('Creating new sns analysis in dir {0}'.format(os.path.abspath(analysis_dir)))

    # run tasks one at a time
    tasks = task_list['sns']
    for key, value in tasks.items():
        run_tasks(tasks = {key: value}, analysis_dir = analysis_dir, fastq_dirs = fastq_dirs, targets_bed = targets_bed, probes_bed = probes_bed, pairs_sheet = pairs_sheet, **kwargs)

def run_snsxt_tasks(task_list, analysis_dir, **kwargs):
    """
    Run the downstream snsxt analysis tasks on sns pipeline output
    """
    # get the args that were passed
    analysis_id = kwargs.pop('analysis_id')
    results_id = kwargs.pop('results_id')
    debug_mode = kwargs.pop('debug_mode')

    tasks = task_list['tasks']
    logger.info('Loading analysis {0} : {1} from dir {2}'.format(analysis_id, results_id, os.path.abspath(analysis_dir)))
    analysis = SnsWESAnalysisOutput(dir = analysis_dir, id = analysis_id, results_id = results_id, sns_config = configs, extra_handlers = extra_handlers)
    run_tasks(tasks, analysis = analysis, debug_mode = debug_mode, **kwargs)

    if task_list.get('setup_report', None):
        # TODO: move report out of this function and into main as part of cleanup
        logger.debug('Starting report setup')
        setup_report.setup_report(output_dir = analysis_dir, analysis_id = analysis_id, results_id = results_id)
    # cleanup.analysis_complete(analysis = analysis)




def main(**kwargs):
    """
    Main control function for the program
    """
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
    if not analysis_dir:
        logger.error('No analysis dir passed')
        # TODO: make sure this raise works, intended for when snsxt is not called as script
        raise

    # rebuild the kwargs with only the items chosen
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

    # get the task list contents
    task_list = get_task_list(task_list_file)

    # list to hold

    # try to run all the tasks for the analysis
    try:
        # check if 'sns' is in the task list
        if task_list.get('sns', None):
            # check if there are items there
            if task_list['sns']:
                logger.debug('sns tasks:\n{0}'.format(task_list['sns'].items()))
                run_sns_tasks(task_list, analysis_dir, **kwargs)

        # check if there are downstream snsxt tasks
        if task_list.get('tasks', None):
            # check if there are items there
            if task_list['tasks']:
                logger.debug('downstream snsxt tasks:\n{0}'.format(task_list['tasks'].items()))
                run_snsxt_tasks(task_list, analysis_dir, **kwargs)
    except:
        # run this if an exception is caught
        logger.exception('Encountered an exception while running tasks')
        mail.email_error_output(message_file = email_log_file)
    else:
        # run this if no exception is caught
        mail.email_output(message_file = email_log_file)
    finally:
        # run this no matter what
        # run cleanup
        cleanup.save_configs(analysis_dir = analysis_dir)

        # logger.debug('email_files: {0}'.format(mail.email_files))
        # mail_command = mutt.mutt_mail(recipient_list = configs['email_recipients'],
        #                 reply_to = mutt.get_reply_to_address(server = configs['reply_to_server']),
        #                 subject_line = '[NGS580] Test',
        #                 message_file = email_log_file,
        #                 attachment_files = email_files,
        #                 return_only_mode = True)
        # tools.SubprocessCmd(command = mail_command).run()




def parse():
    """
    Run the program
    arg parsing goes here, if program was run as a script
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
