#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Run a series of analysis tasks, as an extension to the sns pipeline output

tested under Python 2.7
'''
# ~~~~~ LOGGING ~~~~~~ #
import os
import log
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
logger.debug('{0}'.format(type(main_filehandler)))
logger.debug('{0}'.format(isinstance(main_filehandler, logging.FileHandler)))
logger.debug('{0}'.format(type(console_handler)))

# ~~~~ LOAD PACKAGES ~~~~~~ #
# system modules
import sys
import csv

# this program's modules
import find
import config
from classes import AnalysisItem
from classes import SnsAnalysisSample
from classes import SnsWESAnalysisOutput



# ~~~~ CUSTOM FUNCTIONS ~~~~~~ #
def run_delly2():
    '''
    Run Delly2 on a sample
    '''

def demo():
    '''
    Run a demo of the program
    '''
    analysis_id = "170623_NB501073_0015_AHY5Y3BGX2"
    results_id = "results_2017-06-26_20-11-26"
    results_dir = "results_dir"
    x = SnsWESAnalysisOutput(dir = results_dir, id = analysis_id, results_id = results_id, extra_handlers = [main_filehandler, console_handler])
    logger.debug(x)
    logger.debug(x.get_files(name = 'paired_samples'))
    logger.debug(x.get_files(name = 'samples_fastq_raw'))
    logger.debug(x.get_files(name = 'summary_combined_wes'))
    logger.debug(x.get_files(name = 'settings'))
    logger.debug(x.get_files(name = 'targets_bed'))
    logger.debug(x.samples)

def main():
    '''
    Main control function for the program
    '''
    demo()


def run():
    '''
    Run the monitoring program
    arg parsing goes here, if program was run as a script
    '''
    main()

if __name__ == "__main__":
    run()
