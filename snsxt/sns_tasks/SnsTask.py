#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module for the base SnsTask object class
"""
import os
from AnalysisTask import AnalysisTask

class SnsTask(AnalysisTask):
    """
    Class for a task that runs part of the sns pipeline on the analysis
    and operates on the entires sns analysis

    get the AnalysisTask methods but do not initialize its locations

    note: do not use methods that call self.analysis, such as get_expected_output_files

    TODO: finish this
    """
    def __init__(self, taskname, analysis_dir = None, config_file = None, extra_handlers = None):
        """
        """
        AnalysisTask.__init__(self, taskname = str(taskname), config_file = config_file, analysis = None, extra_handlers = extra_handlers)

        if analysis_dir:
            self.analysis_dir = analysis_dir
            self._init_locs()

        if config_file:
            # get the 'task_configs' from external YAML file, load them in self.task_configs
            self._task_config_from_file(config_file = config_file) #

    def _init_locs(self):
        """
        Initialize output locations
        """
        self.output_dir = self.tools.mkdirs(path = os.path.realpath(self.analysis_dir), return_path = True)
        # internal sns repo
        self.sns_repo_dir = self.main_configs['sns_repo_dir']


    def get_expected_output_files(self, analysis_dir = None):
        """
        Return a list of all the expected output files for all of the samples in the analysis

        get expected files from the main configs
        """
        if not analysis_dir:
            analysis_dir = getattr(self, 'analysis_dir', None)

        expected_output = []

        for output_file in self.main_configs['analysis_output_index']['_parent']['file-names']:
            path = self.get_analysis_file_outpath(file_basename = output_file)
            expected_output.append(path)

        if len(expected_output) < 1:
            self.logger.warning('output files were not set for sns analysis task {0}'.format(self.taskname))

        return(expected_output)

    def run_sns_command(self, command = None):
        """
        Run a command in the context of an sns directory
        """
        output_dir = self.output_dir
        with self.tools.DirHop(output_dir) as d:
            run_cmd = self.tools.SubprocessCmd(command = command).run()
            self.logger.debug(run_cmd.proc_stdout)
            self.logger.debug(run_cmd.proc_stderr)
        return(run_cmd)

    def catch_sns_jobs(self, proc_stdout):
        """
        Capture the job ID's of all qsub jobs submitted by an sns command
        by parsing its stdout
        return a list of jobs
        """
        jobs = []
        for job in [self.qsub.Job(id = job_id, name = job_name)
                    for job_id, job_name
                    in self.qsub.find_all_job_id_names(text = proc_stdout)]:
            jobs.append(job)
        self.logger.debug('Captured qsub jobs from sns pipeline output:\n{0}'.format([(job.id, job.name) for job in jobs]))
        return(jobs)
