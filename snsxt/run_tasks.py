#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Contains functions for running analysis tasks
"""
# ~~~~~ LOGGING ~~~~~~ #
import logging
logger = logging.getLogger(__name__)

# ~~~~~ LOAD MORE PACKAGES ~~~~~ #
import os
import json
from sns_classes.classes import SnsWESAnalysisOutput
import mail
import sns_tasks
import job_management
import setup_report
import validation
import _exceptions as _e

# ~~~~~ LOAD CONFIGS ~~~~~ #
import config
configs = config.config


# ~~~~~ GLOBALS ~~~~~ #
extra_handlers = []


# ~~~~~ FUNCTIONS ~~~~~ #
def get_task_class(task_name):
    """
    Gets the task's class from the `sns_tasks` module

    Parameters
    ----------
    task_name: str
        the name of an analysis task, assumed to correspond to a Class loaded in the `sns_tasks` module

    Returns
    -------
    Class
        the Class object matching the `task_name`
    """
    # make sure the task is present in sns_tasks
    if not task_name in dir(sns_tasks):
        logger.error('Task {0} was not found in the sns_tasks module'.format(task_name))
        raise _e.SnsTaskMissing(message = 'Task {0} was not found in the sns_tasks module'.format(task_name), errors = '')
    else:
        logger.debug('Loading task {0} '.format(task_name))
    # load the task class from the module
    task_class = getattr(sns_tasks, task_name)
    return(task_class)



def run_tasks(tasks, analysis_dir = None, analysis = None, debug_mode = False, **kwargs):
    """
    Runs a series of analysis tasks

    Parameters
    ----------
    tasks: dict
        a dictionary (e.g. loaded from a YAML formatted `task_list`) containing the names of analysis tasks to be run
    analysis_dir: str
        the path to a directory to use for the analysis. For `sns` tasks, this corresponds to the data output location. For downstream `tasks`, this will be used to create a `SnsWESAnalysisOutput` object
    analysis: SnsWESAnalysisOutput
        object representing output from an `sns wes` analysis pipeline output on which to run downstream analysis tasks
    debug_mode: bool
        prevent the program from halting if errors are found in qsub log output files; defaults to `False`. `True` = do not stop for qsub log errors, `False` = stop if errors are found
    kwargs: dict
        a dictionary containing extra args to pass to the `task_class` upon initialization

    Returns
    -------
    tasks_output: dict
        a dictionary containing items output by the analysis task(s) which were run

    Todo
    ----
    Figure out what should be contained in `tasks_output`

    """
    # items output by tasks which should be returned by this function
    tasks_output = {}
    # list of files to send in output email
    tasks_output['email_files'] = []

    if analysis_dir and analysis:
        raise _e.ArgumentError(message = 'Both analysis_dir and analysis were passed; there can be only one.', errors = '')

    if not analysis_dir and not analysis:
        raise _e.ArgumentError(message = 'Neither analysis_dir nor analysis were passed; there must be one.', errors = '')


    for task_name, task_params in tasks.items():
        task_class = get_task_class(task_name)

        # create the task object
        if analysis_dir:
            task = task_class(analysis_dir = analysis_dir, extra_handlers = extra_handlers, **kwargs)
        if analysis:
            # make sure the ana analysis ouput object is valid before continuing
            if not debug_mode:
                if not analysis.is_valid:
                    err_message = 'The analysis did not pass validations\n'
                    validations_message = json.dumps(analysis.validations, indent = 4)
                    logger.error(err_message)
                    raise _e.AnalysisInvalid(message = err_message + validations_message, errors = '')
            task = task_class(analysis = analysis, extra_handlers = extra_handlers)

        # run the task
        if task_params:
            # with the params
            task_output = task.run(**task_params)
        else:
            # without the params
            task_output = task.run()

        # check for files from the task which should be included in email output
        expected_email_files = task.get_expected_email_files()
        logger.debug('task email files: {0}'.format(expected_email_files))
        if expected_email_files:
            for item in expected_email_files:
                mail.email_files.append(item)

        # check the output of the task
        if task_output:
            # check for background qsub jobs output by the task
            task_jobs = []
            for item in task_output:
                if isinstance(item, qsub.Job):
                    task_jobs.append(item)
            # if no task_jobs were produced, validate the task output immediately
            if not task_jobs:
                logger.debug('Validating task output files')
                task.validate_output()
            else:
                # add task jobs to background jobs
                logger.debug('Background qsub jobs were generated by the task and will be monitored at program completion')
                for job in task_jobs:
                    job_management.background_jobs.append(job)
                # add task expected output to background output to be validated later
                logger.debug('Expected output files for the task will be validated at program completion')
                task_output_files = task.get_expected_output_files()
                for item in task_output_files:
                    validation.background_output_files.append(item)

    # monitor and validate all background jobs
    job_management.monitor_validate_background_jobs()

    # validate all background output files
    validation.validate_background_output_files()

    return(tasks_output)


def run_sns_tasks(task_list, analysis_dir, **kwargs):
    """
    Runs tasks which run analysis commands in the context of creating and running new `sns` pipeline analyses.

    Parameters
    ----------
    task_list: dict
        dictionary of tasks read in from the tasks list file; must have a ``sns`` key with sub-dicts corresponding to ``sns`` tasks to run
    analysis_dir: str
        path to a directory to hold the analysis output
    kwargs: dict
        dictionary containing extra args to pass to `run_tasks`

    Notes
    -----
    Each sns task will be run individually, so that all qsub jobs will be monitored to completion at every step.

    """
    # get the args that were passed
    fastq_dirs = kwargs.pop('fastq_dirs')
    targets_bed = kwargs.pop('targets_bed')
    probes_bed = kwargs.pop('probes_bed')
    pairs_sheet = kwargs.pop('pairs_sheet')

    logger.info('Creating new sns analysis in dir {0}'.format(os.path.abspath(analysis_dir)))

    # run tasks one at a time
    tasks = task_list['sns']
    for key, value in tasks.items():
        run_tasks(tasks = {key: value}, analysis_dir = analysis_dir, fastq_dirs = fastq_dirs, targets_bed = targets_bed, probes_bed = probes_bed, pairs_sheet = pairs_sheet, **kwargs)

def run_snsxt_tasks(task_list, analysis_dir, **kwargs):
    """
    Runs the downstream `snsxt` analysis tasks on `sns` pipeline output

    Parameters
    ----------
    task_list: dict
        dictionary of tasks read in from the tasks list file; must have a ``tasks`` key with sub-dicts corresponding to  tasks to run
    analysis_dir: str
        path to a directory containing `sns` analysis output
    kwargs: dict
        dictionary containing extra args to pass to `run_tasks`

    """
    # get the args that were passed
    analysis_id = kwargs.pop('analysis_id')
    results_id = kwargs.pop('results_id')
    debug_mode = kwargs.pop('debug_mode')

    tasks = task_list['tasks']
    logger.info('Loading analysis {0} : {1} from dir {2}'.format(analysis_id, results_id, os.path.abspath(analysis_dir)))
    analysis = SnsWESAnalysisOutput(dir = analysis_dir, id = analysis_id, results_id = results_id, sns_config = configs, extra_handlers = extra_handlers)
    run_tasks(tasks, analysis = analysis, debug_mode = debug_mode, **kwargs)

    if task_list.get('setup_report', None):
        # TODO: move report out of this function and into main as part of cleanup
        logger.debug('Starting report setup')
        setup_report.setup_report(output_dir = analysis_dir, analysis_id = analysis_id, results_id = results_id)
