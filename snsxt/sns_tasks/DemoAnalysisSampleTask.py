#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from task_classes import AnalysisSampleTask

class DemoAnalysisSampleTask(AnalysisSampleTask):
    """
    Demo task that will run a task for the whole analysis and perform actions for each sample
    """
    def __init__(self, analysis, taskname = 'DemoAnalysisSampleTask', config_file = 'DemoAnalysisSampleTask.yml', extra_handlers = None):
        """
        Parameters
        ----------
        analysis: SnsWESAnalysisOutput
            the `sns` pipeline output object to run the task on. If ``None`` is passed, ``self.analysis`` is retrieved instead.
        extra_handlers: list
            a list of extra Filehandlers to use for logging
        """
        AnalysisSampleTask.__init__(self, taskname = taskname, config_file = config_file, analysis = analysis, extra_handlers = extra_handlers)

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
        # get all the Sample objects for the analysis
        samples = analysis.get_samples()

        # list to hold the input files
        input_bams = []
        output_files = []

        for sample in samples:
            sampleID = sample.id
            input_bam = self.get_sample_file_inputpath(sampleID = sampleID, suffix = self.input_suffix)
            output_file = self.get_sample_file_outpath(sampleID = sampleID, suffix = '.txt')
            input_bams.append(input_bam)
            output_files.append(output_file)

        self.logger.debug('samples is: {0}'.format(samples))
        self.logger.debug('input_bams is: {0}'.format(input_bams))
        self.logger.debug('output_files is: {0}'.format(output_files))


        for output_file in output_files:
            self.logger.debug('creating output_file: {0}'.format(output_file))
            with open(output_file, 'w') as f:
                pass


        return()
