#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re
import task_classes
import shutil
from task_classes import SnsTask

class StartSns(SnsTask):
    '''
    Setup a new sns analysis
    '''
    def __init__(self, analysis_dir, targets_bed = None, fastq_dirs = None, taskname = 'StartSns', extra_handlers = None, **kwargs):
        '''
        '''
        SnsTask.__init__(self, analysis_dir = analysis_dir, taskname = taskname, extra_handlers = extra_handlers)
        if not fastq_dirs:
            raise self._exceptions.AnalysisFileMissing(message = 'Fastq directories were not passed to task {0}'.format(self), errors = '')
        if not targets_bed:
            raise self._exceptions.AnalysisFileMissing(message = 'Targets .bed file was not passed to task {0}'.format(self), errors = '')

        # fastq directories to be used
        self.fastq_dirs = []
        for fastq_dir in fastq_dirs:
            self.fastq_dirs.append(os.path.realpath(fastq_dir))

        # path to the input targets files
        self.targets_bed = targets_bed

        # list of items to validate before proceeding
        setup_items = []
        for item in self.fastq_dirs:
            setup_items.append(item)
        setup_items.append(self.targets_bed)
        setup_items.append(self.output_dir)
        self.validate_items(items = setup_items)

    def setup_sns_analysis_dir(self):
        '''
        Copy the base files over to start the sns analysis
        '''
        # copy sns repo over from the internal one
        output_sns_repo = os.path.join(self.output_dir, os.path.basename(self.sns_repo_dir))
        self.logger.debug('sns repo will be copied from\n{0}\nto\n{0}'.format(self.sns_repo_dir, output_sns_repo))
        self.tools.copy_and_overwrite(from_path = self.sns_repo_dir, to_path = output_sns_repo)

        # copy over the targets .bed file
        output_targets = os.path.join(self.output_dir, os.path.basename(self.targets_bed))
        self.logger.debug('targest .bed file will be copied from\n{0}\nto\n{0}'.format(self.targets_bed, output_targets))
        shutil.copy2(self.targets_bed, output_targets)


    def run(self, *args, **kwargs):
        '''
        Main function for performing the analysis task on the entire analysis
        Put your code for performing the analysis task on the entire analysis here

        analysis is an SnsWESAnalysisOutput object
        '''
        self.setup_sns_analysis_dir()
        fastq_gather_commands = '\n'.join(['sns/gather-fastqs {0}'.format(d) for d in self.fastq_dirs])
        command = '''
{0}
{1}
        '''.format(
        fastq_gather_commands, # 0
        'sns/generate-settings hg19'  # 1
        )
        # self.logger.debug('command is:\n{0}'.format(command))
        run_cmd = self.run_sns_command(command = command)
        jobs = self.catch_sns_jobs(proc_stdout = run_cmd.proc_stdout)
        return(jobs)
