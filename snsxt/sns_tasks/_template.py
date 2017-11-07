#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re
from task_classes import QsubSampleTask
from task_classes import QsubAnalysisTask

class TemplateAnalysisTask(QsubAnalysisTask):
    """
    This is a template for an analysis task that operates on the entire analysis at once
    Put your description of the analysis task here
    """
    def __init__(self, analysis, taskname = 'Template_Analysis_Task', config_file = 'Template_Analysis_Task.yml', extra_handlers = None):
        """
        Initialize the object with the parent class

        analysis is an SnsWESAnalysisOutput object
        """
        QsubAnalysisTask.__init__(self, taskname = taskname, config_file = config_file, analysis = analysis, extra_handlers = extra_handlers)

    def main(self, analysis):
        """
        Main function for performing the analysis task
        Put your code for performing the analysis task in here
        analysis is an SnsWESAnalysisOutput object
        """
        self.logger.debug('Put your code for doing the analysis task in this function')
        self.logger.debug('The global configs for all tasks will be in this dict: {0}'.format(self.main_configs))
        self.logger.debug('The configs loaded from the task YAML file will be in this dict: {0}'.format(self.task_configs))



class TemplateAnalysisSampleTask(QsubSampleTask):
    """
    This is a template for an analysis task that operates a single sample in the analysis at a time
    Put your description of the analysis task here
    """
    def __init__(self, analysis, taskname = 'Template_Analysis_Sample_Task', config_file = 'Template_Analysis_Sample_Task.yml', extra_handlers = None):
        """
        Initialize the object with the parent class

        analysis is an SnsWESAnalysisOutput object
        """
        QsubSampleTask.__init__(self, taskname = taskname, config_file = config_file, analysis = analysis, extra_handlers = extra_handlers)

    def main(self, sample):
        """
        Main function for performing the analysis task on a single sample here
        Put your code for performing the analysis task in here on a single sample here

        sample is an SnsAnalysisSample object
        """
        self.logger.debug('Put your code for doing the analysis task in this function')
        self.logger.debug('The global configs for all tasks will be in this dict: {0}'.format(self.main_configs))
        self.logger.debug('The configs loaded from the task YAML file will be in this dict: {0}'.format(self.task_configs))
