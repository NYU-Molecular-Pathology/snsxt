#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from task_classes import SnsTask
from time import sleep

class SnsRnaStar(SnsTask):
    """
    Run the sns rna-star analysis pipeline
    """
    def __init__(self, analysis_dir, taskname = 'SnsRnaStar', extra_handlers = None, **kwargs):
        """
        """
        SnsTask.__init__(self, analysis_dir = analysis_dir, taskname = taskname, extra_handlers = extra_handlers)

    def run(self, *args, **kwargs):
        """
        """
        expected_log_dir = os.path.join(self.analysis_dir, "logs-qsub")
        command = 'sns/run rna-star'
        run_cmd = self.run_sns_command(command = command)
        jobs = self.catch_sns_jobs(proc_stdout = run_cmd.proc_stdout, log_dir = expected_log_dir)

        # wait a few seconds to allow time for jobs to initialize
        sleep(10)
        return(jobs)
