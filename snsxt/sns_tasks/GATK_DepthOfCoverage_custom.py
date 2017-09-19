#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Module for running custom thresholds GATK DepthOfCoverage with the sns pipeline
'''
# ~~~~~ LOGGING ~~~~~~ #
import logging
import os
import sys

# name for this task to use with logging, and elsewhere in the script
task_name = "GATK_DepthOfCoverage_custom"

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
# this program's modules
import config


# ~~~~ SETUP CONFIGS ~~~~~~ #
# get external configs, make internal configs
configs = {}
# GATK_DepthOfCoverage_custom program configs
configs['bin'] = config.GATK_DepthOfCoverage_custom['bin']
configs['ref_fasta'] = config.GATK_DepthOfCoverage_custom['ref_fasta']
configs['thresholds'] = config.GATK_DepthOfCoverage_custom['thresholds']
# analysis input/output locations
configs['input_dir'] = config.GATK_DepthOfCoverage_custom['input_dir']
configs['input_pattern'] = config.GATK_DepthOfCoverage_custom['input_pattern']
configs['output_dir_name'] = config.GATK_DepthOfCoverage_custom['output_dir_name']




# ~~~~ CUSTOM FUNCTIONS ~~~~~~ #
def make_tresholds_arg():
    '''
    Make the command line arg for the thresholds to use
    ex: -ct 10 -ct 50 -ct 100 -ct 500

    d = {'thresholds': [10, 50, 100, 200, 500]}
    '''
    return(' '.join(['-ct ' + str(x) for x in configs['thresholds']]))

def gatk_DepthOfCoverage_cmd(sampleID, bam_file, output_dir):
    '''
    Build the terminal commands to run GATK DepthOfCoverage on a single sample
    '''






def main(sample, extra_handlers = None):
    '''
    Main control function for the program
    Runs GATK DepthOfCoverage on a single sample from an sns analysis
    sample is an SnsAnalysisSample object
    return the qsub job for the sample
    '''
    # logger.debug(configs)
    # sys.exit()

    # check for extra logger handlers that might have been passed
    if extra_handlers != None:
        for h in extra_handlers:
            logger.addHandler(h)

    logger.debug('Sample is: {0}'.format(sample))
    log.print_filehandler_filepaths_to_log(logger = logger)

    # setup the output locations
    output_dir = t.mkdirs(path = os.path.join(sample.analysis_dir, configs['output_dir_name']), return_path = True)
    logger.debug('output_dir: {0}'.format(output_dir))

    qsub_log_dir = sample.list_none(sample.analysis_config['dirs']['logs-qsub'])
    logger.debug('qsub_log_dir: {0}'.format(qsub_log_dir))

    sample_bam = sample.list_none(sample.get_output_files(analysis_step = configs['input_dir'], pattern = configs['input_pattern']))

    # logger.debug(make_tresholds_arg())

    if sample_bam and output_dir and qsub_log_dir:
        logger.debug('sample_bam: {0}'.format(sample_bam))

        # make the shell command to run
        # command = delly2_cmd(sampleID = sample.id, bam_file = sample_bam, output_dir = output_dir)

        # submit the command as a qsub job on the HPC
        # commands to create debug jobs
        # command = 'sleep 60'
        # qsub_log_dir = qsub_log_dir[:-1]
        # job = qsub.submit(command = command, name = task_name + '.' + sample.id, stdout_log_dir = qsub_log_dir, stderr_log_dir = qsub_log_dir, verbose = True, sleeps = 1) #
        # return(job)
    else:
        logger.error('A required item does not exist')

def run():
    '''
    Run the monitoring program
    arg parsing goes here, if program was run as a script
    '''
    main()

if __name__ == "__main__":
    run()
