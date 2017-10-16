#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Functions to run the analysis tasks in the pipeline
'''
# ~~~~~ LOGGING ~~~~~~ #
import os
from util import log
import logging

logger = logging.getLogger(__name__)

# path to the script's dir
scriptdir = os.path.dirname(os.path.realpath(__file__))
scriptname = os.path.basename(__file__)
script_timestamp = log.timestamp()

# ~~~~ LOAD MORE PACKAGES ~~~~~~ #
from util import qsub


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
