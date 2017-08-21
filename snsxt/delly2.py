#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Module for running Delly2 with the sns pipeline
'''
# ~~~~~ LOGGING ~~~~~~ #
from util import log
import logging
import os

script_timestamp = log.timestamp()
scriptdir = os.path.dirname(os.path.realpath(__file__))
scriptname = os.path.basename(__file__)
logdir = os.path.join(scriptdir, 'logs')
log_file = os.path.join(scriptdir, logdir, '{0}.{1}.log'.format(scriptname, script_timestamp))

# add a per-module timestamped logging file handler
logger = log.build_logger(name = "delly2")
logger.addHandler(log.create_main_filehandler(log_file = log_file, name = "delly2"))
# make the file handler global for use elsewhere
main_filehandler = log.get_logger_handler(logger = logger, handler_name = 'delly2')
logger.debug("loading delly2 module")




# ~~~~ SETUP CONFIGS ~~~~~~ #
import config

configs = {}
configs['bin'] = config.Delly2['bin']
configs['bcftools_bin'] = config.Delly2['bcftools_bin']
configs['hg19_fa'] = config.Delly2['hg19_fa']
configs['call_types'] = config.Delly2['call_types']
configs['output_SV_bcf_ext'] = config.Delly2['output_SV_bcf_ext']
configs['output_dir'] = config.Delly2['output_dir']



# ~~~~ LOAD MORE PACKAGES ~~~~~~ #
# system modules
import sys
import csv

# this program's modules
import config
from util import tools as t
from util import find
from util import qsub
# from sns_classes import AnalysisItem
# from sns_classes import SnsAnalysisSample
from sns_classes import SnsWESAnalysisOutput




# ~~~~ CUSTOM FUNCTIONS ~~~~~~ #
def delly2_cmd(sampleID, bam_file, output_dir):
    '''
    Build the terminal commands to run Delly2 on a single sample
    '''
    logger.debug("Running Delly2 on sample: {0}".format(sampleID))

    # get params from config
    delly2_bin = config.Delly2['bin']
    bcftools_bin = config.Delly2['bcftools_bin']
    hg19_fa = config.Delly2['hg19_fa']
    call_types = config.Delly2['call_types']
    output_SV_bcf_ext = config.Delly2['output_SV_bcf_ext']
    logger.debug([delly2_bin, bcftools_bin, hg19_fa, call_types])

    # [ ! -f "${sample_output_SV_bcf}" ] && ${delly2_bin} call -t ${call_type_arg} -g "${hg19_fa}" -o "${sample_output_SV_bcf}" "${bam_file}"
    SV_calling_commands = []
    for call_type_name, call_type_arg in call_types:
        logger.debug("call_type: {0}".format([call_type_name, call_type_arg]))
        sample_output_SV_bcf_basename = ''.join([sampleID, '.' + call_type_name, output_SV_bcf_ext])
        sample_output_SV_bcf = os.path.join(output_dir, sample_output_SV_bcf_basename)
        command = '''
{0} call -t {1} -g "{2}" -o "{3}" "{4}"
'''.format(
delly2_bin, call_type_arg, hg19_fa, sample_output_SV_bcf, bam_file
)
        SV_calling_commands.append(command)
    delly2_command = '\n\n'.join(SV_calling_commands)
    logger.debug(delly2_command)
    return(delly2_command)



def run_delly2(analysis):
    '''
    Run Delly2 on the samples in the analysis
    analysis is a SnsWESAnalysisOutput objects
    '''
    logger.debug("Running Delly2 on analysis: {0}".format(analysis))

    samples = analysis.samples
    # setup the output locations
    delly2_output_dir = config.Delly2['output_dir']

    ## !! intentional error placed here to generate bad qsub jobs for testing !!
    output_dir = t.mkdirs(path = os.path.join(analysis.dir, delly2_output_dir), return_path = True)
    # qsub_log_dir = t.mkdirs(path = analysis.list_none(analysis.dirs['logs-qsub']), return_path = True)
    qsub_log_dir = analysis.dirs['logs-qsub']

    # track the qsub job submissions
    jobs = []

    for sample in samples:
        sample_bam = sample.get_output_files(analysis_step = 'BAM-GATK-RA-RC', pattern = '*.dd.ra.rc.bam')
        if sample_bam:
            command = delly2_cmd(sampleID = sample.id, bam_file = sample_bam, output_dir = output_dir)
            # job = qsub.submit(command = command, params = '-q all.q -j y -wd $PWD', name = "delly2.{0}".format(sample.id), stdout_log_dir = qsub_log_dir, stderr_log_dir = qsub_log_dir, return_stdout = True, verbose = True, sleeps = 1)
            # proc_stdout = qsub.submit_job(command = command, params = '-q all.q -j y -wd $PWD', name = "delly2.{0}".format(sample.id), stdout_log_dir = qsub_log_dir, stderr_log_dir = qsub_log_dir, return_stdout = True, verbose = True)
            # job_id, job_name = qsub.get_job_ID_name(proc_stdout)

            # logger.debug("Submitted job: {0} [{1}]".format(job.name, job.id))
            # jobs.append(job)
            logger.debug("Job comand is:\n\n{0}\n".format(command))
        else:
            logger.error("Bam file not found for sample {0}, sample_bam: {1}".format(sample, sample_bam))
    # wait for jobs to complete, if there are any in the list
    # if jobs:
    #     logger.debug([(job.id, job.running(), job.present()) for job in jobs])
        # jobs_started = qsub.wait_all_jobs_start(job_id_list)
        # if jobs_started:
        #     qsub.wait_all_jobs_finished(job_id_list)




def main(extra_handlers = None):
    '''
    Main control function for the program
    '''
    # check for extra logger handlers that might have been passed
    if extra_handlers != None:
        logger.debug("extra_handlers: {0}".format(extra_handlers))
        for h in extra_handlers:
            logger.addHandler(h)

    logger.info("Log file path: {0}".format(log.logger_filepath(logger = logger, handler_name = "NGS580_demultiplexing.email")))


def run():
    '''
    Run the monitoring program
    arg parsing goes here, if program was run as a script
    '''
    main()

if __name__ == "__main__":
    run()
