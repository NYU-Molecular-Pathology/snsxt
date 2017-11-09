#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Base classes for snsxt analysis tasks
"""
import os
import sys
import csv
import yaml
import shutil


# ~~~~ LOAD MORE PACKAGES ~~~~~~ #
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
import job_management
import _exceptions as _e
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
configs = config.config

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


# ~~~~~ CLASSES ~~~~~ #
class AnalysisTask(LoggedObject):
    """
    Base class for an sns analysis tasks

    Examples
    --------
    Example usage::

        from task_classes import AnalysisTask
        x = AnalysisTask(taskname = 'Delly2', config_file = 'Delly2.yml')

    """
    def __init__(self, taskname, config_file, analysis = None, extra_handlers = None, setup_report = True):
        """
        Parameters
        ----------
        taskname: str
            the name of the task
        analysis: SnsWESAnalysisOutput
            the `sns` pipeline output object to run the task on
        config_file: str
            basename of the YAML formatted config file in the ``tasks_config_dir`` to use for ``task_configs``
        extra_handlers: list
            a list of extra Filehandlers to use for logging
        setup_report: bool
            ``True`` or ``False``, whether or not the task's ``report_files`` should be copied over and configured in the ``output_dir``
        """
        LoggedObject.__init__(self, id = taskname, extra_handlers = extra_handlers)
        self.taskname = str(taskname)
        self.analysis = analysis

        # attach modules so they are easier to access in derived classes
        self.util = util
        self.tools = tools
        self.qsub = qsub
        self.log = log
        self.find = find
        self._exceptions = _e

        # get the 'main_configs' from this script
        self.main_configs = configs
        """
        The global configs for the program
        """

        if config_file:
            # get the 'task_configs' from external YAML file, load them in self.task_configs
            self._task_config_from_file(config_file = config_file) #
            # set some extra attributes for convenience
            self._init_task_attrs()

        if analysis:
            # setup the input and output locations
            self._init_locs()

        if setup_report:
            # setup the report
            self.setup_report()

    def __repr__():
        return('{0}'.format(self.taskname))

    def _init_task_attrs(self):
        """
        Initializes object attributes from the ``task_configs``, if they're present in the YAML config file
        """
        if self.task_configs.get('input_pattern', None):
            self.input_pattern = self.task_configs['input_pattern']

        if self.task_configs.get('input_suffix', None):
            self.input_suffix = self.task_configs['input_suffix']

        if self.task_configs.get('output_pattern', None):
            self.output_pattern = self.task_configs['output_pattern']

        if self.task_configs.get('output_suffix', None):
            self.output_suffix = self.task_configs['output_suffix']

        if self.task_configs.get('output_suffixes', None):
            self.output_suffixes = self.task_configs['output_suffixes']

        if self.task_configs.get('output_files', None):
            self.output_files = self.task_configs['output_files']

        if self.task_configs.get('input_files', None):
            self.input_files = self.task_configs['input_files']

        if self.task_configs.get('email_files', None):
            self.email_files = self.task_configs['email_files']

        if self.task_configs.get('email_suffixes', None):
            self.email_suffixes = self.task_configs['email_suffixes']



    def _init_locs(self):
        """
        Initializes locations for the task
        """
        self.output_dir = self.tools.mkdirs(path = os.path.join(self.analysis.dir, self.task_configs['output_dir_name']), return_path = True)
        self.logger.debug('task output_dir: {0}'.format(self.output_dir))
        self.input_dir = os.path.join(self.analysis.dir, self.task_configs['input_dir'])
        self.validate_items([self.output_dir, self.input_dir])

    def _task_config_from_file(self, config_file):
        """
        Loads a YAML formatted config file and adds it to the object's ``task_configs`` dictionary

        Parameters
        ----------
        config_file: str
            basename of the YAML formatted config file in the ``tasks_config_dir`` to use for ``task_configs``
        """
        config_filepath = os.path.join(self.main_configs['tasks_config_dir'], config_file)
        self.logger.debug('Loading task config file: {0}'.format(config_filepath))
        self.validate_items([config_filepath])
        with open(config_filepath, "r") as f:
            self.task_configs = yaml.load(f)
            self.task_configs['config_file'] = config_filepath

    def get_path(self, dirpath, file_basename, validate = False):
        """
        Generates an expected filepath for an item associated with the analysis. Optionally validate the file

        Parameters
        ----------
        dirpath: str
            path to the parent directory for the expected file
        file_basename: str
            name of the expected file
        validate: bool
            whether or not to validate the file e.g. to check if it exists, etc.

        Returns
        -------
        str
            the expected path to the file
        """
        # self.logger.debug('dirpath is {0}'.format(dirpath))
        # self.logger.debug('file_basename is {0}'.format(file_basename))
        path = os.path.join(dirpath, file_basename)
        # self.logger.debug('path is {0}'.format(path))
        if validate:
            # self.logger.debug('Validating expected file path: {0}'.format(path))
            self.validate_items([path])
        return(path)

    def get_analysis_file_outpath(self, file_basename):
        """
        Creates a path to a file in the analysis ``output_dir``

        Parameters
        ----------
        file_basename: str
            name of the expected file

        Returns
        -------
        str
            the expected path to the file

        Notes
        -----
        Does not validate that the file exists

        Examples
        --------
        Example usage::

            output_file = self.get_analysis_file_outpath(file_basename = 'foo.txt')

        """
        output_path = self.get_path(dirpath = self.output_dir, file_basename = file_basename, validate = False)
        return(output_path)

    def get_analysis_file_inputpath(self, file_basename, validate = True):
        """
        Creates a path to a file that is expected to exist in the analysis ``input_dir``

        Parameters
        ----------
        file_basename: str
            name of the expected file

        Returns
        -------
        str
            the expected path to the file

        Notes
        -----
        Validates that the file exists by default, raising an exception if the file does not exist or pass validation

        Examples
        --------
        Example usage::

            input_file = self.get_analysis_file_inputpath(file_basename = 'foo.txt')

        """
        path = self.get_path(dirpath = self.input_dir, file_basename = file_basename, validate = validate)
        return(path)

    def get_expected_output_files(self, analysis = None):
        """
        Gets the paths to all files expected to be output by the task.

        Parameters
        ----------
        analysis: SnsWESAnalysisOutput
            the `sns` pipeline output object to run the task on. If ``None`` is passed, ``self.analysis`` is retrieved instead.

        Returns
        -------
        list
            a list of the expected output file paths for all files expected to be output by the task

        Notes
        -----
        Filepaths returned are not validated for existence. Expected output files must be listed in the task's ``config_file``
        """
        if not analysis:
            analysis = getattr(self, 'analysis', None)

        expected_output = []

        # check if there are output_files set
        if not getattr(self, 'output_files', None):
            self.logger.debug('output files not set for analysis task {0}'.format(self.taskname))
            return(expected_output)

        for output_file in self.output_files:
            path = self.get_analysis_file_outpath(file_basename = output_file)
            expected_output.append(path)

        if len(expected_output) < 1:
            self.logger.warning('output files were not set for analysis task {0}'.format(self.taskname))

        return(expected_output)

    def get_expected_email_files(self, analysis = None):
        """
        Gets the paths to all files from the task output which should be included in email output

        Parameters
        ----------
        analysis: SnsWESAnalysisOutput
            the `sns` pipeline output object to run the task on. If ``None`` is passed, ``self.analysis`` is retrieved instead.

        Returns
        -------
        list
            a list of the expected output file paths

        """
        if not analysis:
            analysis = getattr(self, 'analysis', None)

        expected_email_files = []

        if not getattr(self, 'email_files', None):
            self.logger.debug('email files not set for analysis task {0}'.format(self.taskname))
            return(expected_email_files)

        for expected_email_file in self.email_files:
            path = self.get_path(dirpath = self.output_dir, file_basename = expected_email_file, validate = False)
            expected_email_files.append(path)

        if len(expected_email_files) < 1:
            self.logger.warning('output files were not set for analysis task {0}'.format(self.taskname))

        return(expected_email_files)


    def validate_items(self, items):
        """
        Runs validations on a list of items. Makes sure that all paths passed exist.

        Parameters
        ----------
        items: list
            a list of file or directory paths

        Todo
        ----
        Add more validation criteria.

        Need to raise an exception here if no items were passed?
        """
        # self.logger.debug('validating items: {0}'.format(items))
        self.logger.debug('validating {0} items'.format(len(items)))
        if len(items) < 1 or not items:
            # TODO: what to raise here?
            self.logger.error('No items were passed for validation')
            # sys.exit()
            return()
        # make sure all files and dirs exist
        items_exist = {}
        for item in items:
            # self.logger.debug('item is: {0}'.format(item))
            items_exist[item] = self.tools.item_exists(item)
        if not all(items_exist.values()):
            # self.logger.error('Some items did not exist:')
            # self.logger.error('{0}'.format(items_exist))
            raise _e.AnalysisFileMissing(message = 'Expected files for {0} do not exist:\n{1}'.format(self, items_exist), errors = '')
            # add more criteria here...

    def validate_output(self):
        """
        Validates all the expected output files from the analysis task
        """
        self.logger.debug('Validating expected task output')
        expected_output = self.get_expected_output_files()
        self.logger.debug('{0} Expected output files'.format(len(expected_output)))
        self.validate_items(expected_output)

    def get_report_files(self):
        """
        Gets the files for the report based on the configs

        Returns
        -------
        list
            a list of paths to files that should be used in the report for the task

        Notes
        -----
        Files for inclusion in the task's report should be set in the task config file.

        Files will be validated for existence, etc..
        """
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
        """
        Sets up the report files output for the pipeline step by copying over every associated file for the report to the task output dir

        Parameters
        ----------
        output_dir: str
            the output directory to copy files to. If ``None`` was passed, ``self.output_dir`` is used instead
        """
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

    def annotate(self, input_dir, extra_handlers = None):
        """
        Runs ANNOVAR annotation in-place on the analysis task output

        Parameters
        ----------
        input_dir: str
            the path to a directory with .bed files for annotation
        extra_handlers: list
            a list of extra Filehandlers to use for logging

        Returns
        -------
        None
            does not return anything

        Todo
        ----
        Should this method return something?

        Should extra handling be implemented to validate the input directory?

        Notes
        -----
        This method makes use of the ``AnnotationInplace`` class ``AnalysisTask`` to perform this extra analysis step on an analysis task's output without having to explicitly create an extra analysis task just for output annotation.

        """
        if not extra_handlers:
            extra_handlers = getattr(self, 'extra_handlers', None)
        # if not input_dir:
        #     input_dir = getattr(self, 'input_dir', None)
        # dont do this, input_dir might not be the right one!
        if input_dir:
            x = AnnotationInplace(extra_handlers = extra_handlers).annotate(input_dir = self.output_dir, annotation_method = 'ANNOVAR')
        else:
            self.logger.error('No input_dir specified')
        return()

    def run(self, analysis = None, *args, **kwargs):
        """
        Runs a task that operates an entire analysis output

        Parameters
        ----------
        analysis: SnsWESAnalysisOutput
            the `sns` pipeline output object to run the task on. If ``None`` is passed, ``self.analysis`` is retrieved instead.
        args: list
            a list of extra positional arguments to pass to ``self.main()``
        kwargs: dict
            a dictionary of extra positional arguments to pass to ``self.main()``

        Notes
        -----
        This method 'runs' the task, by making a call to ``self.main``.

        This method will be overwritten with ``run()`` set by child subclasses of ``AnalysisTask``.

        This default method is not intended for analysis tasks that submit qsub jobs, or for tasks that operate on each sample in an analysis individually.

        Todo
        ----
        Should this method ``return`` something?
        
        """
        if not analysis:
            analysis = getattr(self, 'analysis', None)
        if analysis:
            self.main(analysis = analysis, *args, **kwargs)
        return()











class AnalysisSampleTask(AnalysisTask):
    """
    Analysis Task task that will run separately for every sample in the analysis
    """
    def __init__(self, *ars, **kwargs):
        AnalysisTask.__init__(self, *ars, **kwargs)

    def get_sample_file_outpath(self, sampleID, suffix = None):
        """
        Create a path to a file in the analysis output directory
        """
        # try to resolve an output_suffix
        if not suffix:
            suffix = self.output_suffix
        output_path = os.path.join(self.output_dir, sampleID + suffix)
        return(output_path)

    def get_sample_file_inputpath(self, sampleID, suffix = None, validate = True):
        """
        Create the path to an expected sample file in the input directory
        """
        # try to resolve an input_suffix
        if not suffix:
            suffix = self.input_suffix
        path = os.path.join(self.input_dir, sampleID + suffix)
        if validate:
            self.logger.debug('Validating expected input file path: {0}'.format(path))
            self.validate_items([path])
        return(path)

    def get_expected_output_files(self, analysis = None):
        """
        Return a list of all the expected output files for all of the samples in the analysis
        """
        if not analysis:
            analysis = getattr(self, 'analysis', None)

        expected_output = []
        suffixes = []

        # get all the Sample objects for the analysis
        samples = analysis.get_samples()

        # check if there are output_suffix or output_suffixes set
        if getattr(self, 'output_suffix', None):
            suffixes.append(self.output_suffix)
        else:
            self.logger.debug('output_suffix not set for analysis task {0}'.format(self.taskname))

        if getattr(self, 'output_suffixes', None):
            for suffix in self.output_suffixes:
                suffixes.append(suffix)
        else:
            self.logger.debug('output_suffixes not set for analysis task {0}'.format(self.taskname))

        for sample in samples:
            for suffix in suffixes:
                path = self.get_sample_file_outpath(sampleID = sample.id, suffix = suffix)
                expected_output.append(path)

        if len(expected_output) < 1:
            self.logger.debug('expected output files could not be created for analysis task {0}'.format(self.taskname))

        if len(samples) < 1:
            self.logger.debug('No samples were found in the analysis')

        return(expected_output)

    def run(self, analysis = None, *args, **kwargs):
        """
        Run a task that operates on every sample in the analysis individually

        overrides AnalysisTask.run()
        """
        if not analysis:
            analysis = getattr(self, 'analysis', None)
        # get all the Sample objects for the analysis
        samples = analysis.get_samples()
        for sample in samples:
            self.logger.debug('Running task {0} on sample {1}'.format(self.taskname, sample.id))
            self.main(sample = sample, *args, **kwargs)
        # TODO: what to return here??
        return()










class QsubSampleTask(AnalysisSampleTask):
    """
    Analysis Task task that will submit a qsub job for every sample in the analysis
    """
    def __init__(self, *ars, **kwargs):
        AnalysisSampleTask.__init__(self, *ars, **kwargs)

    def run(self, analysis = None, qsub_wait = True, *args, **kwargs):
        """
        Run a task that submits qsub jobs on all the samples in the analysis output
        analysis is an SnsWESAnalysisOutput object
        task is a module with a function 'main' that returns a qsub Job object
        qsub_wait = wait for all qsub jobs to complete

        overrides AnalysisSampleTask.run()
        """
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
            self.logger.debug('Jobs will be monitored for completion and validated')
            job_management.monitor_validate_jobs(jobs = jobs)
            return(None)
        else:
            return(jobs)









class QsubAnalysisTask(AnalysisTask):
    """
    Analysis Task task that will submit a single qsub job for the entire analysis
    """
    def __init__(self, *ars, **kwargs):
        AnalysisTask.__init__(self, *ars, **kwargs)

    def run(self, analysis = None, qsub_wait = True, *args, **kwargs):
        """
        Run a task that submits one qsub job for the analysis
        analysis is an SnsWESAnalysisOutput object
        task is a module with a function 'main' that returns a qsub Job object
        qsub_wait = wait for all qsub jobs to complete

        overrides AnalysisTask.run()
        """
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
            self.logger.debug('Jobs will be monitored for completion and validated')
            job_management.monitor_validate_jobs(jobs = jobs)
            return(None)
        else:
            return(jobs)









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













class AnnotationInplace(AnalysisTask):
    """
    Class for annotation object to add to other analysis steps

    from task_classes import AnnotationInplace
    x = AnnotationInplace()
    """
    def __init__(self, taskname = 'Annotation_inplace', config_file = 'Annotation_inplace.yml', extra_handlers = None):
        """
        """
        AnalysisTask.__init__(self, taskname = taskname, config_file = config_file, analysis = None, extra_handlers = extra_handlers)

    def annotate(self, input_dir, annotation_method = 'ANNOVAR'):
        """
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
        """
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

            annotation_command = """
            {0} -d {1} --bin-dir {2} --db-dir {3} --genome {4}
            """.format(
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
