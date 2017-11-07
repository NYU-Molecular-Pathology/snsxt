#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re
from task_classes import AnalysisTask

class SummaryAvgCoverage(AnalysisTask):
    """
    Class for creating summaries of the average coverages for the analysis from GATK DepthOfCoverage output
    Run this from an external R script in the current session
    """
    def __init__(self, analysis, taskname = 'Summary_Avg_Coverage', config_file = 'Summary_Avg_Coverage.yml', extra_handlers = None):
        """
        """
        AnalysisTask.__init__(self, taskname = taskname, config_file = config_file, analysis = analysis, extra_handlers = extra_handlers)
        self.task_configs['run_script_path'] = os.path.join(self.main_configs['tasks_scripts_dir'], self.task_configs['run_script'])
        # /ifs/data/molecpathlab/scripts/snsxt/snsxt/sns_tasks/scripts/calculate_average_coverages.R

    def make_run_script_cmd(self, input_dir, output_dir, run_script):
        """
        Make the shell command to run the run_script
        """
        command = """
    {0} -d {1} -o {2}
    """.format(
    run_script, # 0
    input_dir, # 1
    output_dir # 2
    )
        return(command)

    def main(self, analysis):
        """
        Main control function for the program
        Creates summary coverage files for all samples in the analysis
        """
        self.logger.debug('Analysis is: {0}'.format(analysis))
        # logger.debug(sample.static_files)
        self.log.print_filehandler_filepaths_to_log(logger = self.logger)

        # shell command to run
        command = self.make_run_script_cmd(input_dir = self.input_dir, output_dir = self.output_dir, run_script = self.task_configs['run_script_path'])
        self.logger.debug(command)

        # need to change cwd for R commands to source the external tools file
        with self.tools.DirHop(os.path.dirname(self.task_configs['run_script_path'])) as d:
            run_cmd = self.tools.SubprocessCmd(command = command).run()
            self.logger.debug(run_cmd.proc_stderr)

        # reset the list of extra file handlers to pass to the annotation function
        extra_handlers = [h for h in self.log.get_all_handlers(self.logger)]

        # Annotation_inplace(input_dir = output_dir, annotation_method = configs['annotation_method'], extra_handlers = extra_handlers)
        self.annotate(input_dir = self.output_dir, extra_handlers = extra_handlers)
