#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re
import task_classes
from task_classes import MultiQsubSampleTask

class MuTect2Split(MultiQsubSampleTask):
    """
    Runs MuTect2 on every sample in the analysis, submitting one qsub job per chromosome
    """
    def __init__(self, analysis, taskname = 'MuTect2Split', config_file = 'MuTect2Split.yml', extra_handlers = None):
        """
        Parameters
        ----------
        analysis: SnsWESAnalysisOutput
            the `sns` pipeline output object to run the task on. If ``None`` is passed, ``self.analysis`` is retrieved instead.
        extra_handlers: list
            a list of extra Filehandlers to use for logging
        """
        MultiQsubSampleTask.__init__(self, taskname = taskname, config_file = config_file, analysis = analysis, extra_handlers = extra_handlers)

    def MuTect2_split_cmd(self, input_file_tumor, input_file_normal, intervals_file, output_file):
        """
        Creates a shell command to run for MuTect2

        Parameters
        ----------
        input_file: str
            path to the input file for MuTect2
        output_file: str
            path to the output file for MuTect2


        Notes
        -----
        An example MuTect2 shell command looks like this::

            java -Xms16G -Xmx16G -jar /software/GenomeAnalysisTK/GenomeAnalysisTK-3.6-0/GenomeAnalysisTK.jar -T MuTect2 \\
            -dt NONE  \\
            --logging_level WARN  \\
            --standard_min_confidence_threshold_for_calling 30  \\
            --max_alt_alleles_in_normal_count 10  \\
            --max_alt_allele_in_normal_fraction 0.05 \\
            --max_alt_alleles_in_normal_qscore_sum 40  \\
            --reference_sequence /ref/hg19/genome.fa  \\
            --dbsnp /ref/hg19/gatk-bundle/dbsnp_138.hg19.vcf  \\
            --cosmic /ref/hg19/CosmicCodingMuts_v73.hg19.vcf  \\
            --intervals /ifs/data/molecpathlab/NGS580_WES/NGS580_targets.bed  \\
            --interval_padding 10  \\
            --input_file:tumor SampleID-T.dd.ra.rc.bam  \\
            --input_file:normal SampleID-N.dd.ra.rc.bam  \\
            --out SampleID-T_SampleID-N.original.vcf

        """
        # get params from config
        GATK_bin = self.task_configs['bin']
        downsampling = self.task_configs['downsampling'] # -dt
        logging_level = self.task_configs['logging_level']
        standard_min_confidence_threshold_for_calling = self.task_configs['standard_min_confidence_threshold_for_calling']
        max_alt_alleles_in_normal_count = self.task_configs['max_alt_alleles_in_normal_count']
        max_alt_allele_in_normal_fraction = self.task_configs['max_alt_allele_in_normal_fraction']
        max_alt_alleles_in_normal_qscore_sum = self.task_configs['max_alt_alleles_in_normal_qscore_sum']
        reference_sequence = self.task_configs['reference_sequence']
        dbsnp = self.task_configs['dbsnp']
        cosmic = self.task_configs['cosmic']
        interval_padding = self.task_configs['interval_padding']

        mutect2_cmd = """
        java -Xms16G -Xmx16G -jar "{0}" -T MuTect2 \
        -dt "{1}"  \
        --logging_level "{2}"  \
        --standard_min_confidence_threshold_for_calling "{3}"  \
        --max_alt_alleles_in_normal_count "{4}"  \
        --max_alt_allele_in_normal_fraction "{5}" \
        --max_alt_alleles_in_normal_qscore_sum "{6}"  \
        --reference_sequence "{7}"  \
        --dbsnp "{8}"  \
        --cosmic "{9}"  \
        --intervals "{10}"  \
        --interval_padding "{11}"  \
        --input_file:tumor "{12}"  \
        --input_file:normal "{13}"  \
        --out "{14}"
        """.format(
        GATK_bin, # 0
        downsampling, # 1
        logging_level, # 2
        standard_min_confidence_threshold_for_calling, # 3
        max_alt_alleles_in_normal_count, # 4
        max_alt_allele_in_normal_fraction, # 5
        max_alt_alleles_in_normal_qscore_sum, # 6
        reference_sequence, # 7
        dbsnp, # 8
        cosmic, # 9
        intervals_file, # 10
        interval_padding, # 11
        input_file_tumor, # 12
        input_file_normal, # 13
        output_file # 14
        )

    def main(self, sample):
        """
        Run MuTect2 on a single sample, submitting one qsub job per chromosome in the targets.bed file

        Parameters
        ----------
        sample: SnsAnalysisSample
            a single sample from the analysis

        Returns
        -------
        list
            a list of qsub.Job objects
        """
        # self.logger.debug('Put your code for doing the analysis task in this function')
        # self.logger.debug('The global configs for all tasks will be in this dict: {0}'.format(self.main_configs))
        # self.logger.debug('The configs loaded from the task YAML file will be in this dict: {0}'.format(self.task_configs))

        self.logger.debug('Sample is: {0}'.format(sample.id))
        self.logger.debug(dir(sample))
        self.logger.debug(sample.static_files)


        # get the dir for the qsub logs
        qsub_log_dir = sample.list_none(sample.analysis_config['dirs']['logs-qsub'])
        # self.logger.debug('qsub_log_dir is: {0}'.format(qsub_log_dir))

        # get the path to the sample's .bam file
        sample_bam = self.get_sample_file_inputpath(sampleID = sample.id, suffix = self.input_suffix)
        # self.logger.debug('sample_bam is: {0}'.format(sample_bam))

        # get the path to the input targets .bed file
        targets_bed = sample.list_none(sample.get_files('targets_bed'))
        # self.logger.debug('targets_bed is: {0}'.format(targets_bed))

        # get the path to the targets split output directory to use
        targets_split_outdir = self.tools.mkdirs(path = os.path.join(self.output_dir, sample.id + '_targets_split'), return_path = True)
        # self.logger.debug('targets_split_outdir is: {0}'.format(targets_split_outdir))

        # get the paths to the output split targets files per chrom
        chrom_filenames = self.bed_chrom_split.make_bed_splitchrom_filenames(bed_file = targets_bed, output_dir = targets_split_outdir)
        # {'chr15': '/ifs/data/molecpathlab/snsxt-dev/example_runs/mini_analysis/VCF-MuTect2-Split/SeraCare-1to1-Positive_targets_split/targets_chr15.bed', ... }
        # self.logger.debug('chrom_filenames is: {0}'.format(chrom_filenames))

        # build a dict of the targets and output .vcf for each chrom
        output_targets_dict = {}
        for chrom in chrom_filenames.keys():
            output_targets_dict[chrom] = {}
            output_targets_dict[chrom]['targets'] = chrom_filenames[chrom]
            output_targets_dict[chrom]['output'] = os.path.join(self.output_dir, '{0}.{1}.vcf'.format(sample.id, chrom))
        # self.logger.debug('output_targets_dict is: {0}'.format(output_targets_dict))






        # make the shell command to run
        job_name = self.taskname + '.' + sample.id
        command = 'sleep 30'
        job1 = self.qsub.submit(command = command, name = "one" + job_name, stdout_log_dir = qsub_log_dir, stderr_log_dir = qsub_log_dir, verbose = True, sleeps = 1)
        job2 = self.qsub.submit(command = command, name = "two" + job_name, stdout_log_dir = qsub_log_dir, stderr_log_dir = qsub_log_dir, verbose = True, sleeps = 1)
        return([job1, job2])
