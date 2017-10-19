#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Module for comparing each HapMap sample variant calls against
a known list of previously sequenced HapMap variants
Save the overlapping variants in a new files to load in the report
'''
# ~~~~~ LOGGING ~~~~~~ #
import logging
import os
import sys

# name for this task to use with logging, and elsewhere in the script
task_name = "HapMap_variant_ref"

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
import sys
import csv
import shutil
# this program's modules
import config
import task_utils

# ~~~~ SETUP CONFIGS ~~~~~~ #
# get external configs, make internal configs
configs = {}
# from the script
configs['this_script_timestamp'] = script_timestamp # 2017-10-10-16-44-52
configs['this_scriptdir'] = scriptdir # /ifs/data/molecpathlab/scripts/snsxt/snsxt/sns_tasks
configs['this_scriptname'] = scriptname # Summary_Avg_Coverage.py
configs['logdir'] = logdir # /ifs/data/molecpathlab/scripts/snsxt/snsxt/sns_tasks/logs
configs['log_file'] = log_file

# analysis input/output locations
configs['report_dir'] = config.sns_tasks['report_dir']
configs['files_dir'] = config.sns_tasks['files_dir']

configs['input_dir'] = config.HapMap_variant_ref['input_dir']
configs['input_pattern'] = config.HapMap_variant_ref['input_pattern']
configs['output_dir_name'] = config.HapMap_variant_ref['output_dir_name']
configs['hapmap_variant_file'] = config.HapMap_variant_ref['hapmap_variant_file']
configs['hapmap_sample_stats_file'] = config.HapMap_variant_ref['hapmap_sample_stats_file']

configs['report_files'] = config.HapMap_variant_ref['report_files']
configs['task_files'] = config.HapMap_variant_ref['task_files']




# ~~~~ CUSTOM FUNCTIONS ~~~~~~ #
def main(sample, extra_handlers = None):
    '''
    Main control function for the program
    Compare a single HapMap sample variant annotation file
    against a known reference list of HapMap variants
    output a file over the overlapping variant annotations
    for use in the report later
    '''
    # ~~~~~ REQUIRED TASK ITEMS ~~~~~ #
    # every sns_task should have these items

    # check for extra logger handlers that might have been passed
    if extra_handlers != None:
        for h in extra_handlers:
            logger.addHandler(h)

    # setup the output locations
    output_dir = t.mkdirs(path = os.path.join(sample.analysis_dir, configs['output_dir_name']), return_path = True)
    logger.debug('output_dir: {0}'.format(output_dir))

    # ~~~~~ TASK SPECIFIC CUSTOM ITEMS ~~~~~ #
    import re
    import json

    logger.debug('Sample is: {0}'.format(sample))

    # dict to hold info about the hapmap samples and their files
    hapmap_sample_stats = {}
    hapmap_sample_stats_filepath = os.path.join(output_dir, configs['hapmap_sample_stats_file'])

    # check if the sample ID indicates that it is HapMap sample
    if re.match('hapmap', sample.id, re.IGNORECASE):
        # file with the sample's ANNOVAR annotations
        sample_annot_file = sample.list_none(sample.get_output_files(analysis_step = configs['input_dir'], pattern = configs['input_pattern']))
        logger.debug('sample_annot_file is: {0}\nand has {1} entries'.format(sample_annot_file, t.num_lines(sample_annot_file, skip = 1)))

        # reference HapMap variants file; copy it over
        hapmap_variant_file = task_utils.setup_task_file(configs['hapmap_variant_file'], output_dir, configs)
        logger.debug('hapmap_variant_file is: {0}\nand has {1} entries'.format(hapmap_variant_file, t.num_lines(hapmap_variant_file, skip = 1)))

        # file to save the overlaps to
        output_file = os.path.join(output_dir, os.path.basename(sample_annot_file))
        logger.debug('Output file will be: {0}'.format(output_file))

        # make the overlaps
        logger.debug('Overlapping the sample_annot_file against the hapmap_variant_file...')
        t.write_tabular_overlap(file1 = sample_annot_file, ref_file = hapmap_variant_file, output_file = output_file, delim = '\t')
        logger.debug('{0} overlaps were output'.format(t.num_lines(output_file, skip = 1)))

        # save a JSON with info about the sample ID's and their files
        hapmap_sample_stats[sample.id] = {'file': output_file}

        logger.debug('hapmap_sample_stats_filepath: {0}'.format(hapmap_sample_stats_filepath))
        t.update_json(data = hapmap_sample_stats, input_file = hapmap_sample_stats_filepath)

    else:
        logger.debug('Sample is not a HapMap sample, skipping.')



    # set up the report
    # task_utils.setup_report(output_dir = output_dir, configs = configs)

def run():
    '''
    Run the monitoring program
    arg parsing goes here, if program was run as a script
    '''
    main()

if __name__ == "__main__":
    run()
