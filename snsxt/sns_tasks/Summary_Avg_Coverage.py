#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Module for creating summaries of the average coverages for the analysis from GATK DepthOfCoverage output
'''
# ~~~~~ LOGGING ~~~~~~ #
import logging
import os
import sys

# name for this task to use with logging, and elsewhere in the script
task_name = "Summary_Avg_Coverage"

# add parent dir to sys.path to import util
scriptdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(scriptdir)
sys.path.insert(0, parentdir)
from util import log
from util import tools as t
from util import find
from util import qsub
sys.path.pop(0)

script_timestamp = log.timestamp()
scriptdir = os.path.dirname(os.path.realpath(__file__))
scriptname = os.path.basename(__file__)
logdir = os.path.join(scriptdir, 'logs')
log_file = os.path.join(scriptdir, logdir, '{0}.{1}.log'.format(scriptname, script_timestamp))

# add a per-module timestamped logging file handler
logger = log.build_logger(name = task_name)
logger.addHandler(log.create_main_filehandler(log_file = log_file, name = task_name))
# make the file handler global for use elsewhere
main_filehandler = log.get_logger_handler(logger = logger, handler_name = task_name)
main_filehandler_path = log.logger_filepath(logger = logger, handler_name = task_name)
logger.debug("loading {0} module".format(task_name))

# ~~~~ LOAD MORE PACKAGES ~~~~~~ #
import csv
import shutil
import config
import task_utils
from task_utils import Annotation_inplace

# ~~~~ SETUP CONFIGS ~~~~~~ #
# get external configs, make internal configs
configs = {}
# from the script
configs['this_script_timestamp'] = script_timestamp # 2017-10-10-16-44-52
configs['this_scriptdir'] = scriptdir # /ifs/data/molecpathlab/scripts/snsxt/snsxt/sns_tasks
configs['this_scriptname'] = scriptname # Summary_Avg_Coverage.py
configs['logdir'] = logdir # /ifs/data/molecpathlab/scripts/snsxt/snsxt/sns_tasks/logs
configs['log_file'] = log_file
# from global config
configs['script_dir'] = config.sns_tasks['script_dir']
configs['report_dir'] = config.sns_tasks['report_dir']
# from this module config
configs['input_dir'] = config.Summary_Avg_Coverage['input_dir']
configs['input_pattern'] = config.Summary_Avg_Coverage['input_pattern']
configs['output_dir_name'] = config.Summary_Avg_Coverage['output_dir_name']
configs['report_files'] = config.Summary_Avg_Coverage['report_files']
configs['script_files'] = config.Summary_Avg_Coverage['script_files']
configs['run_script'] = config.Summary_Avg_Coverage['run_script']
configs['annotation_method'] = config.Summary_Avg_Coverage['annotation_method']
configs['task_name'] = config.Summary_Avg_Coverage['task_name']

configs['run_script_path'] = os.path.join(configs['this_scriptdir'], configs['script_dir'], configs['run_script'])
# /ifs/data/molecpathlab/scripts/snsxt/snsxt/sns_tasks/scripts/calculate_average_coverages.R

# ~~~~ CUSTOM FUNCTIONS ~~~~~~ #
def make_run_script_cmd(input_dir, output_dir, run_script):
    '''
    Make the shell command to run the run_script
    '''
    command = '''
{0} -d {1} -o {2}
'''.format(
run_script, # 0
input_dir, # 1
output_dir # 2
)
    return(command)


def main(analysis, extra_handlers = None):
    '''
    Main control function for the program
    Creates summary coverage files for all samples in the analysis
    '''

    # check for extra logger handlers that might have been passed
    if extra_handlers != None:
        for h in extra_handlers:
            logger.addHandler(h)



    logger.debug('Analysis is: {0}'.format(analysis))
    # logger.debug(sample.static_files)
    log.print_filehandler_filepaths_to_log(logger = logger)

    # setup the output locations
    output_dir = t.mkdirs(path = os.path.join(analysis.dir, configs['output_dir_name']), return_path = True)
    logger.debug('output_dir: {0}'.format(output_dir))

    logger.debug(os.getcwd())
    logger.debug(configs['run_script_path'])

    input_dir = os.path.join(analysis.dir, configs['input_dir'])

    # shell command to run
    command = make_run_script_cmd(input_dir = input_dir, output_dir = output_dir, run_script = configs['run_script_path'])
    logger.debug(command)

    # need to change cwd for R commands to source the external tools file
    with t.DirHop(os.path.dirname(configs['run_script_path'])) as d:
        run_cmd = t.SubprocessCmd(command = command).run()
        logger.debug(run_cmd.proc_stderr)

    logger.debug('task_utils.configs: {0}'.format(task_utils.configs))
    logger.debug('task_utils.configs["Annotation_inplace"]: {0}'.format(task_utils.configs['Annotation_inplace']))

    # reset the list of extra file handlers to pass to the annotation function
    extra_handlers = [h for h in log.get_all_handlers(logger)]
    Annotation_inplace(input_dir = output_dir, annotation_method = configs['annotation_method'], extra_handlers = extra_handlers)


    # set up the report
    task_utils.setup_report(output_dir = output_dir, configs = configs)

def run():
    '''
    Run the monitoring program
    arg parsing goes here, if program was run as a script
    '''
    main()

if __name__ == "__main__":
    run()
