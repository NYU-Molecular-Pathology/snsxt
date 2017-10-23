#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Base classes for snsxt analysis tasks
'''
import os
import sys
import re

# add parent dir to sys.path to import util
scriptdir = os.path.dirname(os.path.realpath(__file__)) # this script's dir
parentdir = os.path.dirname(scriptdir) # this script's parent dir
sys.path.insert(0, parentdir)
import log
import util
from util import tools
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

        # get the 'main_configs' from this script
        self.main_configs = configs
        # get the 'task_configs' from external YAML file
        self._task_config_from_file(config_file = config_file)

        if analysis:
            # setup the input and output locations
            self.output_dir = self.tools.mkdirs(path = os.path.join(self.analysis.dir, self.task_configs['output_dir_name']), return_path = True)
            self.logger.debug('output_dir: {0}'.format(self.output_dir))
            self.input_dir = os.path.join(self.analysis.dir, self.task_configs['input_dir'])


    def _task_config_from_file(self, config_file):
        '''
        Load a YAML formatted file and add it to the object's configs
        config_file = basename of a file in the tasks_config_dir, for convenience
        '''
        config_filepath = os.path.join(self.main_configs['tasks_config_dir'], config_file)
        with open(config_filepath, "r") as f:
            self.task_configs = yaml.load(f)
            self.task_configs['config_file'] = config_filepath

    def get_report_files(self):
        '''
        Get the files for the report based on the configs, return a list of files
        '''
        report_files = []
        self.logger.debug('Getting report files for task: {0}'.format(self.taskname))
        report_dir = self.main_configs['tasks_reports_dir']
        if self.task_configs.get('report_files', None):
            for item in self.task_configs['report_files']:
                file_path = os.path.join(report_dir, item)
                report_files.append(file_path)
        else:
            self.logger.warning('No report files are set for analysis task {0}'.format(self.taskname))
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
                logger.debug("Copying report file '{0}' to '{1}' ".format(item, output_file))
                shutil.copy2(item, output_file)
            # copy over the config file itself as well if present
            if self.task_configs.get('config_file', None):
                output_file = os.path.join(output_dir, 'config.yml')
                logger.debug("Copying cofig file '{0}' to '{1}' ".format(self.task_configs['config_file'], output_file))
                shutil.copy2(self.task_configs['config_file'], output_file)
        else:
            self.logger.debug('No report files set for task')

    def annotate(self, input_dir = None, extra_handlers = None):
        '''
        Run the ANNOVAR in-place annotation on the analysis task;
        only works if an 'analysis' was passed
        '''
        if not extra_handlers:
            extra_handlers = getattr(self, 'extra_handlers', None)# self.extra_handlers
        x = AnnotationInplace(extra_handlers = extra_handlers).annotate(input_dir = self.output_dir, annotation_method = 'ANNOVAR')
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
        if analysis:
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
                self.qsub.monitor_jobs(jobs = jobs)
        return()

    def run_qsub_analysis_task(self, analysis = None, qsub_wait = True, *args, **kwargs):
        '''
        Run a task that submits one qsub job for the analysis
        analysis is an SnsWESAnalysisOutput object
        task is a module with a function 'main' that returns a qsub Job object
        qsub_wait = wait for all qsub jobs to complete
        '''
        if not analysis:
            analysis = getattr(self, 'analysis', None)
        if analysis:
            # empty list to hold the qsub jobs
            jobs = []
            # run the task on each sample; should return a qsub Job object
            job = self.main(sample = sample, *args, **kwargs)
            if job:
                jobs.append(job)
                self.logger.info('Submitted jobs: {0}'.format([job.id for job in jobs]))

                if qsub_wait:
                    # montitor the qsub jobs until they are all completed
                    self.qsub.monitor_jobs(jobs = jobs)
            else:
                self.logger.info("No jobs were submitted for task {0}".format(self.taskname))
        return()











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












class HapMapVariantRef(AnalysisTask):
    '''
    Class for comparing each HapMap sample variant calls against
    a known list of previously sequenced HapMap variants
    Save the overlapping variants in a new files to load in the report

    from HapMap_variant_ref_dev import HapMapVariantRef
    x = HapMapVariantRef(analysis = None)
    '''
    def __init__(self, analysis, taskname = 'HapMap_variant_ref', config_file = 'HapMap_variant_ref.yml', extra_handlers = None):
        '''
        '''
        AnalysisTask.__init__(self, taskname = taskname, config_file = config_file, analysis = analysis, extra_handlers = extra_handlers)

    def main(self, sample):
        '''
        Main function for running the analysis task
        '''
        self.logger.debug('Sample is: {0}'.format(sample))

        # get paths to files for the sample
        # file with the sample's ANNOVAR annotations
        sample_annot_file = sample.list_none(sample.get_output_files(analysis_step = self.task_configs['input_dir'], pattern = self.task_configs['input_pattern']))
        self.logger.debug('sample_annot_file is: {0}\nand has {1} entries'.format(sample_annot_file, self.tools.num_lines(sample_annot_file, skip = 1)))

        # reference HapMap variants file
        hapmap_variant_file = os.path.join(self.main_configs['tasks_files_dir'], self.task_configs['hapmap_variant_file'])

        # file to save the variants not in the reference list
        output_file = os.path.join(self.output_dir, os.path.basename(sample_annot_file))

        # check if the sample ID indicates that it is HapMap sample
        if re.match('hapmap', sample.id, re.IGNORECASE):
            self.logger.debug('Sample is a HapMap sample')



            # reference HapMap variants file; copy it over
            self.logger.debug('hapmap_variant_file is: {0}\nand has {1} entries'.format(hapmap_variant_file, self.tools.num_lines(hapmap_variant_file, skip = 1)))

            logger.debug('Output file will be: {0}'.format(output_file))

            # find the new variants
            logger.debug('Overlapping the sample_annot_file against the hapmap_variant_file...')
            self.tools.write_tabular_overlap(file1 = sample_annot_file, ref_file = hapmap_variant_file, output_file = output_file, delim = '\t', inverse = True)
            logger.debug('{0} non-overlapping variants were output'.format(self.tools.num_lines(output_file, skip = 1)))
        return(hapmap_variant_file)

    def run(self, *args, **kwargs):
        '''
        Run the analysis step
        '''
        self.run_sample_task(analysis = self.analysis, *args, **kwargs)
        self.setup_report()













class GATKDepthOfCoverageCustom(AnalysisTask):
    '''
    Class for running custom thresholds GATK DepthOfCoverage with the sns pipeline
    '''
    def __init__(self, analysis, taskname = 'GATK_DepthOfCoverage_custom', config_file = 'GATK_DepthOfCoverage_custom.yml', extra_handlers = None):
        '''
        '''
        AnalysisTask.__init__(self, taskname = taskname, config_file = config_file, analysis = analysis, extra_handlers = extra_handlers)

    def make_tresholds_arg(self):
        '''
        Make the command line arg for the thresholds to use
        ex: -ct 10 -ct 50 -ct 100 -ct 500

        d = {'thresholds': [10, 50, 100, 200, 500]}
        '''
        thresholds = self.task_configs['thresholds']
        return(' '.join(['-ct ' + str(x) for x in thresholds]))

    def gatk_DepthOfCoverage_cmd(self, sampleID, bam_file, intervals_bed_file, output_dir):
        '''
        Build the terminal commands to run GATK DepthOfCoverage on a single sample

        ex:
        $gatk_cmd -T DepthOfCoverage -dt NONE $gatk_log_level_arg \
        -rf BadCigar \
        --reference_sequence $ref_fasta \
        --intervals $bed \
        --omitDepthOutputAtEachBase \
        -ct 10 -ct 50 -ct 100 -ct 500 -mbq 20 -mmq 20 --nBins 999 --start 1 --stop 1000 \
        --input_file $bam \
        --outputFormat csv \
        --out $out_prefix
        '''
        # get params from config
        GATK_bin = self.task_configs['bin']
        ref_fasta = self.task_configs['ref_fasta']
        minBaseQuality = self.task_configs['minBaseQuality']
        minMappingQuality = self.task_configs['minMappingQuality']
        nBins = self.task_configs['nBins']
        start = self.task_configs['start']
        stop = self.task_configs['stop']
        outputFormat = self.task_configs['outputFormat']
        readFilter = self.task_configs['readFilter']
        downsampling_type = self.task_configs['downsampling_type']
        thresholds_arg = self.make_tresholds_arg()
        output_summary_file = os.path.join(output_dir, '{0}'.format(sampleID))

        gatk_cmd = '''
    java -Xms16G -Xmx16G -jar {0} -T DepthOfCoverage \
    --logging_level ERROR \
    --downsampling_type {1} \
    --read_filter {2} \
    --reference_sequence {3} \
    --omitDepthOutputAtEachBase \
    {4} \
    --intervals {5} \
    --minBaseQuality {6} \
    --minMappingQuality {7} \
    --nBins {8} \
    --start {9} \
    --stop {10} \
    --input_file {11} \
    --outputFormat {12} \
    --out {13}
    '''.format(
    GATK_bin,
    downsampling_type,
    readFilter,
    ref_fasta,
    thresholds_arg,
    intervals_bed_file,
    minBaseQuality,
    minMappingQuality,
    nBins,
    start,
    stop,
    bam_file,
    outputFormat,
    output_summary_file
    )
        return(gatk_cmd)

    def main(self, sample, extra_handlers = None):
        '''
        Main control function for the program
        Runs GATK DepthOfCoverage on a single sample from an sns analysis
        sample is an SnsAnalysisSample object
        return the qsub job for the sample
        '''
        self.logger.debug('Sample is: {0}'.format(sample))
        self.logger.debug(sample.static_files)
        self.log.print_filehandler_filepaths_to_log(logger = self.logger)

        # get the dir for the qsub logs
        qsub_log_dir = sample.list_none(sample.analysis_config['dirs']['logs-qsub'])
        self.logger.debug('qsub_log_dir: {0}'.format(qsub_log_dir))

        sample_bam = sample.list_none(sample.get_output_files(analysis_step = self.task_configs['input_dir'], pattern = self.task_configs['input_pattern']))
        targets_bed = sample.list_none(sample.get_files('targets_bed'))

        if sample_bam and output_dir and qsub_log_dir:
            self.logger.debug('sample_bam: {0}'.format(sample_bam))

            # make the shell command to run
            command = self.gatk_DepthOfCoverage_cmd(sampleID = sample.id, bam_file = sample_bam, output_dir = output_dir, intervals_bed_file = targets_bed)
            self.logger.debug(command)

            # submit the command as a qsub job on the HPC
            # commands to create debug jobs
            # command = 'sleep 60'
            # qsub_log_dir = qsub_log_dir[:-1]
            job = self.qsub.submit(command = command, name = self.taskname + '.' + sample.id, stdout_log_dir = qsub_log_dir, stderr_log_dir = qsub_log_dir, verbose = True, sleeps = 1) #
            return(job)
        else:
            self.logger.error('A required item does not exist')

    def run(self, *args, **kwargs):
        '''
        Run the analysis step
        '''
        self.run_qsub_sample_task(analysis = self.analysis, *args, **kwargs)
        self.setup_report()


class SummaryAvgCoverage(AnalysisTask):
    '''
    Class for creating summaries of the average coverages for the analysis from GATK DepthOfCoverage output
    '''
    def __init__(self, analysis, taskname = 'Summary_Avg_Coverage', config_file = 'Summary_Avg_Coverage.yml', extra_handlers = None):
        '''
        '''
        AnalysisTask.__init__(self, taskname = taskname, config_file = config_file, analysis = analysis, extra_handlers = extra_handlers)
        self.task_configs['run_script_path'] = os.path.join(self.main_configs['tasks_scripts_dir'], self.task_configs['run_script'])
        # /ifs/data/molecpathlab/scripts/snsxt/snsxt/sns_tasks/scripts/calculate_average_coverages.R

    def make_run_script_cmd(self, input_dir, output_dir, run_script):
        '''
        Make the shell command to run the run_script
        '''
        command = '''
    {0} -d {1} -o {2}
    '''.format(
    run_script, # 0
    input_dir, # 1
    output_dir # 2
    )
        return(command)

    def main(analysis):
        '''
        Main control function for the program
        Creates summary coverage files for all samples in the analysis
        '''
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

        Annotation_inplace(input_dir = output_dir, annotation_method = configs['annotation_method'], extra_handlers = extra_handlers)

    def run(self, *args, **kwargs):
        '''
        '''
        self.run_analysis_task(analysis = self.analysis, *args, **kwargs)
        self.setup_report()
