#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import csv
from task_classes import MultiQsubSampleTask

class MuTect2Split(MultiQsubSampleTask):
    """
    Runs MuTect2 on every tumor-normal sample pair in the analysis, submitting one qsub job per chromosome per pair
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

    def get_samle_bam_file(self, sampleID, file_suffix, input_dir):
        """
        Gets the file path to a .bam file, given its sample ID
        """
        # path = self.get_path(dirpath = self.input_dir, file_basename = file_basename, validate = validate)
        # self.get_path(dirpath = self.output_dir, file_basename = file_basename, validate = False)
        path = os.path.join(input_dir, sampleID + file_suffix)
        self.validate_items([path])
        return(path)

    def find_sample_tumor_normal_pairs(self, sampleID, sampleIDs, pairs_sheet):
        """
        Parses the 'samples.pairs.csv' file to determine if the sample has any tumor-normal pairs. Assumes that the sample is the tumor, and must have a matched non-NA sample entry corresponding to another sample in the analysis

        Parameters
        ----------
        sampleID: str
            sample ID for the sample to find tumor-normal pairs for
        pairs_sheet: str
            path to the 'samples.pairs.csv' sheet
        sampleIDs: list
            a list of the sample ID's for all samples in the analysis; if ``None``, they will be retrieved from ``self.analysis``

        Returns
        -------
        list
            a list of dictionaries representing tumor-normal sample pairs

        Examples
        --------
        Example output::

            [{'#SAMPLE-N': 'Sample1-N', '#SAMPLE-T': 'Sample1-T'}]

        """
        # read in as a list of dicts
        with open(pairs_sheet) as f:
            reader = csv.DictReader(f)
            entries = [row for row in reader]

        # make a list to hold tumor - normal pairs with the given sample
        comparisons = []
        for entry in entries:
            if entry['#SAMPLE-T'] == sampleID:
                comparisons.append(entry)

        # remove entries with 'NA' as one of the ID's
        non_NA_comparisons = []
        for items in comparisons:
            if 'NA' not in items.values():
                non_NA_comparisons.append(items)

        # make sure that the normal sample is actually in the analysis sampleIDs
        valid_comparisons = []
        for items in non_NA_comparisons:
            if items['#SAMPLE-N'] in sampleIDs:
                valid_comparisons.append(items)

        return(valid_comparisons)

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

        Notes
        -----
        Calls back to ``self.analysis`` in order to get the other samples for paired analysis
        """
        # self.logger.debug('Put your code for doing the analysis task in this function')
        # self.logger.debug('The global configs for all tasks will be in this dict: {0}'.format(self.main_configs))
        # self.logger.debug('The configs loaded from the task YAML file will be in this dict: {0}'.format(self.task_configs))

        self.logger.debug('Sample is: {0}'.format(sample.id))

        input_dir = self.input_dir
        input_suffix = self.task_configs['input_suffix']

        # get the path to the 'samples.pairs.csv' sheet
        pairs_sheet = sample.static_files['paired_samples']
        # self.logger.debug('pairs_sheet is: {0}'.format(pairs_sheet))

        # get list of all sample IDs in the analysis
        sampleIDs = [s.id for s in self.analysis.get_samples() ]

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

        # for chrom in chrom_filenames.keys():
        #     output_targets_dict[chrom] = {}
        #     output_targets_dict[chrom]['targets'] = chrom_filenames[chrom]
        #     output_targets_dict[chrom]['output'] = os.path.join(self.output_dir, '{0}.{1}.vcf'.format(sample.id, chrom))
        # self.logger.debug('output_targets_dict is: {0}'.format(output_targets_dict))

        # get the tumor-normal comparisons from the pairs sheet for the sample
        tumor_normal_pairs = self.find_sample_tumor_normal_pairs(sampleID = sample.id, sampleIDs = sampleIDs, pairs_sheet = pairs_sheet)
        self.logger.debug('tumor_normal_pairs is: {0}'.format(tumor_normal_pairs))
        # tumor_normal_pairs is: [{'#SAMPLE-N': 'HapMap-B17-1267', '#SAMPLE-T': 'SeraCare-1to1-Positive'}]

        if not tumor_normal_pairs:
            # return an empty list if there are no comparisons; default output is a list of jobs
            return([])

        if tumor_normal_pairs:
            # make a dictionary with the targets, input_file_tumor, and input_file_normal paths
            input_output_targets = {}
            for comparisons in tumor_normal_pairs:
                # get the sample IDs for the tumor and normal, and the comparison
                tumor_ID = comparisons['#SAMPLE-T'] # 'SeraCare-1to1-Positive'
                normal_ID = comparisons['#SAMPLE-N'] # 'HapMap-B17-1267'
                comparison_ID = tumor_ID + '_' + normal_ID # SeraCare-1to1-Positive_HapMap-B17-1267

                # get the .bam files for them
                tumor_bam = self.get_samle_bam_file(sampleID = tumor_ID, file_suffix = input_suffix, input_dir = input_dir)
                normal_bam = self.get_samle_bam_file(sampleID = normal_ID, file_suffix = input_suffix, input_dir = input_dir)

                # make sure .bam.bai files also exist...
                tumor_bai = tumor_bam + '.bai'
                normal_bai = normal_bam + '.bai'
                self.validate_items([tumor_bai, normal_bai])

                # add in the chrom targets..
                for chrom, targets_file in chrom_filenames.items():
                    tumor_normal_chrom_ID = comparison_ID + '_' + chrom

                    # make a subdict entry
                    input_output_targets[tumor_normal_chrom_ID] = {}
                    input_output_targets[tumor_normal_chrom_ID]['targets_file'] = targets_file
                    input_output_targets[tumor_normal_chrom_ID]['tumor_bam'] = tumor_bam
                    input_output_targets[tumor_normal_chrom_ID]['normal_bam'] = normal_bam
        self.logger.debug('input_output_targets is:\n{0}'.format(input_output_targets))










        # make the shell command to run
        job_name = self.taskname + '.' + sample.id
        command = 'sleep 30'
        job1 = self.qsub.submit(command = command, name = "one" + job_name, stdout_log_dir = qsub_log_dir, stderr_log_dir = qsub_log_dir, verbose = True, sleeps = 1)
        job2 = self.qsub.submit(command = command, name = "two" + job_name, stdout_log_dir = qsub_log_dir, stderr_log_dir = qsub_log_dir, verbose = True, sleeps = 1)
        return([job1, job2])
