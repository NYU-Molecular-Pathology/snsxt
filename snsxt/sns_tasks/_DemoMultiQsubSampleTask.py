#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re
import task_classes
from task_classes import MultiQsubSampleTask

class DemoMultiQsubSampleTask(MultiQsubSampleTask):
    """
    Demo task that will submit multiple qsub jobs for every sample in the analysis

    This is a template for an analysis task that operates a single sample in the analysis at a time
    Put your description of the analysis task here
    """
    def __init__(self, analysis, taskname = 'DemoMultiQsubSampleTask', config_file = 'DemoMultiQsubSampleTask.yml', extra_handlers = None):
        """
        Parameters
        ----------
        analysis: SnsWESAnalysisOutput
            the `sns` pipeline output object to run the task on. If ``None`` is passed, ``self.analysis`` is retrieved instead.
        extra_handlers: list
            a list of extra Filehandlers to use for logging
        """
        MultiQsubSampleTask.__init__(self, taskname = taskname, config_file = config_file, analysis = analysis, extra_handlers = extra_handlers)

    def main(self, sample):
        """
        Put your code for performing the analysis task on a single sample here

        Parameters
        ----------
        sample: SnsAnalysisSample
            a single sample from the analysis

        Returns
        -------
        qsub.Job
            a single qsub job object
        """
        self.logger.debug('Put your code for doing the analysis task in this function')
        self.logger.debug('The global configs for all tasks will be in this dict: {0}'.format(self.main_configs))
        self.logger.debug('The configs loaded from the task YAML file will be in this dict: {0}'.format(self.task_configs))

        self.logger.debug('Sample is: {0}'.format(sample.id))

        # get the dir for the qsub logs
        qsub_log_dir = sample.list_none(sample.analysis_config['dirs']['logs-qsub'])
        self.logger.debug('qsub_log_dir is: {0}'.format(qsub_log_dir))

        # get the path to the sample's .bam file
        sample_bam = self.get_sample_file_inputpath(sampleID = sample.id, suffix = self.input_suffix)
        self.logger.debug('sample_bam is: {0}'.format(sample_bam))

        # make the shell command to run
        job_name = self.taskname + '.' + sample.id
        command = 'sleep 30'
        job1 = self.qsub.submit(command = command, name = "one" + job_name, stdout_log_dir = qsub_log_dir, stderr_log_dir = qsub_log_dir, verbose = True, sleeps = 1)
        job2 = self.qsub.submit(command = command, name = "two" + job_name, stdout_log_dir = qsub_log_dir, stderr_log_dir = qsub_log_dir, verbose = True, sleeps = 1)
        return([job1, job2])
