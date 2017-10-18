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



configs['report_files'] = config.HapMap_variant_ref['report_files']
configs['task_files'] = config.HapMap_variant_ref['task_files']




# ~~~~ CUSTOM FUNCTIONS ~~~~~~ #
# def make_tresholds_arg():
#     '''
#     Make the command line arg for the thresholds to use
#     ex: -ct 10 -ct 50 -ct 100 -ct 500
#
#     d = {'thresholds': [10, 50, 100, 200, 500]}
#     '''
#     thresholds = configs['thresholds']
#     return(' '.join(['-ct ' + str(x) for x in thresholds]))

# def gatk_DepthOfCoverage_cmd(sampleID, bam_file, intervals_bed_file, output_dir):
#     '''
#     Build the terminal commands to run GATK DepthOfCoverage on a single sample
#
#     ex:
#     $gatk_cmd -T DepthOfCoverage -dt NONE $gatk_log_level_arg \
#     -rf BadCigar \
#     --reference_sequence $ref_fasta \
#     --intervals $bed \
#     --omitDepthOutputAtEachBase \
#     -ct 10 -ct 50 -ct 100 -ct 500 -mbq 20 -mmq 20 --nBins 999 --start 1 --stop 1000 \
#     --input_file $bam \
#     --outputFormat csv \
#     --out $out_prefix
#     '''
#     # get params from config
#     GATK_bin = configs['bin']
#     ref_fasta = configs['ref_fasta']
#     minBaseQuality = configs['minBaseQuality']
#     minMappingQuality = configs['minMappingQuality']
#     nBins = configs['nBins']
#     start = configs['start']
#     stop = configs['stop']
#     outputFormat = configs['outputFormat']
#     readFilter = configs['readFilter']
#     downsampling_type = configs['downsampling_type']
#     thresholds_arg = make_tresholds_arg()
#     output_summary_file = os.path.join(output_dir, '{0}'.format(sampleID))
#
#     gatk_cmd = '''
# java -Xms16G -Xmx16G -jar {0} -T DepthOfCoverage \
# --logging_level ERROR \
# --downsampling_type {1} \
# --read_filter {2} \
# --reference_sequence {3} \
# --omitDepthOutputAtEachBase \
# {4} \
# --intervals {5} \
# --minBaseQuality {6} \
# --minMappingQuality {7} \
# --nBins {8} \
# --start {9} \
# --stop {10} \
# --input_file {11} \
# --outputFormat {12} \
# --out {13}
# '''.format(
# GATK_bin,
# downsampling_type,
# readFilter,
# ref_fasta,
# thresholds_arg,
# intervals_bed_file,
# minBaseQuality,
# minMappingQuality,
# nBins,
# start,
# stop,
# bam_file,
# outputFormat,
# output_summary_file
# )
#     return(gatk_cmd)

def get_report_files():
    '''
    Get the files for the report based on the configs, return a list
    '''
    report_files = []
    report_dir = os.path.join(scriptdir, configs['report_dir'])
    for item in configs['report_files']:
        file_path = os.path.join(report_dir, item)
        report_files.append(file_path)
    return(report_files)

def setup_report(output_dir):
    '''
    Set up the report files output for the pipeline step
    by copying over every associated file for the report to the output dir
    '''
    report_files = get_report_files()
    logger.debug("Report files are: {0}".format(report_files))
    for item in report_files:
        output_file = os.path.join(output_dir, os.path.basename(item))
        logger.debug("Copying report file '{0}' to '{1}' ".format(item, output_file))
        shutil.copy2(item, output_file)


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
    logger.debug('Sample is: {0}'.format(sample))


    sample_annot_file = sample.list_none(sample.get_output_files(analysis_step = configs['input_dir'], pattern = configs['input_pattern']))

    hapmap_variant_file = task_utils.setup_task_file(configs['hapmap_variant_file'], output_dir, configs)


    # sample_bam = sample.list_none(sample.get_output_files(analysis_step = configs['input_dir'], pattern = configs['input_pattern']))
    # targets_bed = sample.list_none(sample.get_files('targets_bed'))

    # logger.debug(make_tresholds_arg())

    # if sample_bam and output_dir and qsub_log_dir:
    #     logger.debug('sample_bam: {0}'.format(sample_bam))
    #
    #     # make the shell command to run
    #     command = gatk_DepthOfCoverage_cmd(sampleID = sample.id, bam_file = sample_bam, output_dir = output_dir, intervals_bed_file = targets_bed)
    #     logger.debug(command)
    #
    #     # submit the command as a qsub job on the HPC
    #     # commands to create debug jobs
    #     # command = 'sleep 60'
    #     # qsub_log_dir = qsub_log_dir[:-1]
    #     job = qsub.submit(command = command, name = task_name + '.' + sample.id, stdout_log_dir = qsub_log_dir, stderr_log_dir = qsub_log_dir, verbose = True, sleeps = 1) #
    #     return(job)
    # else:
    #     logger.error('A required item does not exist')
    #
    #
    # # set up the report
    # task_utils.setup_report(output_dir = output_dir, configs = configs)

def run():
    '''
    Run the monitoring program
    arg parsing goes here, if program was run as a script
    '''
    main()

if __name__ == "__main__":
    run()
