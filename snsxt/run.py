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

logger.debug("snsxt program is starting")
logger.debug("Path to the monitor's log file: {0}".format(log.logger_filepath(logger = logger, handler_name = "main")))


# ~~~~ LOAD MORE PACKAGES ~~~~~~ #
# system modules
import sys
import csv
import shutil
from time import sleep
import argparse

# this program's modules
from util import tools as t
from util import find
from util import qsub
from sns_classes.classes import SnsWESAnalysisOutput

# ~~~~ LOAD sns_tasks MODULES ~~~~~~ #
from sns_tasks import Delly2
from sns_tasks import GATK_DepthOfCoverage_custom
from sns_tasks import Summary_Avg_Coverage


# ~~~~ GET EXTERNAL CONFIGS ~~~~~~ #
import config
email_recipients = config.snsxt['email_recipients']
analysis_output_index = config.sns['analysis_output_index']


# ~~~~ CREATE INTERNAL CONFIGS ~~~~~~ #
sns_config = {}
sns_config['email_recipients'] = email_recipients
sns_config['analysis_output_index'] = analysis_output_index

sns_config['report_dir'] = config.snsxt['report_dir']
sns_config['report_files'] = config.snsxt['report_files']
sns_config['main_report'] = config.snsxt['main_report']
sns_config['report_compile_script'] = config.snsxt['report_compile_script']
sns_config['analysis_id_file'] = config.snsxt['analysis_id_file']
sns_config['results_id_file'] = config.snsxt['results_id_file']


# ~~~~ CUSTOM FUNCTIONS ~~~~~~ #
def get_report_files():
    '''
    Get the files for the report based on the configs, return a list
    '''
    report_files = []
    report_dir = os.path.join(scriptdir, sns_config['report_dir'])
    for item in sns_config['report_files']:
        file_path = os.path.join(report_dir, item)
        report_files.append(file_path)
    return(report_files)

def get_main_report_file():
    '''
    get the path to the main report file
    '''
    report_dir = os.path.join(scriptdir, sns_config['report_dir'])
    main_report_file = os.path.join(report_dir, sns_config['main_report'])
    return(main_report_file)

def compile_RMD_report(input_file):
    '''
    Compile an RMD report using the script set in the configs
    '''
    # path to the script that does the document compiling
    compile_script = os.path.join(scriptdir, sns_config['report_compile_script'])

    # shell command to run before running the script to make sure the environment is set right
    setup_command = 'module load pandoc/1.13.1'

    # make sure the script exists
    if not os.path.exists(compile_script):
        logger.error("Report script does not exist: {0}".format(compile_script))
        logger.error("Exiting program")
        sys.exit()
    else:
        # build the script command to run
        command = '''
{0}
{1} {2}
'''.format(
setup_command, # 0
compile_script, # 1
str(input_file) # 2
)
        logger.debug('Report compile command: \n{0}\n'.format(command))
        logger.debug('Compiling the report...')
        run_cmd = t.SubprocessCmd(command = command).run()
        logger.debug(run_cmd.proc_stdout)

def setup_report(output_dir, analysis_id = None, results_id = None):
    '''
    setup the main analysis report in the analysis directory
    by copying over every associated file for the report to the output dir
    '''
    # write the analysis_id and results_id to files for the report
    analysis_id_file = sns_config['analysis_id_file']
    analysis_id_filepath = os.path.join(output_dir, analysis_id_file)
    with open(analysis_id_filepath, 'w') as f:
        f.write(str(analysis_id))

    results_id_file = sns_config['results_id_file']
    results_id_filepath = os.path.join(output_dir, results_id_file)
    with open(results_id_filepath, 'w') as f:
        f.write(str(results_id))

    # set the main report output filename
    main_report_filename = '{0}_{1}_{2}'.format(str(analysis_id), str(results_id), sns_config['main_report'])

    # copy over the main report
    main_report_path = os.path.join(output_dir, main_report_filename)
    main_report_template_path = get_main_report_file()
    if os.path.exists(main_report_template_path):
        logger.debug("Copying report file '{0}' to '{1}' ".format(main_report_template_path, main_report_path))
        shutil.copy2(main_report_template_path, main_report_path)
    else:
        logger.warning("File does not exist: {0}".format(main_report_template_path))

    # copy over the supporting report files
    report_files = get_report_files()
    logger.debug("Report files are: {0}".format(report_files))
    for item in report_files:
        if os.path.exists(item):
            output_file = os.path.join(output_dir, os.path.basename(item))
            logger.debug("Copying report file '{0}' to '{1}' ".format(item, output_file))
            shutil.copy2(item, output_file)
        else:
            logger.warning("Report file '{0}' does not exist".format(item))

    # compile the report
    logger.debug("Compiling report...")
    compile_RMD_report(input_file = main_report_path)

def run_qsub_sample_task(analysis, task, qsub_wait = True, *args, **kwargs):
    '''
    Run a task that submits qsub jobs on all the samples in the analysis output
    analysis is an SnsWESAnalysisOutput object
    task is a module with a function 'main' that returns a qsub Job object
    qsub_wait = wait for all qsub jobs to complete
    '''
    # get all the Sample objects for the analysis
    samples = analysis.get_samples()
    # empty list to hold the qsub jobs
    jobs = []
    for sample in samples:
        # run the task on each sample; should return a qsub Job object
        job = task.main(sample = sample, *args, **kwargs)
        if job:
            jobs.append(job)
    logger.info('Submitted jobs: {0}'.format([job.id for job in jobs]))
    # montitor the qsub jobs until they are all completed
    if qsub_wait:
        qsub.monitor_jobs(jobs = jobs)
    return()

def run_qsub_analysis_task(analysis, task, qsub_wait = True, *args, **kwargs):
    '''
    Run a task that submits one qsub job for the analysis
    analysis is an SnsWESAnalysisOutput object
    task is a module with a function 'main' that returns a qsub Job object
    qsub_wait = wait for all qsub jobs to complete
    '''
    # empty list to hold the qsub jobs
    jobs = []
    # run the task on each sample; should return a qsub Job object
    job = task.main(sample = sample, *args, **kwargs)
    if job:
        jobs.append(job)
        logger.info('Submitted jobs: {0}'.format([job.id for job in jobs]))

        if qsub_wait:
            # montitor the qsub jobs until they are all completed
            qsub.monitor_jobs(jobs = jobs)
    else:
        logger.info("No jobs were submitted for task {0}".format(task.__name__))
    return()

def run_analysis_task(analysis, task, *args, **kwargs):
    '''
    Run a task that operates an analysis (not per-sample)
    analysis is an SnsWESAnalysisOutput object
    task is a module with a function 'main' that returns a qsub Job object
    '''
    task.main(analysis = analysis, *args, **kwargs)
    return()

def demo():
    '''
    Demo of the script run for testing
    '''
    analysis_id = "170623_NB501073_0015_AHY5Y3BGX2"
    results_id = "results_2017-06-26_20-11-26"
    analysis_dir = os.path.join(scriptdir, 'results_dir')
    main(analysis_dir = analysis_dir, analysis_id = analysis_id, results_id = results_id)


def main(analysis_dir, analysis_id = None, results_id = None, report_only = False):
    '''
    Main control function for the program
    '''
    if not report_only:
        extra_handlers = [main_filehandler]
        x = SnsWESAnalysisOutput(dir = analysis_dir, id = analysis_id, results_id = results_id, sns_config = sns_config, extra_handlers = extra_handlers)
        logger.debug(x)

        # run the per-sample tasks; each sample in the analysis is run individually
        # Delly2
        # run_qsub_sample_task(analysis = x, task = Delly2, extra_handlers = extra_handlers, qsub_wait = False)

        # GATK_DepthOfCoverage_custom
        run_qsub_sample_task(analysis = x, task = GATK_DepthOfCoverage_custom, extra_handlers = extra_handlers)

        run_analysis_task(analysis = x, task = Summary_Avg_Coverage, extra_handlers = extra_handlers)

        logger.info('All tasks completed')
    logger.debug("Starting report setup")
    setup_report(output_dir = analysis_dir, analysis_id = analysis_id, results_id = results_id)





def run():
    '''
    Run the monitoring program
    arg parsing goes here, if program was run as a script
    '''
    # ~~~~ GET SCRIPT ARGS ~~~~~~ #
    parser = argparse.ArgumentParser(description='snsxt: sns bioinformatics pipeline extension program')

    # required positional args
    parser.add_argument("analysis_dir",
        # default analysis dir location is two levels above the 'snsxt/snsxt/run.py' dir
         # /ifs/data/molecpathlab/scripts/snsxt/snsxt/run.py -> /ifs/data/molecpathlab/scripts
        default = os.path.realpath(os.path.join(os.path.realpath(__file__), "../../../")),
        help = "Path to the analysis output directory used for the sns pipeline", nargs="?")

    # optional flags
    parser.add_argument("-ai", "--analysis_id", default = None, type = str, dest = 'analysis_id', metavar = 'analysis_id', help="Identifier for the analysis")
    parser.add_argument("-ri", "--results_id", default = None, type = str, dest = 'results_id', metavar = 'results_id', help="Identifier for the analysis results, e.g. timestamp used to differentiate multiple sns pipeline outputs for the same sequencing run raw analysis input files")
    parser.add_argument("--demo", default = False, action='store_true', dest = 'run_demo', help="Run the demo of the script instead of processing args")
    parser.add_argument("--report-only", default = False, action='store_true', dest = 'report_only', help="Only run the reporting steps of the program on the specified analysis directory")

    args = parser.parse_args()

    analysis_dir = args.analysis_dir
    analysis_id = args.analysis_id
    results_id = args.results_id
    run_demo = args.run_demo
    report_only = args.report_only

    # logger.debug(args)


    if run_demo:
        demo()
    else:
        main(analysis_dir = analysis_dir, analysis_id = analysis_id, results_id = results_id, report_only = report_only)

# ~~~~ RUN ~~~~~~ #
if __name__ == "__main__":
    run()
