#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sets up and compiles the parent analysis report for the pipeline output
"""
# ~~~~~ LOGGING ~~~~~~ #
import os
import shutil
from util import log
import logging
import config
from util import tools
import validation

logger = logging.getLogger(__name__)

# path to the script's dir
scriptdir = os.path.dirname(os.path.realpath(__file__))
scriptname = os.path.basename(__file__)
script_timestamp = log.timestamp()

# ~~~~~ LOAD CONFIGS ~~~~~ #
config.config['report_dir'] = os.path.join(config.config['snsxt_dir'], config.config['report_dir'])
config.config['report_compile_script'] = os.path.join(config.config['snsxt_dir'], config.config['report_compile_script'])
config.config['main_report'] = os.path.join(config.config['report_dir'], config.config['main_report'])

configs = config.config



# ~~~~ CUSTOM FUNCTIONS ~~~~~~ #
def get_report_files():
    """
    Gets the supporting files for the parent analysis report based on the configs. These include files with helper functions, sub-reports, etc.

    Returns
    -------
    list
        a list of paths to files that should be used to set up the parent analysis report
    """
    report_files = []
    report_dir = configs['report_dir']
    for item in configs['report_files']:
        file_path = os.path.join(report_dir, item)
        report_files.append(file_path)
    return(report_files)

def get_main_report_file():
    """
    Gets the path to the main parent report .Rmd file which should be used to compile the analysis report.

    Returns
    -------
    str
        the path to the parent .Rmd file to use in compiling the report
    """
    report_dir = configs['report_dir']
    main_report_file = configs['main_report']
    return(main_report_file)

def compile_RMD_report(input_file):
    """
    Compiles a .Rmd format report using the R script set in the configs.

    Todo
    ----
    Need to raise an exception here in case the report script does not exist

    Returns
    -------
    SubprocessCmd
        the ``tools.SubprocessCmd`` object for the shell command that was run to execute the report compilation script
    """
    # path to the script that does the document compiling
    compile_script = configs['report_compile_script']

    # shell command to run before running the script to make sure the environment is set right
    setup_command = 'module load pandoc/1.13.1'

    # make sure the script exists
    if not os.path.exists(compile_script):
        logger.error("Report script does not exist: {0}".format(compile_script))
        logger.error("Exiting program")
        # TODO: raise exception here!
        sys.exit()
    else:
        # build the script command to run
        command = """
{0}
{1} {2}
""".format(
setup_command, # 0
compile_script, # 1
str(input_file) # 2
)
        logger.debug('Report compile command: \n{0}\n'.format(command))
        logger.debug('Compiling the report...')
        run_cmd = tools.SubprocessCmd(command = command).run()
        logger.debug(run_cmd.proc_stdout)
        logger.debug(run_cmd.proc_stderr)
        return(run_cmd)

def setup_report(output_dir, analysis_id = None, results_id = None):
    """
    setup the main analysis report in the analysis directory
    by copying over every associated file for the report to the output dir
    """
    # write the analysis_id and results_id to files for the report
    analysis_id_file = configs['analysis_id_file']
    analysis_id_filepath = os.path.join(output_dir, analysis_id_file)
    with open(analysis_id_filepath, 'w') as f:
        f.write(str(analysis_id) + '\n')

    results_id_file = configs['results_id_file']
    results_id_filepath = os.path.join(output_dir, results_id_file)
    with open(results_id_filepath, 'w') as f:
        f.write(str(results_id) + '\n')

    # set the main report output filename
    main_report_filename = '{0}_{1}_{2}'.format(str(analysis_id), str(results_id), os.path.basename(configs['main_report']))

    # copy over the main report
    main_report_path = os.path.join(output_dir, main_report_filename)
    main_report_template_path = get_main_report_file()
    validation.validate_items(items = [main_report_template_path])

    if os.path.exists(main_report_template_path):
        logger.debug("Copying report file '{0}' to '{1}' ".format(main_report_template_path, main_report_path))
        shutil.copy2(main_report_template_path, main_report_path)
    else:
        logger.warning("File does not exist: {0}".format(main_report_template_path))

    validation.validate_items(items = [main_report_path])

    # copy over the supporting report files
    report_files = get_report_files()
    logger.debug("Report files are: {0}".format(report_files))
    validation.validate_items(items = report_files)

    for item in report_files:
        if os.path.exists(item):
            output_file = os.path.join(output_dir, os.path.basename(item))
            logger.debug("Copying report file '{0}' to '{1}' ".format(item, output_file))
            shutil.copy2(item, output_file)
        else:
            logger.warning("Report file '{0}' does not exist".format(item))

    # compile the report
    logger.debug("Compiling report...")
    run_cmd = compile_RMD_report(input_file = main_report_path)
    if int(run_cmd.process.returncode) != 0:
        logger.warning("Report compilation process finished with exit status {0}; errors may have occured!".format(run_cmd.process.returncode))
    else:
        logger.debug("Finished compiling the report")
