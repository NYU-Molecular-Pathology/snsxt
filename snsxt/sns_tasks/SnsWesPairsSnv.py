#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re
import shutil
import task_classes
from task_classes import SnsTask
from time import sleep

class SnsWesPairsSnv(SnsTask):
    """
    Run the sns wes-pairs paired tumor-normal variant calling pipeline
    """
    def __init__(self, analysis_dir, pairs_sheet = None, taskname = 'SnsWesPairsSnv', config_file = 'SnsWesPairsSnv.yml', extra_handlers = None, **kwargs):
        """
        """
        SnsTask.__init__(self, analysis_dir = analysis_dir, taskname = taskname,  extra_handlers = extra_handlers, config_file = config_file)
        # make sure the samples pairs sheet was passed
        if not pairs_sheet:
            raise self._exceptions.AnalysisFileMissing(message = 'Samples pairs was not passed to task {0}'.format(self), errors = '')
        # copy the sample pairs sheet to the proper location
        pairs_sheet_output = self.get_analysis_file_outpath(file_basename = "samples.pairs.csv")
        self.logger.debug('Copying samples pairs sheet from\n{0}\nto\n{1}'.format(pairs_sheet, pairs_sheet_output))
        shutil.copy2(pairs_sheet, pairs_sheet_output)

    def run(self, *args, **kwargs):
        """
        """
        expected_log_dir = os.path.join(self.analysis_dir, "logs-qsub")
        command = 'sns/run wes-pairs-snv'
        run_cmd = self.run_sns_command(command = command)
        jobs = self.catch_sns_jobs(proc_stdout = run_cmd.proc_stdout, log_dir = expected_log_dir)

        # wait a few seconds to allow time for jobs to initialize
        sleep(10)
        return(jobs)
