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

def logpath():
    '''
    Return the path to the main log file; needed by the logging.yml
    use this for dynamic output log file paths & names
    '''
    global log_file
    return(log.logpath(logfile = log_file))

# load the logging config
config_yaml = os.path.join(scriptdir, 'logging.yml')
logger = log.log_setup(config_yaml = config_yaml, logger_name = "run")

# make the 'main' file handler global for use elsewhere
main_filehandler = log.get_logger_handler(logger = logger, handler_name = 'main')
console_handler = log.get_logger_handler(logger = logger, handler_name = "console", handler_type = 'StreamHandler')

logger.debug("The program is starting...")
logger.debug("Path to the monitor's log file: {0}".format(log.logger_filepath(logger = logger, handler_name = "main")))




# ~~~~ GET EXTERNAL CONFIGS ~~~~~~ #
import config
email_recipients = config.sns['email_recipients']
analysis_output_index = config.sns['analysis_output_index']


# ~~~~ CREATE INTERNAL CONFIGS ~~~~~~ #
sns_config = {}
sns_config['email_recipients'] = email_recipients
sns_config['analysis_output_index'] = analysis_output_index


# ~~~~ LOAD MORE PACKAGES ~~~~~~ #
# system modules
import sys
import csv
from time import sleep

# this program's modules
from util import tools as t
from util import find
from sns_classes.classes import SnsWESAnalysisOutput
from sns_tasks import Delly2



# ~~~~ CUSTOM FUNCTIONS ~~~~~~ #
def demo():
    '''
    Run a demo of the program
    '''
    analysis_id = "170623_NB501073_0015_AHY5Y3BGX2"
    results_id = "results_2017-06-26_20-11-26"
    results_dir = os.path.join(scriptdir, 'results_dir')
    x = SnsWESAnalysisOutput(dir = results_dir, id = analysis_id, results_id = results_id, extra_handlers = [main_filehandler])
    # t.my_debugger(locals().copy())
    logger.debug(x)
    logger.debug(x.get_files(name = 'paired_samples'))
    logger.debug(x.get_files(name = 'samples_fastq_raw'))
    logger.debug(x.get_files(name = 'summary_combined_wes'))
    logger.debug(x.get_files(name = 'settings'))
    logger.debug(x.get_files(name = 'targets_bed'))
    logger.debug(x.samples)
    logger.debug(x.get_dirs(name = 'VCF-GATK-HC'))
    logger.debug(x.get_dirs(name ='BAM-GATK-RA-RC'))
    y = x.samples[0].search_pattern
    logger.debug(find.find(search_dir = x.list_none(x.get_dirs(name ='BAM-GATK-RA-RC')), inclusion_patterns = ("*.bam", y), search_type = 'file', match_mode = 'all') )

    logger.debug(x.samples[0].get_output_files(analysis_step = 'BAM-GATK-RA-RC', pattern = '*.dd.ra.rc.bam'))


def run_task(analysis, task, *args, **kwargs):
    '''
    Run an analysis task on all the samples in the analysis output
    analysis is an SnsWESAnalysisOutput object
    task is a module with a function 'main' that runs a single sample and returns a qsub job
    '''
    samples = analysis.get_samples()
    jobs = []
    for sample in samples:
        # task should return a qsub Job object
        job = task.main(sample = sample, *args, **kwargs)
        if job:
            jobs.append(job)
    logger.info('Submitted jobs: {0}'.format([job.id for job in jobs]))


    # TODO: debug here 
    logger.debug('Waiting for all jobs to start...')
    # wait for start
    while not all([job.running() for job in jobs]):
        sleep(1)
        # make sure the jobs did not die
        if all([not job.present() for job in jobs]):
            logger.warning('All jobs exited while waiting for jobs to start')
    # wait for jobs to finish
    # make sure there's at least 1 job running
    if any([job.running() for job in jobs]):
        logger.debug('Waiting for all jobs to finish...')
        while any([job.running() for job in jobs]):
            sleep(5)
    # jobs are all done
    if not any([job.running() for job in jobs]) and not any([job.present() for job in jobs]):
        logger.debug('No jobs remaining in the job queue')
    elif not any([job.running() for job in jobs]) and any([job.present() for job in jobs]):
        logger.warning('Some jobs are remaining in the job queue but are not running')
    return()




def main():
    '''
    Main control function for the program
    '''
    analysis_id = "170623_NB501073_0015_AHY5Y3BGX2"
    results_id = "results_2017-06-26_20-11-26"
    results_dir = os.path.join(scriptdir, 'results_dir')
    extra_handlers = [main_filehandler]
    x = SnsWESAnalysisOutput(dir = results_dir, id = analysis_id, results_id = results_id, sns_config = sns_config, extra_handlers = extra_handlers)
    logger.debug(x)
    # t.my_debugger(locals().copy())
    run_task(analysis = x, task = Delly2, extra_handlers = extra_handlers)




def run():
    '''
    Run the monitoring program
    arg parsing goes here, if program was run as a script
    '''
    main()

# ~~~~ RUN ~~~~~~ #
if __name__ == "__main__":
    run()
