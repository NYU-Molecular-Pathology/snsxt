#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Contains base classes to use for analysis and sample objects in the program
"""
# ~~~~~ LOGGING ~~~~~~ #
import logging
logger = logging.getLogger(__name__)

import os
import csv
import _exceptions as _e
from util import tools
from util.classes import LoggedObject

class Analysis(LoggedObject):
    """
    Base class for an analysis object. Represents the metadata surrounding an analysis

    Parameters
    ----------
    id: str
        an identifier for the analysis
    dir: str
        path to the directory for the analysis
    extra_handlers: list
        a list of Filehandlers to be added to the object's internal logger
    debug: bool
        whether the analysis output should be intitialized in `debug` mode which skips initial validation

    Examples
    --------
    Example usage::

        from analysis import Analysis; x = Analysis(id = 'foo', dir = '..')
        from analysis import Analysis, Sample; x = Analysis(id = 'foo', dir = '../..'); x.get_samples(file = '../../samples.fastq-raw.csv', method = 'samples.fastq-raw.csv')

    Notes
    -----
    Historically implements the following::

        analysis.get_samples()
        analysis.dir
        analysis.id
        analysis.is_valid
        validations_message = json.dumps(analysis.validations, indent = 4)
        analysis.list_none # <- get rid of this one!


    """
    def __init__(self, id, dir, results_id = None, debug = False, extra_handlers = None):
        LoggedObject.__init__(self, id = id, extra_handlers = extra_handlers)
        self.id = str(id)
        self.results_id = results_id
        # path to the directory containing analysis output
        self.dir = os.path.abspath(dir)
        self.debug = debug
        self.extra_handlers = extra_handlers
        self.is_valid = True
        # TODO: this is a deprecated feature, remove references from this elsewhere in the program and move the functionality to the tasks

    def __repr__(self):
        return("Analysis(id='{0}', dir='{1}', results_id='{2}', debug='{3}', extra_handlers='{4}')".format(self.id, self.dir, self.results_id, self.debug, self.extra_handlers))

    def get_samples(self, file, method = 'samples.fastq-raw.csv'):
        """
        Gets the samples in the analysis

        Parameters
        ----------
        file: str
            path to file to get samples from
        method: str
            method to use for parsing samples from the file

        Returns
        -------
        list
            a list of ``Sample`` objects

        Examples
        --------
        Example usage::

            x.get_samples(file = '../../samples.fastq-raw.csv', method = 'samples.fastq-raw.csv')
        """
        if method == "samples.fastq-raw.csv":
            sampleIDs = self.sampleIDs_fastq_raw(file = file)
            samples = [Sample(id = sampleID, analysis = self, extra_handlers = self.extra_handlers) for sampleID in sampleIDs]
            return(samples)

    def sampleIDs_fastq_raw(self, file):
        """
        Get samples from a  'samples.fastq-raw.csv' file
        """
        if not tools.item_exists(file):
            raise _e.AnalysisFileMissing(message = 'The "samples_fastq_raw" file could not be found for the analysis: {0}'.format(file), errors = '')
        samplesIDs = []
        with open(file, "rb") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                samplesIDs.append(row[0])
        return(samplesIDs)


class Sample(LoggedObject):
    """
    Base class for a sample in the analysis. Represents the metadata surrounding an individual sample.

    Notes
    -----
    Historically implements the following::

        targets_bed = sample.list_none(sample.get_files('targets_bed'))
        qsub_log_dir = sample.list_none(sample.analysis_config['dirs']['logs-qsub'])
        sample.id
        sample_annot_file = sample.list_none(sample.get_output_files(analysis_step = self.task_configs['input_dir'], pattern = self.task_configs['input_pattern']))
        pairs_sheet = sample.static_files['paired_samples']
        self.logger.debug(sample.static_files)
    """
    def __init__(self, id, analysis, extra_handlers = None):
        """
        Parameters
        ----------
        id: str
            an identifier for the sample
        analysis: Analysis
            the parent analysis object for the sample
        extra_handlers: list
            a list of Filehandlers to be added to the object's internal logger
        """
        LoggedObject.__init__(self, id = id, extra_handlers = extra_handlers)
        self.id = str(id)
        self.analysis = analysis
        self.extra_handlers = extra_handlers

    def __repr__(self):
        return("Sample(id='{0}', analysis='{1}', extra_handlers='{2}')".format(self.id, self.analysis, self.extra_handlers))
