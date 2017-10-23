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

# make the 'main' file handler global for use elsewhere
main_filehandler = log.get_logger_handler(logger = logger, handler_name = 'main')
console_handler = log.get_logger_handler(logger = logger, handler_name = "console", handler_type = 'StreamHandler')

logger.debug("snsxt program is starting")
logger.debug("Path to the monitor's log file: {0}".format(log.logger_filepath(logger = logger, handler_name = "main")))


# ~~~~ LOAD MORE PACKAGES ~~~~~~ #
# system modules
import sys
import csv
import shutil
from time import sleep
import argparse
import importlib

# this program's modules
import config
from util import tools as t
from util import find
from util import qsub
from sns_classes.classes import SnsWESAnalysisOutput
import task_lists
import task_func
import setup_report

# ~~~~ LOAD sns_tasks MODULES ~~~~~~ #
import sns_tasks
from sns_tasks import Delly2
from sns_tasks import GATK_DepthOfCoverage_custom
from sns_tasks import Summary_Avg_Coverage


# ~~~~~ LOAD CONFIGS ~~~~~ #
configs = config.config
extra_handlers = [h for h in log.get_all_handlers(logger)]

# ~~~~~ FUNCTIONS ~~~~~~ #
def main(analysis_dir, task_list, analysis_id = None, results_id = None):
    '''
    Main control function for the program


    from sns_classes.classes import SnsWESAnalysisOutput
    import config
    configs = config.config

    analysis_dir = '../example_sns_analysis5-copy'
    analysis_id = 'example_sns_analysis5'
    results_id = 'results1'

    analysis = SnsWESAnalysisOutput(dir = analysis_dir, id = analysis_id, results_id = results_id, sns_config = configs, extra_handlers = None)

    import sns_tasks

    task = sns_tasks.HapMapVariantRef(analysis = analysis)
    task.run()
    '''
    # load the analysis
    # extra_handlers = [main_filehandler]
    logger.info('Loading analysis {0} : {1} from dir {2}'.format(analysis_id, results_id, os.path.abspath(analysis_dir)))
    analysis = SnsWESAnalysisOutput(dir = analysis_dir, id = analysis_id, results_id = results_id, sns_config = configs, extra_handlers = extra_handlers)
    logger.debug(analysis)
    if not analysis.is_valid:
        logger.error('The analysis did not pass validations, exiting...')
        sys.exit()

    # run the tasks in the task list
    #  check if 'tasks' is an empty dict
    if not task_list or not task_list.get('tasks', None):
        logger.warning("No tasks were loaded")
    # run the steps included in the config
    else:
        # run the tasks
        for task_name, task_params in task_list['tasks'].items():
            # get the run_func value if present in the config
            run_func = None
            if 'run_func' in task_params.keys():
                run_func = task_params.pop('run_func')

            # make sure that the task is present
            logger.debug("Checking task '{0}' and function {1}".format(task_name, run_func))
            if not task_name in dir(sns_tasks):
                logger.debug("Task '{0}' is not a valid sns_task".format(task_name))
                continue
            # make sure the run function is present
            if not run_func in dir(task_func) or not run_func:
                logger.debug("run_func '{0}' is not a valid task function".format(run_func))
                continue

            # get the task module, e.g. sns_tasks.Delly2
            task_modulename = 'sns_tasks.{0}'.format(task_name)
            logger.debug("Loading task '{0}' from package '{1}'".format(task_name, 'sns_tasks'))
            task_module = importlib.import_module(task_modulename)

            # get the run function e.g. task_func.run_qsub_sample_task
            logger.debug("Loading run function '{0}' from package '{1}'".format(run_func, 'task_func'))
            run_func_module = getattr(task_func, run_func)

            # run the task
            logger.debug('Running task {0} as module {1}, with params: {2}'.format(task_name, task_module, task_params))
            run_func_module(analysis = analysis, task = task_module, extra_handlers = extra_handlers, **task_params)


    # check if reporting was included in config
    if task_list and task_list.get('setup_report', None):
        logger.debug('Starting report setup')
        setup_report.setup_report(output_dir = analysis_dir, analysis_id = analysis_id, results_id = results_id)

    logger.info('All tasks completed')
    log.log_all_handler_filepaths(logger)


def run():
    '''
    Run the monitoring program
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

    args = parser.parse_args()

    analysis_dir = args.analysis_dir
    analysis_id = args.analysis_id
    results_id = args.results_id
    task_list_file = args.task_list_file
    # logger.debug(args)

    logger.debug('Loading tasks from task list file: {0}'.format(os.path.abspath(task_list_file)))
    # get the list of tasks to run
    if task_list_file:
        task_list = task_lists.get_tasks(input_file = task_list_file)
    else:
        task_list = {}
    logger.debug('task_list config loaded: {0}'.format(task_list))

    main(analysis_dir = analysis_dir, analysis_id = analysis_id, results_id = results_id, task_list = task_list)

# ~~~~ RUN ~~~~~~ #
if __name__ == "__main__":
    run()
