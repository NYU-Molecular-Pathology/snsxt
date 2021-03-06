#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re
from task_classes import QsubSampleTask

class GATKDepthOfCoverageCustom(QsubSampleTask):
    """
    Class for running custom thresholds GATK DepthOfCoverage with the sns pipeline
    """
    def __init__(self, analysis, taskname = 'GATK_DepthOfCoverage_custom', config_file = 'GATK_DepthOfCoverage_custom.yml', extra_handlers = None):
        """
        """
        QsubSampleTask.__init__(self, taskname = taskname, config_file = config_file, analysis = analysis, extra_handlers = extra_handlers)

    def make_tresholds_arg(self):
        """
        Make the command line arg for the thresholds to use
        ex: -ct 10 -ct 50 -ct 100 -ct 500

        d = {'thresholds': [10, 50, 100, 200, 500]}
        """
        thresholds = self.task_configs['thresholds']
        return(' '.join(['-ct ' + str(x) for x in thresholds]))

    def gatk_DepthOfCoverage_cmd(self, sampleID, bam_file, intervals_bed_file, output_dir):
        """
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
        """
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

        gatk_cmd = """
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
    """.format(
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
        """
        Main control function for the program
        Runs GATK DepthOfCoverage on a single sample from an sns analysis
        sample is an SnsAnalysisSample object
        return the qsub job for the sample
        """
        self.logger.debug('Sample is: {0}'.format(sample))
        self.logger.debug(sample.static_files)

        # TODO: does this need to be here??
        self.setup_report()

        # get the dir for the qsub logs
        qsub_log_dir = sample.list_none(sample.analysis_config['dirs']['logs-qsub'])
        self.logger.debug('qsub_log_dir: {0}'.format(qsub_log_dir))

        sample_bam = self.get_sample_file_inputpath(sampleID = sample.id, suffix = self.input_suffix)
        targets_bed = sample.list_none(sample.get_files('targets_bed'))

        # make sure the files and locations exist
        self.validate_items([sample_bam, qsub_log_dir])


        self.logger.debug('sample_bam: {0}'.format(sample_bam))

        # make the shell command to run
        command = self.gatk_DepthOfCoverage_cmd(sampleID = sample.id, bam_file = sample_bam, output_dir = self.output_dir, intervals_bed_file = targets_bed)
        self.logger.debug(command)

        # submit the command as a qsub job on the HPC
        job = self.qsub.submit(command = command, name = self.taskname + '.' + sample.id, stdout_log_dir = qsub_log_dir, stderr_log_dir = qsub_log_dir, verbose = True, sleeps = 1) #
        return(job)
