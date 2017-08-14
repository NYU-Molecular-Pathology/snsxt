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


# ~~~~ LOAD PACKAGES ~~~~~~ #
# system modules
import sys
import csv

# this program's modules
import tools as t
import find
import config
import qsub
from classes import AnalysisItem
from classes import SnsAnalysisSample
from classes import SnsWESAnalysisOutput



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
            job = qsub.submit(command = command, params = '-q all.q -j y -wd $PWD', name = "delly2.{0}".format(sample.id), stdout_log_dir = qsub_log_dir, stderr_log_dir = qsub_log_dir, return_stdout = True, verbose = True, sleeps = 1)
            # proc_stdout = qsub.submit_job(command = command, params = '-q all.q -j y -wd $PWD', name = "delly2.{0}".format(sample.id), stdout_log_dir = qsub_log_dir, stderr_log_dir = qsub_log_dir, return_stdout = True, verbose = True)
            # job_id, job_name = qsub.get_job_ID_name(proc_stdout)

            logger.debug("Submitted job: {0} [{1}]".format(job.name, job.id))
            jobs.append(job)
        else:
            logger.error("Bam file not found for sample {0}, sample_bam: {1}".format(sample, sample_bam))
    # wait for jobs to complete, if there are any in the list
    if jobs:
        logger.debug([(job.id, job.running(), job.present()) for job in jobs])
        # jobs_started = qsub.wait_all_jobs_start(job_id_list)
        # if jobs_started:
        #     qsub.wait_all_jobs_finished(job_id_list)


def demo():
    '''
    Run a demo of the program
    '''
    global scriptdir
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
    # get_output_files(analysis_step, pattern)

    run_delly2(analysis = x)


def main():
    '''
    Main control function for the program
    '''
    global scriptdir
    analysis_id = "170623_NB501073_0015_AHY5Y3BGX2"
    results_id = "results_2017-06-26_20-11-26"
    results_dir = os.path.join(scriptdir, 'results_dir')
    x = SnsWESAnalysisOutput(dir = results_dir, id = analysis_id, results_id = results_id, extra_handlers = [main_filehandler])
    # t.my_debugger(locals().copy())
    run_delly2(analysis = x)


def run():
    '''
    Run the monitoring program
    arg parsing goes here, if program was run as a script
    '''
    main()

# ~~~~ RUN ~~~~~~ #
if __name__ == "__main__":
    run()
