#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Base classes for snsxt analysis tasks
'''
import os
import sys
import re
import functools

# add parent dir to sys.path to import util
scriptdir = os.path.dirname(os.path.realpath(__file__)) # this script's dir
parentdir = os.path.dirname(scriptdir) # this script's parent dir
sys.path.insert(0, parentdir)
import util
from util import find
from util import tools
from util import log
from util import qsub
from util.classes import LoggedObject
sys.path.pop(0)

# ~~~~ LOAD MORE PACKAGES ~~~~~~ #
import csv
import yaml
import shutil


# ~~~~ SETUP GLOBAL CONFIGS ~~~~~~ #
# configs that should be available to all analysis tasks
configs = {}

# from this script
configs['sns_tasks_dir'] = scriptdir # this dir; /ifs/data/molecpathlab/scripts/snsxt/snsxt/sns_tasks

# path to the `scripts` directory relative to the `sns_tasks` dir
# dont change this!
configs['tasks_scripts_dir'] = os.path.join(configs['sns_tasks_dir'], 'scripts')
# ^ i.e. same as sns_tasks/scripts

# path to the `reports` directory relative to the `sns_tasks` dir
# dont change this!
configs['tasks_reports_dir'] = os.path.join(configs['sns_tasks_dir'], 'reports')
# ^ i.e. same as sns_tasks/reports

# path to the `reports` directory relative to the `sns_tasks` dir
# dont change this!
configs['tasks_config_dir'] = os.path.join(configs['sns_tasks_dir'], 'config')
# ^ i.e. same as sns_tasks/config

# path to the `files` directory relative to the `sns_tasks` dir
# dont change this!
configs['tasks_files_dir'] = os.path.join(configs['sns_tasks_dir'], 'files')
# ^ i.e. same as sns_tasks/files


# ~~~~~ DECORATORS ~~~~~ #
def _setup_report(func, *args, **kwargs):
    '''
    Decorator to set up the analysis task's report files
    '''
    def report_wrapper(self, *args, **kwargs) :
        '''
        Wrap another class method
        '''
        self.logger.debug('Setting up the report files for the task')
        self.setup_report()
        func(self, *args, **kwargs)
    return(report_wrapper)


# ~~~~~ CLASSES ~~~~~ #
class AnalysisTask(LoggedObject):
    '''
    Base class for an sns analysis task

    from task_classes import AnalysisTask
    x = AnalysisTask(taskname = 'Delly2', config_file = 'Delly2.yml')
    '''
    def __init__(self, taskname, config_file, analysis = None, extra_handlers = None):
        '''
        Initialize the object
        taskname = name of this task
        analysis = SnsWESAnalysisOutput object
        '''
        LoggedObject.__init__(self, id = taskname, extra_handlers = extra_handlers)
        self.taskname = str(taskname)
        self.analysis = analysis

        # attach modules so they are easier to access in derived classes
        self.util = util
        self.tools = tools
        self.qsub = qsub
        self.log = log
        self.find = find

        # get the 'main_configs' from this script
        self.main_configs = configs

        if config_file:
            # get the 'task_configs' from external YAML file, load them in self.task_configs
            self._task_config_from_file(config_file = config_file) #
            # set some extra attributes for convenience
            self._init_task_attrs()

        if analysis:
            # setup the input and output locations
            self._init_locs()
            # setup the report
            self.setup_report()

    def _init_task_attrs(self):
        '''
        Initialize some extra object attributes from the task config, if they're present

        These are convenience items for easy access in child classes
        '''
        if self.task_configs.get('input_pattern', None):
            self.input_pattern = self.task_configs['input_pattern']

        if self.task_configs.get('input_suffix', None):
            self.input_suffix = self.task_configs['input_suffix']

        if self.task_configs.get('output_pattern', None):
            self.output_pattern = self.task_configs['output_pattern']

        if self.task_configs.get('output_suffix', None):
            self.output_suffix = self.task_configs['output_suffix']


    def _init_locs(self):
        '''
        Initialize locations for the task
        '''
        self.output_dir = self.tools.mkdirs(path = os.path.join(self.analysis.dir, self.task_configs['output_dir_name']), return_path = True)
        self.logger.debug('task output_dir: {0}'.format(self.output_dir))
        self.input_dir = os.path.join(self.analysis.dir, self.task_configs['input_dir'])
        self.validate_items([self.output_dir, self.input_dir])

    def _task_config_from_file(self, config_file):
        '''
        Load a YAML formatted file and add it to the object's configs
        config_file = basename of a file in the tasks_config_dir, for convenience
        '''
        config_filepath = os.path.join(self.main_configs['tasks_config_dir'], config_file)
        self.validate_items([config_filepath])
        with open(config_filepath, "r") as f:
            self.task_configs = yaml.load(f)
            self.task_configs['config_file'] = config_filepath

    def create_sample_file_outpath(self, sampleID, suffix = None):
        '''
        Create a path to a file in the analysis output directory
        '''
        # try to resolve an output_suffix
        if not suffix:
            suffix = self.output_suffix
        output_path = os.path.join(self.output_dir, sampleID + suffix)
        return(output_path)

    def get_sample_file_inputpath(self, sampleID, suffix = None, validate = True):
        '''
        Create the path to an expected sample file in the input directory
        '''
        # try to resolve an input_suffix
        if not suffix:
            suffix = self.input_suffix
        path = os.path.join(self.input_dir, sampleID + suffix)
        if validate:
            self.logger.debug('Validating expected input file path: {0}'.format(path))
            self.validate_items([path])
        return(path)

    def validate_items(self, items):
        '''
        Run validations on a list of items
        items = list of file or dir paths

        TODO: raise custom exceptions here if files dont validate
        '''
        if len(items) < 1 or not items:
            self.logger.error('No items were passed')
            sys.exit()
        # make sure all files and dirs exist
        items_exist = {item: self.tools.item_exists(item) for item in items}
        if not all(items_exist.values()):
            self.logger.error('Some items did not exist:')
            self.logger.error('{0}'.format(items_exist))
            sys.exit()
            # add more criteria here...
        # TODO: raise custom exceptions here if files dont validate

    def get_report_files(self):
        '''
        Get the files for the report based on the configs, return a list of files
        '''
        report_files = []

        report_dir = self.main_configs['tasks_reports_dir']
        if self.task_configs.get('report_files', None):
            for item in self.task_configs['report_files']:
                file_path = os.path.join(report_dir, item)
                report_files.append(file_path)
        else:
            self.logger.warning('No report files are set for analysis task {0}'.format(self.taskname))

        if report_files:
            self.validate_items(report_files)
        return(report_files)

    def setup_report(self, output_dir = None):
        '''
        Set up the report files output for the pipeline step
        by copying over every associated file for the report to the output dir
        '''
        # try to get an outputdir if it wasnt passed
        if not output_dir:
            output_dir = getattr(self, 'output_dir', None) # self.output_dir
        if output_dir:
            report_files = self.get_report_files()
            self.logger.debug("Report files are: {0}".format(report_files))
            # copy over the report files from the config
            for item in report_files:
                output_file = os.path.join(output_dir, os.path.basename(item))
                self.logger.debug("Copying report file '{0}' to '{1}' ".format(item, output_file))
                shutil.copy2(item, output_file)
            # copy over the config file itself as well if present
            if self.task_configs.get('config_file', None):
                output_file = os.path.join(output_dir, 'config.yml')
                self.logger.debug("Copying cofig file '{0}' to '{1}' ".format(self.task_configs['config_file'], output_file))
                shutil.copy2(self.task_configs['config_file'], output_file)
        else:
            self.logger.debug('No report files set for task')

    def annotate(self, input_dir = None, extra_handlers = None):
        '''
        Run the ANNOVAR in-place annotation on the analysis task;
        '''
        if not extra_handlers:
            extra_handlers = getattr(self, 'extra_handlers', None)
        # if not input_dir:
        #     input_dir = getattr(self, 'input_dir', None)
        # dont do this, input_dir might not be the right one!
        if input_dir:
            x = AnnotationInplace(extra_handlers = extra_handlers).annotate(input_dir = self.output_dir, annotation_method = 'ANNOVAR')
        else:
            self.logger.debug('No input_dir specified')
        return()


    def run_sample_task(self, analysis = None, *args, **kwargs):
        '''
        Run a task that operates on every sample in the analysis individually
        '''
        if not analysis:
            analysis = getattr(self, 'analysis', None)
        if analysis:
            # get all the Sample objects for the analysis
            samples = analysis.get_samples()
            for sample in samples:
                self.logger.debug('Running task {0} on sample {1}'.format(self.taskname, sample.id))
                self.main(sample = sample, *args, **kwargs)
        return()

    def run_analysis_task(self, analysis = None, *args, **kwargs):
        '''
        Run a task that operates an analysis (not per-sample)
        analysis is an SnsWESAnalysisOutput object
        '''
        if not analysis:
            analysis = getattr(self, 'analysis', None)
        if analysis:
            self.main(analysis = analysis, *args, **kwargs)
        return()

    def run_qsub_sample_task(self, analysis = None, qsub_wait = True, *args, **kwargs):
        '''
        Run a task that submits qsub jobs on all the samples in the analysis output
        analysis is an SnsWESAnalysisOutput object
        task is a module with a function 'main' that returns a qsub Job object
        qsub_wait = wait for all qsub jobs to complete
        '''
        if not analysis:
            analysis = getattr(self, 'analysis', None)

        # get all the Sample objects for the analysis
        samples = analysis.get_samples()

        # empty list to hold the qsub jobs
        jobs = []

        for sample in samples:
            # run the task on each sample; should return a qsub Job object
            job = self.main(sample = sample, *args, **kwargs)
            if job:
                jobs.append(job)
        self.logger.info('Submitted jobs: {0}'.format([job.id for job in jobs]))

        # montitor the qsub jobs until they are all completed
        if qsub_wait:
            self.logger.debug('Waiting for jobs to complete')
            self.qsub.monitor_jobs(jobs = jobs)
            if jobs:
                self.logger.debug('Validating completion status of jobs')
                job_validations = [job.validate_completion() for job in jobs]
                if all(job_validations):
                    self.logger.debug('All jobs appear to have completed successfully')
                else:
                    for job in jobs:
                        if not job.validate_completion():
                            self.logger.error('Job {0} did not complete successfully!'.format((job.id, job.name)))
            return(None)
        else:
            return(jobs)

    def run_qsub_analysis_task(self, analysis = None, qsub_wait = True, *args, **kwargs):
        '''
        Run a task that submits one qsub job for the analysis
        analysis is an SnsWESAnalysisOutput object
        task is a module with a function 'main' that returns a qsub Job object
        qsub_wait = wait for all qsub jobs to complete

        TODO: Update this with run_qsub_sample_task methods
        '''
        if not analysis:
            analysis = getattr(self, 'analysis', None)
        # empty list to hold the qsub jobs
        jobs = []
        # run the task on the analysis; should return a qsub Job object
        job = self.main(analysis = analysis, *args, **kwargs)
        if job:
            jobs.append(job)
            self.logger.info('Submitted jobs: {0}'.format([job.id for job in jobs]))

            if qsub_wait:
                # montitor the qsub jobs until they are all completed
                self.qsub.monitor_jobs(jobs = jobs)
        else:
            self.logger.info("No jobs were submitted for task {0}".format(self.taskname))
        return(None)


class SnsTask(AnalysisTask):
    '''
    Class for a task that runs part of the sns pipeline on the analysis

    from task_classes import AnnotationInplace
    x = AnnotationInplace()
    '''
    def __init__(self, analysis, taskname, config_file, extra_handlers = None):
        '''
        '''
        AnalysisTask.__init__(self, taskname = str(taskname), config_file = config_file, analysis = analysis, extra_handlers = extra_handlers)

        # directory holding the sns repo
        self.sns_repo_dir = os.path.join(self.analysis.dir, 'sns')
        # with self.tools.DirHop(self.analysis.dir) as d:
        #     do_something()



class AnnotationInplace(AnalysisTask):
    '''
    Class for annotation object to add to other analysis steps

    from task_classes import AnnotationInplace
    x = AnnotationInplace()
    '''
    def __init__(self, taskname = 'Annotation_inplace', config_file = 'Annotation_inplace.yml', extra_handlers = None):
        '''
        '''
        AnalysisTask.__init__(self, taskname = taskname, config_file = config_file, analysis = None, extra_handlers = extra_handlers)

    def annotate(self, input_dir, annotation_method = 'ANNOVAR'):
        '''
        Run an annotation command

        Function for annotating genomic regions and variants output by other pipeline steps in-place
        without creating a new output directory just for the annotations
        because for reporting purposes, you might end up needing both the pipeline task
        raw output and the annotations in the same location.

        This function will use the ANNOVAR annotation script, which finds and runs ANNOVAR
        on all the .bed files found (maybe .vcf too? TODO: decide this later)

        annotation_method is one of ANNOVAR, ChIPseeker, or biomaRt_ChIPpeakAnno,
        based on the external configs which are based on the subdirs in the annotation
        package

        TODO: add testing to this function... somehow...

        example command output:
        annotation_command = '/ifs/data/molecpathlab/scripts/snsxt/snsxt/sns_tasks/scripts/annotate-peaks/ANNOVAR/annotate.R -d /ifs/data/molecpathlab/scripts/snsxt/example_sns_analysis2/Summary-Avg-Coverage --bin-dir /ifs/data/molecpathlab/bin/annovar_annotate --db-dir /ifs/data/molecpathlab/bin/annovar_annotate/db --genome hg19'
        '''
        self.logger.debug("Starting annotation for dir: {0}".format(input_dir))
        self.logger.debug("Annotation method: {0}".format(annotation_method))

        scripts_dir_name = self.task_configs['scripts_dir_name']
        # annotate-peaks

        tasks_scripts_dir = self.main_configs['tasks_scripts_dir']
        # /ifs/data/molecpathlab/scripts/snsxt/snsxt/sns_tasks/scripts

        annotation_script = os.path.join(annotation_method, self.task_configs['annotation_methods'][annotation_method])
        # ANNOVAR/annotate.R

        annotation_script_path = os.path.join(tasks_scripts_dir, scripts_dir_name, annotation_script)
        self.logger.debug('path to annotation script will be: {0}'.format(annotation_script_path))

        # create the annotation_command; default is None
        annotation_command = None

        # ANNOVAR annotation method; add other methods later as needed!
        if annotation_method == "ANNOVAR":
            bin_dir = self.task_configs['ANNOVAR_bin_dir']
            db_dir = self.task_configs['ANNOVAR_db_dir']
            genome = self.task_configs['ANNOVAR_genome']

            annotation_command = '''
            {0} -d {1} --bin-dir {2} --db-dir {3} --genome {4}
            '''.format(
            annotation_script_path, # 0
            input_dir, # 1
            bin_dir, # 2
            db_dir, # 3
            genome # 4
            )

            self.logger.debug('ANNOVAR script command: {0}'.format(annotation_command))

        # run the annotation command
        if annotation_command:
            run_cmd = self.tools.SubprocessCmd(command = annotation_command).run()
            self.logger.debug(run_cmd.proc_stderr)

        return()
