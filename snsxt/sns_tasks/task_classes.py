#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Updates global configs with task dir paths, then imports the base classes for snsxt analysis tasks used throughout the program
"""
import os
import sys

# ~~~~ LOAD MORE PACKAGES ~~~~~~ #
# add parent dir to sys.path to import config
scriptdir = os.path.dirname(os.path.realpath(__file__)) # this script's dir
parentdir = os.path.dirname(scriptdir) # this script's parent dir
sys.path.insert(0, parentdir)
import config
sys.path.pop(0)

# ~~~~ SETUP GLOBAL CONFIGS ~~~~~~ #
# update program-wide config with extra items from this script
config.config['sns_tasks_dir'] = scriptdir # this dir; /ifs/data/molecpathlab/scripts/snsxt/snsxt/sns_tasks

# path to the `scripts` directory relative to the `sns_tasks` dir
# dont change this!
config.config['tasks_scripts_dir'] = os.path.join(config.config['sns_tasks_dir'], config.config['tasks_scripts_dir'])
# ^ i.e. same as sns_tasks/scripts

# path to the `reports` directory relative to the `sns_tasks` dir
# dont change this!
config.config['tasks_reports_dir'] = os.path.join(config.config['sns_tasks_dir'], config.config['tasks_reports_dir'])
# ^ i.e. same as sns_tasks/reports

# path to the `reports` directory relative to the `sns_tasks` dir
# dont change this!
config.config['tasks_config_dir'] = os.path.join(config.config['sns_tasks_dir'], config.config['tasks_config_dir'])
# ^ i.e. same as sns_tasks/config

# path to the `files` directory relative to the `sns_tasks` dir
# dont change this!
config.config['tasks_files_dir'] = os.path.join(config.config['sns_tasks_dir'], config.config['tasks_files_dir'])
# ^ i.e. same as sns_tasks/files

# path to the sns repo to use for sns_tasks that use sns itself
# tasks_sns_repo_dir
# TODO: add this path

# ~~~~ LOAD BASE CLASSES ~~~~~~ #
from AnalysisTask import AnalysisTask
from AnalysisTask import AnnotationInplace
from AnalysisSampleTask import AnalysisSampleTask
from QsubSampleTask import QsubSampleTask
from QsubAnalysisTask import QsubAnalysisTask
from SnsTask import SnsTask

# ~~~~~ DECORATORS ~~~~~ #
def _setup_report(func, *args, **kwargs):
    """
    Decorator to set up the analysis task's report files
    """
    def report_wrapper(self, *args, **kwargs) :
        """
        Wrap another class method
        """
        self.logger.debug('Setting up the report files for the task')
        self.setup_report()
        func(self, *args, **kwargs)
    return(report_wrapper)
