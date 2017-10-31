#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Module for the main snsxt function to run the downstream analysis
'''
# ~~~~~ LOGGING ~~~~~~ #
import os
import sys
from sns_classes.classes import SnsWESAnalysisOutput
import sns_tasks
import job_management
# from util import log
from util import qsub
import logging
logger = logging.getLogger(__name__)



def snsxt(task_list, configs, *args, **kwargs):
    '''
    Function to run the sns pipeline analysis extension
    all the downstream analysis & processing steps to be done on a completed sns analysis output

    analysis = SnsWESAnalysisOutput object
    task_list, analysis = None, analysis_dir = None, analysis_id = None, results_id = None, debug_mode = False, *args, **kwargs
    '''
    analysis = kwargs.pop('analysis', None)
    analysis_dir = kwargs.pop('analysis_dir', None)
    analysis_id = kwargs.pop('analysis_id', None)
    results_id = kwargs.pop('results_id', None)
    debug_mode = kwargs.pop('debug_mode', None)
    extra_handlers = kwargs.pop('extra_handlers', [])
    if kwargs:
        raise TypeError('Unexpected **kwargs: %r' % kwargs)

    # try to load the analysis from the sns output
    if not analysis:
        if analysis_dir:
            logger.info('Loading analysis {0} : {1} from dir {2}'.format(analysis_id, results_id, os.path.abspath(analysis_dir)))
            analysis = SnsWESAnalysisOutput(dir = analysis_dir, id = analysis_id, results_id = results_id, sns_config = configs, extra_handlers = extra_handlers)
    if not analysis_dir and not analysis:
        logger.error('No analysis dir provided')
        return()

    logger.debug('analysis is {0}'.format(analysis))
    logger.debug('task_list is {0}'.format(task_list))

    # exit if the analysis is invalid, unless debug mode is enabled
    if not debug_mode:
        if not analysis.is_valid:
            logger.error('The analysis did not pass validations, exiting...')
            sys.exit()

    # run the tasks in the task list
    #  check if 'tasks' is an empty dict
    if not task_list or not task_list.get('tasks', None):
        logger.warning("No tasks were loaded")
    # run the steps included in the config
    else:
        run_task_list(analysis = analysis, task_list = task_list, extra_handlers = extra_handlers)

def run_task_list(analysis, task_list, extra_handlers = None):
    '''
    Run all the tasks in the task list

    if a task submits compute jobs via qsub but does not monitor them until completion,
    they should be captured here in a list and after all tasks are finished
    the jobs should be monitored for completion
    and their completion status validated
    '''
    if not extra_handlers:
        extra_handlers = []
    # list to capture qsub jobs submitted but not monitored by a task
    background_jobs = []

    logger.debug('Loaded task configs from file: {0}'.format(task_list['tasks'].items()))
    logger.debug('Loaded sns_tasks module contents: {}'.format(dir(sns_tasks)))
    for task_name, task_params in task_list['tasks'].items():
        # make sure the task is present in sns_tasks
        if not task_name in dir(sns_tasks):
            logger.error('Task {0} was not found in the sns_tasks module'.format(task_name))
        else:
            logger.debug('Loading task {0} '.format(task_name))
            logger.debug('task_params are {0}'.format(task_params))

            # load the task class from the module
            task_class = getattr(sns_tasks, task_name)

            # create the task object with the analysis
            task = task_class(analysis = analysis, extra_handlers = extra_handlers)

            # run the task
            if task_params:
                task_output = task.run(**task_params)
            else:
                task_output = task.run()

            # check for background qsub jobs output by the task
            if task_output:
                for item in task_output:
                    if isinstance(item, qsub.Job):
                        background_jobs.append(item)

    if background_jobs:
        # job_management.monitor_background_jobs(background_jobs = background_jobs)
        logger.debug('Background jobs will be monitored for completion and validated')
        job_management.monitor_validate_jobs(jobs = background_jobs)
