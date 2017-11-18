#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module for the base AnalysisSampleTask object class
"""
import os
from AnalysisTask import AnalysisTask

class AnalysisSampleTask(AnalysisTask):
    """
    An ``AnalysisTask`` that will run actions separately for every sample in the analysis
    """
    def __init__(self, *ars, **kwargs):
        AnalysisTask.__init__(self, *ars, **kwargs)

    def get_sample_file_outpath(self, sampleID, suffix = None):
        """
        Creates a path to an expected file in the analysis output directory by concatenating the provided ``sampleID`` and ``suffix`` into a file basename and then preprending the path to the task's ``output_dir``.

        Parameters
        ----------
        sampleID: str
            the ID for the sample
        suffix: str
            the suffix of the file to create. If ``None`` is passed, the task's ``output_suffix`` is used instead

        Returns
        -------
        str
            the path to the expected output file for the sample

        Examples
        --------
        Example usage::

            sample_output = self.get_sample_file_outpath(sampleID = sample.id, suffix = self.output_suffix)

        """
        # try to resolve an output_suffix
        if not suffix:
            suffix = self.output_suffix
        output_path = os.path.join(self.output_dir, sampleID + suffix)
        return(output_path)

    def get_sample_file_inputpath(self, sampleID, suffix = None, validate = True):
        """
        Creates a path to an expected file in the analysis input directory by concatenating the provided ``sampleID`` and ``suffix`` into a file basename and then preprending the path to the task's ``input_dir``.

        Parameters
        ----------
        sampleID: str
            the ID for the sample
        suffix: str
            the suffix of the file to create. If ``None`` is passed, the task's ``input_suffix`` is used instead
        validate: bool
            whether or not the filepath should be validated; ``True`` by default

        Returns
        -------
        str
            the path to the expected input file for the sample

        Examples
        --------
        Example usage::

            sample_bam = self.get_sample_file_inputpath(sampleID = sample.id, suffix = self.input_suffix)

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
        Creates a list of all the expected output files for all of the samples in the analysis

        Parameters
        ----------
        analysis: SnsWESAnalysisOutput
            the `sns` pipeline output object to run the task on. If ``None`` is passed, ``self.analysis`` is retrieved instead.

        Returns
        -------
        list
            a list of files that are expected to be output by the task
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
        Runs a task that operates on every sample in the analysis individually

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

        Todo
        ----
        Should this method ``return`` something?

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
