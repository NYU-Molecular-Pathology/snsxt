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
import sns_tasks



# ~~~~~ LOAD CONFIGS ~~~~~ #
configs = config.config
extra_handlers = [h for h in log.get_all_handlers(logger)]



# ~~~~~ FUNCTIONS ~~~~~~ #
def main(analysis_dir, task_list, analysis_id = None, results_id = None, debug_mode = False):
    '''
    Main control function for the program
    '''
    # load the analysis from the sns output
    logger.info('Loading analysis {0} : {1} from dir {2}'.format(analysis_id, results_id, os.path.abspath(analysis_dir)))
    analysis = SnsWESAnalysisOutput(dir = analysis_dir, id = analysis_id, results_id = results_id, sns_config = configs, extra_handlers = extra_handlers)

    logger.debug(analysis)
    logger.debug(task_list)

    # exit if the analysis is invalid, unless debug mode is enabled
    if not debug_mode:
        if not analysis.is_valid:
            logger.error('The analysis did not pass validations, exiting...')
            sys.exit()

    # run the tasks in the task list
    #  check if 'tasks' is an empty dict
    if not task_list or not task_list.get('tasks', None):
        logger.warning("No tasks were loaded")
    # run the steps included in the config
    else:
        logger.debug(task_list['tasks'].items())
        logger.debug(dir(sns_tasks))
        for task_name, task_params in task_list['tasks'].items():
            # make sure the task is present in sns_tasks
            if not task_name in dir(sns_tasks):
                logger.error('Task {0} was not found in the sns_tasks module'.format(task_name))
            else:
                logger.error('Loading task {0} '.format(task_name))
                # load the task class from the module
                task_class = getattr(sns_tasks, task_name)
                # logger.debug(task_class)
                # create the task object with the analysis
                task = task_class(analysis = analysis, extra_handlers = extra_handlers)
                # run the task
                task.run()
                # logger.debug(dir(task))

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
    parser.add_argument("-t", "--task-list", default = os.path.join("task_lists", "dev2.yml"), dest = 'task_list_file', help="YAML formatted tasks list file to control which analysis tasks get run")
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
