#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A demo custom SnsTask
"""
from task_classes import SnsTask

class DemoSnsTask(SnsTask):
    """
    Run the sns wes analysis pipeline for unpaired variant calling on exome data
    """
    def __init__(self, analysis_dir, taskname = 'DemoSnsTask', extra_handlers = None, **kwargs):
        """
        """
        SnsTask.__init__(self, analysis_dir = analysis_dir, taskname = taskname, extra_handlers = extra_handlers)

    def run(self, *args, **kwargs):
        """
        """
        command = '''
        echo ""
        echo "this is the demo sns task, pwd is:"
        echo $PWD
        ls -l
        echo ""
        '''
        run_cmd = self.run_sns_command(command = command)
        self.logger.debug(run_cmd.proc_stdout)
        return()
