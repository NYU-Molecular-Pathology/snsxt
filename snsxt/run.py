#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Run a series of analysis tasks, as an extension to the sns pipeline output
'''
# ~~~~~ LOGGING ~~~~~~ #
import os
from util import log
import logging

# path to the script's dir
scriptdir = os.path.dirname(os.path.realpath(__file__))
scriptname = os.path.basename(__file__)
script_timestamp = log.timestamp()
# set a timestamped log file for debug log
log_file = os.path.join(scriptdir, 'logs', '{0}.{1}.log'.format(scriptname, script_timestamp))
email_log_file = os.path.join(scriptdir, 'logs', '{0}.{1}.email.log'.format(scriptname, script_timestamp))

def logpath():
    '''
    Return the path to the main log file; needed by the logging.yml
    use this for dynamic output log file paths & names
    '''
    global log_file
    return(log.logpath(logfile = log_file))

def email_logpath():
    '''
    Return the path for the email log output
    '''
    return(log.logpath(logfile = email_log_file))

# load the logging config
config_yaml = os.path.join(scriptdir, 'logging.yml')
logger = log.log_setup(config_yaml = config_yaml, logger_name = "run")
logger.debug("snsxt program is starting")



# ~~~~ LOAD MORE PACKAGES ~~~~~~ #
# system modules
import sys
import argparse
import yaml

# this program's modules
import config
from util import tools as t
from util import find
from util import qsub
from sns_classes.classes import SnsWESAnalysisOutput
import setup_report

from _snsxt import snsxt


# ~~~~~ LOAD CONFIGS ~~~~~ #
configs = config.config
extra_handlers = [h for h in log.get_all_handlers(logger)]



# ~~~~~ FUNCTIONS ~~~~~~ #
def main(analysis_dir, task_list, analysis_id = None, results_id = None, debug_mode = False, *args, **kwargs):
    '''
    Main control function for the program
    '''
    kwargs.update({
    'analysis_dir':analysis_dir,
    'analysis_id': analysis_id,
    'results_id': results_id,
    'debug_mode': debug_mode
    # 'extra_handlers': extra_handlers
    })

    snsxt(task_list = task_list, configs = configs, *args, **kwargs)

    # check if reporting was included in config
    if task_list and task_list.get('setup_report', None):
        logger.debug('Starting report setup')
        setup_report.setup_report(output_dir = analysis_dir, analysis_id = analysis_id, results_id = results_id)

    logger.info('All tasks completed')
    log.log_all_handler_filepaths(logger)


def run():
    '''
    Run the program
    arg parsing goes here, if program was run as a script
    '''
    # ~~~~ GET SCRIPT ARGS ~~~~~~ #
    parser = argparse.ArgumentParser(description='snsxt: sns bioinformatics pipeline extension program')

    # required positional args
    parser.add_argument("analysis_dir",
        # default analysis dir location is two levels above the 'snsxt/snsxt/run.py' dir
         # /ifs/data/molecpathlab/scripts/snsxt/snsxt/run.py -> /ifs/data/molecpathlab/scripts
        default = os.path.realpath(os.path.join(os.path.realpath(__file__), "../../../")),
        help = "Path to the analysis output directory used for the sns pipeline", nargs="?")

    # optional flags
    parser.add_argument("-ai", "--analysis_id", default = None, type = str, dest = 'analysis_id', metavar = 'analysis_id', help="Identifier for the analysis")
    parser.add_argument("-ri", "--results_id", default = None, type = str, dest = 'results_id', metavar = 'results_id', help="Identifier for the analysis results, e.g. timestamp used to differentiate multiple sns pipeline outputs for the same sequencing run raw analysis input files")
    parser.add_argument("-t", "--task-list", default = os.path.join("task_lists", "default.yml"), dest = 'task_list_file', help="YAML formatted tasks list file to control which analysis tasks get run")
    parser.add_argument("--debug_mode", default = False, action = "store_true", dest = 'debug_mode', help="Skip analysis validation")

    args = parser.parse_args()

    analysis_dir = args.analysis_dir
    analysis_id = args.analysis_id
    results_id = args.results_id
    task_list_file = args.task_list_file
    debug_mode = args.debug_mode
    # logger.debug(args)

    logger.debug('Loading tasks from task list file: {0}'.format(os.path.abspath(task_list_file)))
    # get the list of tasks to run
    if task_list_file:
        # task_list = task_lists.get_tasks(input_file = task_list_file)
        with open(task_list_file, "r") as f:
            task_list = yaml.load(f)
    else:
        task_list = {}
    logger.debug('task_list config loaded: {0}'.format(task_list))

    main(analysis_dir = analysis_dir, analysis_id = analysis_id, results_id = results_id, task_list = task_list, debug_mode = debug_mode)

# ~~~~ RUN ~~~~~~ #
if __name__ == "__main__":
    run()
