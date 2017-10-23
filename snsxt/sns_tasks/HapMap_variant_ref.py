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
configs['task_name'] = task_name


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
configs['config_file'] = config.HapMap_variant_ref_file



# ~~~~ CUSTOM FUNCTIONS ~~~~~~ #
def main(sample, extra_handlers = None):
    '''
    Main control function for the program
    Compare a single HapMap sample variant annotation file
    against a known reference list of HapMap variants
    output a file containing the variant annotations found which were not in the reference variant list
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

    # get paths to files for the sample
    # file with the sample's ANNOVAR annotations
    sample_annot_file = sample.list_none(sample.get_output_files(analysis_step = configs['input_dir'], pattern = configs['input_pattern']))
    logger.debug('sample_annot_file is: {0}\nand has {1} entries'.format(sample_annot_file, t.num_lines(sample_annot_file, skip = 1)))

    # reference HapMap variants file
    # hapmap_variant_file = task_utils.setup_task_file(configs['hapmap_variant_file'], output_dir, configs)
    hapmap_variant_file = os.path.join(configs['this_scriptdir'], configs['files_dir'], configs['hapmap_variant_file'])

    # JSON file to hold info about the hapmap samples and their files
    # hapmap_stats_filepath = os.path.join(output_dir, configs['hapmap_sample_stats_file'])

    # name of the reference file
    # ref_name = os.path.splitext(os.path.basename(hapmap_variant_file))[0]

    # file to save the variants not in the reference list
    output_file = os.path.join(output_dir, os.path.basename(sample_annot_file))

    # # data to save in the JSON output
    # data = {}

    # check if the sample ID indicates that it is HapMap sample
    if re.match('hapmap', sample.id, re.IGNORECASE):
        logger.debug('Sample is a HapMap sample')



        # reference HapMap variants file; copy it over
        logger.debug('hapmap_variant_file is: {0}\nand has {1} entries'.format(hapmap_variant_file, t.num_lines(hapmap_variant_file, skip = 1)))

        logger.debug('Output file will be: {0}'.format(output_file))

        # find the new variants
        logger.debug('Overlapping the sample_annot_file against the hapmap_variant_file...')
        t.write_tabular_overlap(file1 = sample_annot_file, ref_file = hapmap_variant_file, output_file = output_file, delim = '\t', inverse = True)
        logger.debug('{0} non-overlapping variants were output'.format(t.num_lines(output_file, skip = 1)))

        # save a JSON with info about the sample ID's and their files
        # logger.debug('hapmap_stats_filepath: {0}'.format(hapmap_stats_filepath))

        # check if the output JSON file already exists
        # if t.item_exists(hapmap_stats_filepath):
            # logger.debug('File {0} already exists, loading data'.format(hapmap_stats_filepath))
            # # import the old data
            # data = t.load_json(hapmap_stats_filepath)
            #
            # # update the 'samples' dict with this sample
            # try:
            #     data['samples'].update({sample.id: {'file': output_file} })
            #     logger.debug('Upated "samples" entry in the data')
            # except KeyError:
            #     # or make the entry instead
            #     logger.debug('"samples" entry not found in the data, it will be created')
            #     data['samples'] = {sample.id: {'file': output_file} }
            #
            # # update the 'ref' dict
            # try:
            #     data['ref'].update({ref_name: hapmap_variant_file})
            #     logger.debug('Upated "ref_name" entry in the data')
            # except KeyError:
            #     # or make the entry instead
            #     logger.debug('"ref_name" entry not found in the data, it will be created')
            #     data['ref'] = {ref_name: hapmap_variant_file}
            #
            # # save the data to the JSON file
            # logger.debug('Saving the data to file: {0}'.format(hapmap_stats_filepath))
            # t.write_json(object = data, output_file = hapmap_stats_filepath)
        # else:
            # if the file doesn't exist, create the data and save it to the file
            # logger.debug('File {0} does not exists, data will be created and saved to it'.format(hapmap_stats_filepath))
            #
            # data['samples'] = {sample.id: {'file': output_file} }
            # data['ref'] = {ref_name: hapmap_variant_file}
            # t.write_json(object = data, output_file = hapmap_stats_filepath)

    else:
        logger.debug('Sample is not a HapMap sample, skipping.')

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
