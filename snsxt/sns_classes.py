#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
General utility classes for the program
'''
import os
import sys
import csv
from collections import defaultdict

from util import find
from util import log
from util import tools
from util.classes import LoggedObject
import config

# ~~~~ CUSTOM CLASSES ~~~~~~ #
class AnalysisItem(LoggedObject):
    '''
    Base class for objects associated with an sns sequencing analysis
    '''
    def __init__(self, id, extra_handlers = None):
        LoggedObject.__init__(self, id = id, extra_handlers = extra_handlers)
        self.id = id
        # a dictionary of files associated with the item
        self.files = defaultdict(list)
        # a dictionary of dirs associated with the item
        self.dirs = defaultdict(list)

    def list_none(self, l):
        '''
        return None for an empty list, or the first element of a list
        convenience function for dealing with object's file lists
        '''
        if len(l) == 0:
            return(None)
        elif len(l) > 0:
            return(l[0])

    def set_dir(self, name, path):
        '''
        Add a single dir to the analysis object's 'dirs' dict
        name = dict key
        path = dict value
        '''
        if isinstance(path, str):
            self.dirs[name] = [os.path.abspath(path)]
        else:
            self.dirs[name] = [os.path.abspath(p) for p in path]

    def set_dirs(self, name, paths_list):
        '''
        Add dirs to the analysis object's 'dirs' dict
        name = dict key
        paths_list = list of file paths
        '''
        self.set_dir(name = name, path = paths_list)

    def set_file(self, name, path):
        '''
        Add a single file to the analysis object's 'files' dict
        name = dict key
        path = dict value
        '''
        if isinstance(path, str):
            self.files[name] = [os.path.abspath(path)]
        else:
            self.files[name] = [os.path.abspath(p) for p in path]

    def set_files(self, name, paths_list):
        '''
        Add a file to the analysis object's 'files' dict
        name = dict key
        paths_list = list of file paths
        '''
        # self.files[name] = [os.path.abspath(path) for path in paths_list]
        self.set_file(name = name, path = paths_list)

    def add_file(self, name, path):
        '''
        Add a file to the analysis object's 'files' dict
        name = dict key
        paths_list = list of file paths
        '''
        self.files[name].append(os.path.abspath(path))


    def add_files(self, name, paths_list):
        '''
        Add a file to the analysis object's 'files' dict
        name = dict key
        paths_list = list of file paths
        '''
        for path in paths_list:
            self.files[name].append(os.path.abspath(path))

    def get_files(self, name):
        '''
        Retrieve a file by name from the object's 'files' dict
        name = dict key
        i = index entry in file list
        '''
        return(self.files[name])

    def get_dirs(self, name):
        '''
        Retrieve a file by name from the object's 'files' dict
        name = dict key
        i = index entry in file list
        '''
        return(self.dirs[name])

    # def get_file(self, name):
    #     '''
    #     Retrieve a file by name from the object's 'files' dict
    #     name = dict key
    #     i = index entry in file list
    #     '''
    #     f = self.list_none(l = self.files[name])
    #     if i != None:
    #         return(f[int(i)])
    #     else:
    #         return(f)




class SnsWESAnalysisOutput(AnalysisItem):
    '''
    Container for metadata about a sns WES targeted exome sequencing run analysis
    '''
    def __init__(self, dir, id, sns_config, results_id = None, extra_handlers = None):
        '''
        Initialize the object

        dir = path to the analysis output directory
        id = ID for the analysis, typically the parent analysis output dir name, corresponding to a NextSeq run ID
        results_id = typically a time-stamped ID of the results for the analysis, and the subdir name for the anaysis output

        e.g.:
        dir = "/ifs/data/molecpathlab/NGS580_WES/170623_NB501073_0015_AHY5Y3BGX2/results_2017-06-26_20-11-26"
        id = "170623_NB501073_0015_AHY5Y3BGX2"
        results_id = "results_2017-06-26_20-11-26"

        sns_config = dictionary of configuration items for the run; requires 'analysis_output_index' dict, and 'email_recipients'
        extra_filehandlers = None or a list of handlers to add


        from sns_classes import SnsWESAnalysisOutput
        import config
        d = '/ifs/data/molecpathlab/scripts/snsxt/snsxt/fixtures/sns_output/sns_analysis1'
        x = SnsWESAnalysisOutput(dir = d, id = 'sns_analysis1', sns_config = config.sns)
        '''
        AnalysisItem.__init__(self, id = id, extra_handlers = extra_handlers)
        # ID for the analysis run output; should match NextSeq ID
        self.id = str(id)

        # path to the directory containing analysis output
        self.dir = os.path.abspath(dir)
        # config dict for sns program settings
        self.sns_config = sns_config
        # timestamped ID for the analysis results, if supplied
        self.results_id = results_id
        # extra log handlers
        self.extra_handlers = extra_handlers

        self._init_attrs()
        self._init_dirs()
        self._init_targets_bed()
        self._init_static_files()
        # self._init_analysis_config()

        # get the samples for the analysis
        # self.samples = self.get_samples()
        self.is_valid = self.validate()

        # set up per-analysis logger
        # self.logger = log.build_logger(name = self.id)
        # self.extra_handlers = extra_handlers
        # if self.extra_handlers:
        #     self.logger = log.add_handlers(logger = self.logger, handlers = extra_handlers)
        # self.logger.debug("Initialized logging for analysis: {0}".format(self.id))
    def _init_attrs(self):
        '''
        Initialize attributes for the analysis
        '''
        self.email_recipients = self.sns_config['email_recipients']
        self.analysis_output_index = self.sns_config['analysis_output_index']

    def _init_dirs(self):
        '''
        Initialize the paths  attributes for items associated with the sequencing run
        from list of dirnames and filename patterns for the output steps in the sns WES analysis output
        '''
        for name, attributes in self.analysis_output_index.items():
            if name not in ['_parent']:
                self.set_dir(name = name, path = find.find(search_dir = self.dir, inclusion_patterns = name, search_type = "dir", num_limit = 1, level_limit = 0))

    def _init_static_files(self):
        '''
        Initialize paths to files that should always exist in the same location for an analysis output directory
        '''
        self.static_files = {key: value for key, value in self.expected_static_files().items()}

    def _init_targets_bed(self):
        '''
        Initialize the path to the targets .bed file with the chromosome target regions
        '''
        self.set_file(name = 'targets_bed', path = find.find(search_dir = self.dir, inclusion_patterns = "*.bed", exclusion_patterns = '*.pad10.bed', search_type = 'file', num_limit = 1, level_limit = 0))

    def get_analysis_config(self):
        '''
        Return a dictionary of config values to pass to child Sample objects
        '''
        analysis_config = {}
        analysis_config['analysis_id'] = self.id
        analysis_config['analysis_dir'] = self.dir
        analysis_config['results_id'] = self.results_id

        analysis_config['dirs'] = self.dirs
        analysis_config['files'] = self.files
        analysis_config['static_files'] = self.static_files

        analysis_config['analysis_is_valid'] = self.is_valid

        # analysis_config['sns_config'] = self.sns_config
        return(analysis_config)

    def expected_static_files(self):
        '''
        Return a dict of files that are expected to exist in the analysis dir
        '''
        expected_files = {}
        # samplesheet file with the run's paired samples
        expected_files['paired_samples'] = os.path.join(self.dir, 'samples.pairs.csv')
        # file with the original starting .fastq file paths & id's
        expected_files['samples_fastq_raw'] = os.path.join(self.dir, 'samples.fastq-raw.csv')
        # file with settings for the analysis
        expected_files['settings'] = os.path.join(self.dir, 'settings.txt')
        # summary table produced at the end of the WES pipeline
        expected_files['summary_combined_wes'] = os.path.join(self.dir, 'summary-combined.wes.csv')
        return(expected_files)

    def get_qsub_logfiles(self, logdir = None):
        '''
        Get the list of log files from the qsub dir

        logdir = x.list_none(x.get_dirs('logs-qsub'))
        log_files = [item for item in find.find(logdir, search_type = 'file')]
        '''
        log_files = []
        # try to get the logdir from self
        if not logdir:
            logdir = self.list_none(self.get_dirs('logs-qsub'))
        if not logdir:
            # TODO: need an exception here
            self.logger.error('Qsub log dir not found.')
        else:
            # find all the log files
            for item in find.find(logdir, search_type = 'file'):
                log_files.append(item)
        return(log_files)

    def check_qsub_log_errors_present(self, log_files = None, err_patterns = ("ERROR:",)):
        '''
        Check the qsub logs for errors
        '''
        contains_errors = {}
        # try to find the log files from self
        if not log_files:
            log_files = self.get_qsub_logfiles()
        if not log_files:
            # TODO: need an exception here
            self.logger.error('Qsub log files not found.')

        # check all the files for the patterns
        for log_file in log_files:
            with open(log_file, 'rb') as f:
                lines = f.readlines()
            for line in lines:
                for err_pattern in err_patterns:
                    if err_pattern in line:
                        contains_errors[log_file] = True

        # return a boolean for presence of errors
        if len(contains_errors) < 1:
            return(False)
        else:
            # True or False; any values are True = some log(s) contained error(s)
            if any(contains_errors.values()): self.logger.warning('Error messages were found in qsub logs: {0}'.format([path for path, value in contains_errors.items() if value == True]))
            return(any(contains_errors.values()))

    def validate(self):
        '''
        Check if the analysis is valid for downstream usage
        '''
        # make sure dir exists
        dir_validation = os.path.exists(self.dir)

        # make sure all expected files exist
        static_files_validations = {}
        for key, value in self.expected_static_files().items():
            exists = os.path.exists(value)
            self.logger.debug('{0} : {1} : {2}'.format(key, value, exists))
            static_files_validations[key] = exists

        # check for qsub log errors
        qsub_log_error_validation = not self.check_qsub_log_errors_present()

        validations = {}
        validations['dir_validation'] = dir_validation
        validations['qsub_log_error_validation'] = qsub_log_error_validation
        validations['static_files_validations'] = all(static_files_validations.values())


        self.logger.debug(validations)

        is_valid = all(validations.values())
        self.logger.info('All run validations passed: {0}'.format(is_valid))

        return(is_valid)


    def get_samplesIDs_from_samples_fastq_raw(self, samples_fastq_raw_file = None):
        '''
        Get the samples in the run from the samples_fastq_raw file
        '''
        self.logger.debug("Getting sample ID's from the 'samples_fastq_raw' file for the analysis")
        samplesIDs = []
        # try to get the file if it wasn't passed
        if not samples_fastq_raw_file:
            samples_fastq_raw_file = self.static_files.get('samples_fastq_raw', None)

        #
        if samples_fastq_raw_file:
            with open(samples_fastq_raw_file, "rb") as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    samplesIDs.append(row[0])

        else:
            self.logger.error('The "samples_fastq_raw" file could not be found for the analysis.')
        # unique entries only
        samplesIDs = list(set(samplesIDs))
        return(samplesIDs)

    def get_samples(self, samplesIDs = None):
        '''
        Get the samples for the analysis
        samplesIDs is a list of character string sample ID's
        '''
        samples = []
        # try to get the sample IDs
        if not samplesIDs:
            samplesIDs = self.get_samplesIDs_from_samples_fastq_raw()
        for samplesID in samplesIDs:
            samples.append(SnsAnalysisSample(id = samplesID, analysis_config = self.get_analysis_config(), sns_config = self.sns_config, extra_handlers = self.extra_handlers))
        return(samples)

    def __repr__(self):
        return("SnsWESAnalysisOutput {0} ({1}) located at {2}".format(self.id, self.results_id, self.dir))



class SnsAnalysisSample(AnalysisItem):
    '''
    Container for metadata about a sample in the sns WES targeted exome sequencing run analysis output
    '''

    def __init__(self, id, analysis_config, sns_config, extra_handlers = None):
        AnalysisItem.__init__(self, id = id, extra_handlers = extra_handlers)
        self.id = str(id)
        # set up per-sample logger
        # self.logger = log.build_logger(name = self.id)
        # if extra_handlers:
        #     self.logger = log.add_handlers(logger = self.logger, handlers = extra_handlers)
        # self.logger.debug("Initialized logging for sample: {0}".format(self.id))

        self.analysis_config = analysis_config
        # self.logger.debug("Analysis is: {0}".format(self.analysis))

        # file matching pattern based on the sample's id
        self.search_pattern = '{0}*'.format(self.id)

    def get_output_files(self, analysis_step, pattern):
        '''
        Get a file from the sample's analysis output
        '''
        # get the dirpath for the analysis step from the analysis dir; return None if there isn't one set for the provided step
        search_dir = self.list_none(self.analysis.dirs[analysis_step])
        patterns = [pattern, self.search_pattern]
        f = []
        if search_dir:
            self.logger.debug("Searching for {0} files in {1}, dir: {2}".format(patterns, analysis_step, search_dir))
            f = find.find(search_dir = search_dir, inclusion_patterns = patterns, search_type = 'file', match_mode = 'all')
            self.logger.debug('Found: {0}'.format(f))
        else:
            self.logger.error("search_dir not found for {0}, dir: {1}".format(analysis_step, search_dir))
        return(f)
