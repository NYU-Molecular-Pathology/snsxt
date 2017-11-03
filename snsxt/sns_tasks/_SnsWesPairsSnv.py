#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re
import task_classes
from task_classes import SnsTask

class SnsWesPairsSnv(SnsTask):
    '''
    Run the sns wes-pairs paired tumor-normal variant calling pipeline
    '''
    def __init__(self, analysis_dir, pairs_sheet = None, taskname = 'SnsWesPairsSnv', extra_handlers = None, **kwargs):
        '''
        '''
        SnsTask.__init__(self, analysis_dir = analysis_dir, taskname = taskname,  extra_handlers = extra_handlers)
        if not pairs_sheet:
            raise self._exceptions.AnalysisFileMissing(message = 'Samples pairs was not passed to task {0}'.format(self), errors = '')

    def run(self, *args, **kwargs):
        '''
        '''
        command = 'sns/run wes-pairs-snv'
        # run_cmd = self.run_sns_command(command = command)
        # jobs = self.catch_sns_jobs(proc_stdout = run_cmd.proc_stdout)
        # return(jobs)
        self.logger.debug(command)
        return()
