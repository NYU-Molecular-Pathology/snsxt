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
import collections

# this program's modules
import config
from util import tools as t
from util import find
from util import qsub
from sns_classes.classes import SnsWESAnalysisOutput
import setup_report

from _snsxt import snsxt
from _start_sns import start_sns

# ~~~~~ LOAD CONFIGS ~~~~~ #
configs = config.config

# path to parent dir 2 levels above this script
snsxt_parent_dir = os.path.realpath(os.path.dirname(os.path.dirname(__file__)) )
# /ifs/data/molecpathlab/scripts/snsxt/
configs['snsxt_parent_dir'] = snsxt_parent_dir

extra_handlers = [h for h in log.get_all_handlers(logger)]
configs['extra_handlers'] = extra_handlers



# ~~~~~ FUNCTIONS ~~~~~~ #
def get_task_list(task_list_file):
    '''
    Read the task_list from a YAML formatted file
    '''
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

def main(analysis_dir, task_list, analysis_id = None, results_id = None, debug_mode = False, *args, **kwargs):
    '''
    Main control function for the program
    '''
    kwargs.update({
    'analysis_dir':analysis_dir,
    'analysis_id': analysis_id,
    'results_id': results_id,
    'debug_mode': debug_mode
    })

    # run the downstream pipeline analysis tasks
    snsxt(task_list = task_list, configs = configs, *args, **kwargs)

    # check if reporting was included in config
    if task_list and task_list.get('setup_report', None):
        logger.debug('Starting report setup')
        setup_report.setup_report(output_dir = analysis_dir, analysis_id = analysis_id, results_id = results_id)

    logger.info('All tasks completed')
    log.log_all_handler_filepaths(logger)


def run_main(args, **kwargs):
    '''
    Parse the args to run the main downstream analysis program
    '''
    analysis_dir = args.analysis_dir
    analysis_id = args.analysis_id
    results_id = args.results_id
    task_list_file = args.task_list_file
    debug_mode = args.debug_mode

    task_list = get_task_list(task_list_file)
    main(analysis_dir = analysis_dir, analysis_id = analysis_id, results_id = results_id, task_list = task_list, debug_mode = debug_mode)

def run_new(args, **kwargs):
    '''
    Parse args to start a new sns analysis
    '''
    # get args to use here
    fastq_dirs = args.fastq_dirs
    output_dir = args.output_dir
    no_downstream = args.no_downstream
    task_list_file = args.task_list_file
    analysis_id = args.analysis_id
    results_id = args.results_id
    debug_mode = args.debug_mode

    # setup dict of args to pass on
    kwargs.update({
    'fastq_dirs': fastq_dirs,
    'output_dir': output_dir
    })

    # setup and run the new sns analysis
    sns_output_dir = start_sns(configs = configs, **kwargs)

    # optionally run the downstream snsxt analysis steps as well
    if not no_downstream: # True = dont run, False = run
        logger.debug('Running downstream snsxt analysis pipeline')
        task_list = get_task_list(task_list_file)
        main(analysis_dir = sns_output_dir, analysis_id = analysis_id, results_id = results_id, task_list = task_list, debug_mode = debug_mode)



def parse():
    '''
    Run the program
    arg parsing goes here, if program was run as a script
    '''
    # ~~~~ GET SCRIPT ARGS ~~~~~~ #
    # create the top-level parser
    parser = argparse.ArgumentParser(description='snsxt: sns bioinformatics pipeline extension program')
    subparsers = parser.add_subparsers(title='subcommands', description='valid subcommands', help='additional help', dest='subparsers')

    parser.add_argument("-ai", "--analysis_id", default = None, type = str, dest = 'analysis_id', metavar = 'analysis_id', help="Identifier for the analysis")
    parser.add_argument("-t", "--task-list", default = os.path.join("task_lists", "default.yml"), dest = 'task_list_file', help="YAML formatted tasks list file to control which downstream analysis tasks get run")
    parser.add_argument("-ri", "--results_id", default = None, type = str, dest = 'results_id', metavar = 'results_id', help="Identifier for the analysis results, e.g. timestamp used to differentiate multiple sns pipeline outputs for the same sequencing run raw analysis input files")
    parser.add_argument("--debug_mode", default = False, action = "store_true", dest = 'debug_mode', help="Skip analysis output validation and error checking before running downstream snsxt pipeline steps")


    # create the parser for the "new" command
    parser_new = subparsers.add_parser('new', help = 'Start a new sns wes pipeline analysis from fastq directories')
    parser_new.set_defaults(func = run_new)
    parser_new.add_argument("fastq_dirs", help = "Directories containing .fastq files to use in a new sns analysis", nargs="+")
    parser_new.add_argument('-o', '--output_dir', dest = 'output_dir', help = 'Output directory for the new analysis',
                            default =  os.path.join(snsxt_parent_dir, 'sns_output', '{0}'.format(t.timestamp())))
    parser_new.add_argument('--targets', dest = 'targets_bed', help = 'Targets .bed file with regions for analysis', default = os.path.join(snsxt_parent_dir, 'targets.bed'))
    parser_new.add_argument('--pairs_sheet', dest = 'pairs_sheet', help = '"samples.pairs.csv" samplesheet to use for paired analysis', default = None, type = str)
    parser.add_argument("--no_qsub_wait", default = False, action = "store_true", dest = 'no_qsub_wait', help="Do not wait for the qsub jobs to finish in a new analysis")
    parser.add_argument("--no_downstream", default = False, action = "store_true", dest = 'no_downstream', help="Do not run the downstream snsxt analysis tasks after the completion of a new analysis")


    # create the parser for the "d" downstream command
    parser_d = subparsers.add_parser('d', help = 'Run downstream snsxt analysis pipeline tasks on an existing sns pipeline output')
    parser_d.set_defaults(func = run_main)
    parser_d.add_argument('-i', '--input_dir', '--analysis_dir', dest = "analysis_dir", help = "Path to the directory containing the existing sns pipeline output", required = True)

    # parse the args and run the default parser function
    args = parser.parse_args()
    args.func(args)


# ~~~~ RUN ~~~~~~ #
if __name__ == "__main__":
    parse()
