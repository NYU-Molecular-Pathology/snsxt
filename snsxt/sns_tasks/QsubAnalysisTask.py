#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module for the base QsubAnalysisTask object class
"""
from AnalysisTask import AnalysisTask

class QsubAnalysisTask(AnalysisTask):
    """
    Analysis Task task that will submit a single qsub job for the entire analysis
    """
    def __init__(self, *ars, **kwargs):
        AnalysisTask.__init__(self, *ars, **kwargs)

    def run(self, analysis = None, qsub_wait = True, *args, **kwargs):
        """
        Run a task that submits one qsub job for the analysis
        analysis is an SnsWESAnalysisOutput object
        task is a module with a function 'main' that returns a qsub Job object
        qsub_wait = wait for all qsub jobs to complete

        overrides AnalysisTask.run()
        """
        if not analysis:
            analysis = getattr(self, 'analysis', None)
        # empty list to hold the qsub jobs
        jobs = []
        # run the task on the analysis; should return a qsub Job object
        job = self.main(analysis = analysis, *args, **kwargs)
        if job:
            jobs.append(job)
            self.logger.info('Submitted jobs: {0}'.format([job.id for job in jobs]))

        if qsub_wait:
            # montitor the qsub jobs until they are all completed
            self.logger.debug('Jobs will be monitored for completion and validated')
            self.job_management.monitor_validate_jobs(jobs = jobs)
            return(None)
        else:
            return(jobs)
