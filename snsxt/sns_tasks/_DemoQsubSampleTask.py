#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re
import task_classes
from task_classes import QsubSampleTask

class DemoQsubSampleTask(QsubSampleTask):
    '''
    Demo task that will submit a qsub job for every sample in the analysis

    This is a template for an analysis task that operates a single sample in the analysis at a time
    Put your description of the analysis task here
    '''
    def __init__(self, analysis, taskname = 'DemoQsubSampleTask', config_file = 'DemoQsubSampleTask.yml', extra_handlers = None):
        '''
        analysis is an SnsWESAnalysisOutput object
        '''
        QsubSampleTask.__init__(self, taskname = taskname, config_file = config_file, analysis = analysis, extra_handlers = extra_handlers)

    def main(self, sample):
        '''
        Main function for performing the analysis task on a single sample here
        Put your code for performing the analysis task in here on a single sample here

        sample is an SnsAnalysisSample object
        '''
        self.logger.debug('Put your code for doing the analysis task in this function')
        self.logger.debug('The global configs for all tasks will be in this dict: {0}'.format(self.main_configs))
        self.logger.debug('The configs loaded from the task YAML file will be in this dict: {0}'.format(self.task_configs))

        self.logger.debug('Sample is: {0}'.format(sample.id))

        # input file
        sample_bam = self.get_sample_file_inputpath(sampleID = sample.id, suffix = self.input_suffix)

        # output file
        sample_output = self.create_sample_file_outpath(sampleID = sample.id, suffix = self.output_suffix)

        self.logger.debug('sample_bam is: {0}'.format(sample_bam))
        self.logger.debug('sample output file will be: {0}'.format(sample_output))

        # get the dir for the qsub logs
        qsub_log_dir = sample.list_none(sample.analysis_config['dirs']['logs-qsub'])

        # make the shell command to run
        command = 'touch "{0}"; sleep 20'.format(sample_output)
        self.logger.debug('command will be:\n{}'.format(command))

        # submit the command as a qsub job on the HPC
        job = self.qsub.submit(command = command, name = self.taskname + '.' + sample.id, stdout_log_dir = qsub_log_dir, stderr_log_dir = qsub_log_dir, verbose = True, sleeps = 1)

        return(job)
