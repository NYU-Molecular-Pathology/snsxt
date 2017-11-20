#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module for the base QsubAnalysisTask object class
"""
from AnalysisTask import AnalysisTask

class QsubAnalysisTask(AnalysisTask):
    """
    Base class for an ``AnalysisTask`` that operates on the entire analysis, and submits a single qsub job

    Notes
    -----
    This class should have a ``main`` method that returns a single ``qsub.Job`` object
    """
    def __init__(self, *ars, **kwargs):
        AnalysisTask.__init__(self, *ars, **kwargs)

    def run(self, analysis = None, qsub_wait = True, *args, **kwargs):
        """
        Runs a task that operates an entire analysis output, and submits a single qsub job

        Parameters
        ----------
        analysis: SnsWESAnalysisOutput
            the `sns` pipeline output object to run the task on. If ``None`` is passed, ``self.analysis`` is retrieved instead.
        qsub_wait: bool
            whether the task should wait for the qsub job to finish before continuing; default is ``True``
        args: list
            a list of extra positional arguments to pass to ``self.main()``
        kwargs: dict
            a dictionary of extra positional arguments to pass to ``self.main()``

        Returns
        -------
        list or None
            a list of ``qsub.Job`` objects if ``qsub_wait`` is ``False``, otherwise returns ``None`` after waiting for all jobs to finish

        Notes
        -----
        If ``qsub_wait`` is ``True``, then qsub jobs will also be validated for completion status.
        """
        if not analysis:
            analysis = getattr(self, 'analysis', None)
        # empty list to hold the qsub jobs
        jobs = []
        # run the task on the analysis; should return a qsub Job object
        job = self.main(analysis = analysis, *args, **kwargs)
        if job:
            jobs.append(job)
            self.logger.debug('Submitted jobs: {0}'.format([job.id for job in jobs]))

        if qsub_wait:
            # montitor the qsub jobs until they are all completed
            self.logger.debug('Jobs will be monitored for completion and validated')
            self.job_management.monitor_validate_jobs(jobs = jobs)
            return(None)
        else:
            return(jobs)
