#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Module for running Delly2 with the sns pipeline
'''
# ~~~~~ LOGGING ~~~~~~ #
import logging
import os
import sys

# name for this task to use with logging, and elsewhere in the script
task_name = "Delly2"

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
logger.debug("loading Delly2 module")

# ~~~~ LOAD MORE PACKAGES ~~~~~~ #
import sys
import csv
# this program's modules
import config
# print(os.path.abspath(config.__file__)) # watch for import conflicts with parent config




# ~~~~ SETUP CONFIGS ~~~~~~ #
# get external configs, make internal configs
configs = {}
# Delly2 program configs
configs['bin'] = config.Delly2['bin']
configs['bcftools_bin'] = config.Delly2['bcftools_bin']
configs['hg19_fa'] = config.Delly2['hg19_fa']
configs['call_types'] = config.Delly2['call_types']
# analysis input/output locations
configs['input_dir'] = config.Delly2['input_dir']
configs['input_pattern'] = config.Delly2['input_pattern']
configs['output_SV_bcf_ext'] = config.Delly2['output_SV_bcf_ext']
configs['output_dir_name'] = config.Delly2['output_dir_name']




# ~~~~ CUSTOM FUNCTIONS ~~~~~~ #
def delly2_cmd(sampleID, bam_file, output_dir):
    '''
    Build the terminal commands to run Delly2 on a single sample

    Make a separate command for each SV calling type, concatenate them all together

    example command:

    delly call -t DEL -g "genome.fa" -o "results_dir/delly2-snv/Sample1.deletions.bcf" "results_dir/BAM-GATK-RA-RC/Sample1.dd.ra.rc.bam"
    '''
    # get params from config
    delly2_bin = configs['bin']
    bcftools_bin = configs['bcftools_bin']
    hg19_fa = configs['hg19_fa']
    call_types = configs['call_types']
    output_SV_bcf_ext = configs['output_SV_bcf_ext']

    # empty list to hold individual command strings
    SV_calling_commands = []

    # make a command for each SV calling type
    for call_type_name, call_type_arg in call_types:
        sample_output_SV_bcf_basename = ''.join([sampleID, '.' + call_type_name, output_SV_bcf_ext])
        sample_output_SV_bcf = os.path.join(output_dir, sample_output_SV_bcf_basename)
        command = '''
{0} call -t {1} -g "{2}" -o "{3}" "{4}"
'''.format(
delly2_bin,
call_type_arg,
hg19_fa,
sample_output_SV_bcf,
bam_file
)
        SV_calling_commands.append(command)

    # concatenate all commands
    delly2_command = '\n'.join(SV_calling_commands)
    return(delly2_command)




def main(sample, extra_handlers = None):
    '''
    Main control function for the program
    Runs Delly2 on a single sample from an sns analysis
    sample is an SnsAnalysisSample object
    return the qsub job for the sample
    '''
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


    if sample_bam and output_dir and qsub_log_dir:
        logger.debug('sample_bam: {0}'.format(sample_bam))

        # make the shell command to run
        command = delly2_cmd(sampleID = sample.id, bam_file = sample_bam, output_dir = output_dir)
        # logger.debug('command: {0}'.format(command))

        # submit the command as a qsub job on the HPC
        command = 'sleep 30'
        job = qsub.submit(command = command, name = task_name + '.' + sample.id, stdout_log_dir = qsub_log_dir, stderr_log_dir = qsub_log_dir, sleeps = 1, verbose = True)

        return(job)
    else:
        logger.error('A required item does not exist')


    # run_delly2(sample = sample)



def run():
    '''
    Run the monitoring program
    arg parsing goes here, if program was run as a script
    '''
    sample = "foo"
    main(sample)

if __name__ == "__main__":
    run()
