#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module for the base SnsTask object class
"""
import os
from AnalysisTask import AnalysisTask

class SnsTask(AnalysisTask):
    """
    Base class for a task that runs the ``sns`` pipeline. A wrapper for running the ``sns`` pipeline in the context of ``snsxt``.

    Notes
    -----
    The ``run()`` method for this class should be overriden by the end-user's custom ``run()`` method, per task. See other included ``SnsTask`` classes for examples.
    """
    def __init__(self, taskname, analysis_dir = None, config_file = None, extra_handlers = None):
        """
        Parameters
        ----------
        taskname: str
            the name of the task
        analysis_dir: str
            path to the directory to use for ``sns`` pipeline output
        config_file: str
            basename of the YAML formatted config file in the ``tasks_config_dir`` to use for ``task_configs``
        extra_handlers: list
            a list of extra Filehandlers to use for logging

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
        Initializes directory location attributes for the task
        """
        self.output_dir = self.tools.mkdirs(path = os.path.realpath(self.analysis_dir), return_path = True)
        # internal sns repo
        self.sns_repo_dir = self.main_configs['sns_repo_dir']


    def run_sns_command(self, command = None):
        """
        Runs a command in the context of an sns directory, e.g. to run the ``sns`` pipeline program itself. This method will change the current working directory to the location of the ``analysis_dir`` before executing the ``command`` given.

        Parameters
        ----------
        command: str
            the command to run

        Returns
        -------
        tools.SubprocessCmd
            the ``tools.SubprocessCmd`` object representing the command that was run
        """
        output_dir = self.output_dir
        with self.tools.DirHop(output_dir) as d:
            run_cmd = self.tools.SubprocessCmd(command = command).run()
            self.logger.debug(run_cmd.proc_stdout)
            self.logger.debug(run_cmd.proc_stderr)
        return(run_cmd)

    def catch_sns_jobs(self, proc_stdout, log_dir = None):
        """
        Parses the stdout message for entries that correspond to qsub jobs that were submitted
        Capture the job ID's of all qsub jobs submitted by an sns command
        by parsing its stdout
        return a list of jobs

        Parameters
        ----------
        proc_stdout: str
            the stdout message from a ``tools.SubprocessCmd`` command that was run

        Returns
        -------
        list
            a list of ``qsub.Job`` objects representing qsub jobs that were submitted
        """
        jobs = []
        for job in [self.qsub.Job(id = job_id, name = job_name, log_dir = log_dir)
                    for job_id, job_name
                    in self.qsub.find_all_job_id_names(text = proc_stdout)]:
            jobs.append(job)
        self.logger.debug('Captured qsub jobs from sns pipeline output:\n{0}'.format([(job.id, job.name) for job in jobs]))
        return(jobs)
