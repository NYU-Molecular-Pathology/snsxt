#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re
import task_classes
from task_classes import QsubAnalysisTask

class DemoQsubAnalysisTask(QsubAnalysisTask):
    """
    Demo task that will submit a single qsub job for the analysis
    """
    def __init__(self, analysis, taskname = 'DemoQsubAnalysisTask', config_file = 'DemoQsubAnalysisTask.yml', extra_handlers = None):
        """
        Parameters
        ----------
        analysis: SnsWESAnalysisOutput
            the `sns` pipeline output object to run the task on. If ``None`` is passed, ``self.analysis`` is retrieved instead.
        extra_handlers: list
            a list of extra Filehandlers to use for logging
        """
        QsubAnalysisTask.__init__(self, taskname = taskname, config_file = config_file, analysis = analysis, extra_handlers = extra_handlers)

    def main(self, analysis):
        """
        Main function for performing the analysis task on the entire analysis
        Put your code for performing the analysis task on the entire analysis here

        Parameters
        ----------
        analysis: SnsWESAnalysisOutput
            the `sns` pipeline output object to run the task on. If ``None`` is passed, ``self.analysis`` is retrieved instead.

        Returns
        -------
        qsub.Job
            a single qsub job object

        """
        self.logger.debug('Put your code for doing the analysis task in this function')
        self.logger.debug('The global configs for all tasks will be in this dict: {0}'.format(self.main_configs))
        self.logger.debug('The configs loaded from the task YAML file will be in this dict: {0}'.format(self.task_configs))

        self.logger.debug('Analysis is: {0}'.format(analysis.id))

        # output file
        output_foo = self.get_analysis_file_outpath(file_basename = 'foo.txt')
        output_bar = self.get_analysis_file_outpath(file_basename = 'bar.txt')

        self.logger.debug('output_foo is: {0}'.format(output_foo))
        self.logger.debug('output_bar is: {0}'.format(output_bar))

        # get the dir for the qsub logs
        # qsub_log_dir = analysis.list_none(analysis.get_dirs('logs-qsub'))
        qsub_log_dir = self.qsub_log_dir
        self.logger.debug('qsub_log_dir is {0}:'.format(qsub_log_dir))

        # make the shell command to run
        command = 'touch "{0}"; touch "{1}"; sleep 10'.format(output_foo, output_bar)
        self.logger.debug('command will be:\n{0}'.format(command))

        # submit the command as a qsub job on the HPC
        job = self.qsub.submit(command = command, name = self.taskname + '.' + analysis.id, stdout_log_dir = qsub_log_dir, stderr_log_dir = qsub_log_dir, verbose = True, sleeps = 1)

        return(job)
