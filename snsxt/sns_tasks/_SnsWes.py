#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re
import task_classes
from task_classes import SnsTask

class SnsWes(SnsTask):
    '''
    Run the sns wes analysis pipeline
    '''
    def __init__(self, analysis_dir, taskname = 'SnsWes', extra_handlers = None, **kwargs):
        '''
        '''
        SnsTask.__init__(self, analysis_dir = analysis_dir, taskname = taskname, extra_handlers = extra_handlers)

    def run(self, *args, **kwargs):
        '''
        '''
        command = 'sns/run wes'
        # run_cmd = self.run_sns_command(command = command)
        # jobs = self.catch_sns_jobs(proc_stdout = run_cmd.proc_stdout)
        # return(jobs)
        self.logger.debug(command)
        return()
