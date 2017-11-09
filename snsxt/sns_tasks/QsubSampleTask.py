#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module for the base QsubSampleTask object class
"""
from AnalysisSampleTask import AnalysisSampleTask

class QsubSampleTask(AnalysisSampleTask):
    """
    Analysis Task task that will submit a qsub job for every sample in the analysis
    """
    def __init__(self, *ars, **kwargs):
        AnalysisSampleTask.__init__(self, *ars, **kwargs)

    def run(self, analysis = None, qsub_wait = True, *args, **kwargs):
        """
        Run a task that submits qsub jobs on all the samples in the analysis output
        analysis is an SnsWESAnalysisOutput object
        task is a module with a function 'main' that returns a qsub Job object
        qsub_wait = wait for all qsub jobs to complete

        overrides AnalysisSampleTask.run()
        """
        if not analysis:
            analysis = getattr(self, 'analysis', None)

        # get all the Sample objects for the analysis
        samples = analysis.get_samples()

        # empty list to hold the qsub jobs
        jobs = []

        for sample in samples:
            # run the task on each sample; should return a qsub Job object
            job = self.main(sample = sample, *args, **kwargs)
            if job:
                jobs.append(job)
        self.logger.info('Submitted jobs: {0}'.format([job.id for job in jobs]))

        # montitor the qsub jobs until they are all completed
        if qsub_wait:
            self.logger.debug('Jobs will be monitored for completion and validated')
            self.job_management.monitor_validate_jobs(jobs = jobs)
            return(None)
        else:
            return(jobs)
