#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re
import shutil
from task_classes import SnsTask
from time import sleep

class SnsSetupPairs(SnsTask):
    """
    Copies over the tumor-normal ``pairs_sheet`` passed by the user in the program's args, overwriting the default "samples.pairs.csv" file produced by the ``sns wes`` pipeline which contains no comparisons. Need this so that we can prepare for tumor-normal analysis without having run an ``sns`` paired analysis step.
    """
    def __init__(self, analysis_dir, pairs_sheet = None, taskname = 'SnsSetupPairs', config_file = 'SnsSetupPairs.yml', extra_handlers = None, **kwargs):
        """
        """
        SnsTask.__init__(self, analysis_dir = analysis_dir, taskname = taskname,  extra_handlers = extra_handlers, config_file = config_file)
        # make sure the samples pairs sheet was passed
        if not pairs_sheet:
            raise self._exceptions.AnalysisFileMissing(message = 'Samples pairs was not passed to task {0}'.format(self), errors = '')

        # the basename of the file to create
        pairs_sheet_basename = self.task_configs['pairs_sheet_basename'] # "samples.pairs.csv"

        # path to expected/required output file
        pairs_sheet_output = self.get_analysis_file_outpath(file_basename = pairs_sheet_basename)

        # make sure it doesn't exist already
        self.tools.backup_file(input_file = pairs_sheet_output, use_logger = self.logger)

        # copy the sample pairs sheet to the proper location
        self.logger.debug('Copying samples pairs sheet from\n{0}\nto\n{1}'.format(pairs_sheet, pairs_sheet_output))
        shutil.copy2(pairs_sheet, pairs_sheet_output)

        # make sure it really worked
        self.validate_items([pairs_sheet_output])

    def run(self, *args, **kwargs):
        """
        Placeholder to run the task; this task's actions take place in '__init__' since they deal with the files passed to the task upon initialization
        """
        # return an empty list since there are no jobs
        return([])
