#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Module for functions and classes to be used by all sns_task submodules
'''
# ~~~~~ LOGGING ~~~~~~ #
import logging
import os
import sys

# name for this task to use with logging, and elsewhere in the script
task_name = "task_utils"

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



# ~~~~ SETUP CONFIGS ~~~~~~ #
# get external configs, make internal configs
configs = {}
# from this script_dir
configs['this_scriptdir'] = scriptdir # /ifs/data/molecpathlab/scripts/snsxt/snsxt/sns_tasks
configs['this_scriptname'] = scriptname # Summary_Avg_Coverage.py
# from global config
configs['script_dir'] = config.sns_tasks['script_dir']
configs['report_dir'] = config.sns_tasks['report_dir']
# from task specific configs
configs['Annotation_inplace'] = config.Annotation_inplace

configs['run_script_dir'] = os.path.join(configs['this_scriptdir'], configs['script_dir'])
# /ifs/data/molecpathlab/scripts/snsxt/snsxt/sns_tasks/scripts

def get_report_files(configs):
    '''
    Get the files for the report based on the configs, return a list

    configs['this_scriptdir'] = '/ifs/data/molecpathlab/scripts/snsxt/snsxt/sns_tasks/scripts'
    full path to the 'sns_tasks/scripts' dir

    configs['report_dir'] = 'reports'

    configs['task_name'] = 'name_of_sns_task'

    configs['report_files'] = list of files in the report_dir to get
    '''
    report_files = []
    logger.debug('Getting report files for task: {0}'.format(configs['task_name']))
    # logger.debug('configs are: {0}'.format(configs))
    report_dir = os.path.join(configs['this_scriptdir'], configs['report_dir'])
    for item in configs['report_files']:
        file_path = os.path.join(report_dir, item)
        report_files.append(file_path)
    return(report_files)

def setup_report(output_dir, configs):
    '''
    Set up the report files output for the pipeline step
    by copying over every associated file for the report to the output dir
    '''
    report_files = get_report_files(configs)
    logger.debug("Report files are: {0}".format(report_files))
    for item in report_files:
        output_file = os.path.join(output_dir, os.path.basename(item))
        logger.debug("Copying report file '{0}' to '{1}' ".format(item, output_file))
        shutil.copy2(item, output_file)

def Annotation_inplace(input_dir, annotation_method, extra_handlers = None):
    '''
    Function for annotating genomic regions and variants output by other pipeline steps in-place
    without creating a new output directory just for the annotations
    because for reporting purposes, you might end up needing both the pipeline task
    raw output and the annotations in the same location.

    This function will use the ANNOVAR annotation script, which finds and runs ANNOVAR
    on all the .bed files found (maybe .vcf too? TODO: decide this later)

    annotation_method is one of ANNOVAR, ChIPseeker, or biomaRt_ChIPpeakAnno,
    based on the external configs which are based on the subdirs in the annotation
    package

    TODO: add testing to this function... somehow...

    example command output:
    annotation_command = '/ifs/data/molecpathlab/scripts/snsxt/snsxt/sns_tasks/scripts/annotate-peaks/ANNOVAR/annotate.R -d /ifs/data/molecpathlab/scripts/snsxt/example_sns_analysis2/Summary-Avg-Coverage --bin-dir /ifs/data/molecpathlab/bin/annovar_annotate --db-dir /ifs/data/molecpathlab/bin/annovar_annotate/db --genome hg19'
    '''
    # check for extra logger handlers that might have been passed
    if extra_handlers != None:
        for h in extra_handlers:
            logger.addHandler(h)

    logger.debug("Starting annotation for dir: {0}".format(input_dir))
    logger.debug("Annotation method: {0}".format(annotation_method))

    scripts_dir_name = configs['Annotation_inplace']['scripts_dir_name']
    # annotate-peaks

    run_script_dir = configs['run_script_dir']
    # /ifs/data/molecpathlab/scripts/snsxt/snsxt/sns_tasks/scripts

    annotation_script = os.path.join(annotation_method, configs['Annotation_inplace']['annotation_methods'][annotation_method])
    # ANNOVAR/annotate.R

    annotation_script_path = os.path.join(run_script_dir, scripts_dir_name, annotation_script)
    logger.debug('path to annotation script will be: {0}'.format(annotation_script_path))

    # create the annotation_command; default is None
    annotation_command = None

    # ANNOVAR annotation method
    if annotation_method == "ANNOVAR":
        bin_dir = configs['Annotation_inplace']['ANNOVAR_bin_dir']
        db_dir = configs['Annotation_inplace']['ANNOVAR_db_dir']
        genome = configs['Annotation_inplace']['ANNOVAR_genome']

        annotation_command = '''
{0} -d {1} --bin-dir {2} --db-dir {3} --genome {4}
'''.format(
annotation_script_path, # 0
input_dir, # 1
bin_dir, # 2
db_dir, # 3
genome # 4
)
        logger.debug('ANNOVAR script command: {0}'.format(annotation_command))

    # run the annotation command
    if annotation_command:
        run_cmd = t.SubprocessCmd(command = annotation_command).run()
        logger.debug(run_cmd.proc_stderr)

    return()
