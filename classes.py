#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
General utility classes for the program
'''
import os
import sys
import csv
from collections import defaultdict

import find
import log
import tools
import config

# ~~~~ CUSTOM CLASSES ~~~~~~ #
class AnalysisItem(object):
    '''
    Base class for objects associated with an sns sequencing analysis
    '''
    def __init__(self):
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
    def __init__(self, dir, id, results_id = None, extra_handlers = None):
        '''
        Initialize the object

        extra_filehandlers = None or a list of handlers to add
        '''
        AnalysisItem.__init__(self)
        # ID for the analysis run output; should match NextSeq ID
        self.id = str(id)

        # set up per-analysis logger
        self.logger = log.build_logger(name = self.id)
        self.extra_handlers = extra_handlers
        if self.extra_handlers:
            self.logger = log.add_handlers(logger = self.logger, handlers = extra_handlers)
        self.logger.debug("Initialized logging for analysis: {0}".format(self.id))

        # ~~~~ FIND ANALYSIS ITEMS ~~~~~~ #
        # path to the directory containing analysis output
        self.dir = os.path.abspath(dir)

        # timestamped ID for the analysis results
        self.results_id = results_id

        # list of dirnames and filename patterns for the output steps in the sns WES analysis output
        self.analysis_output_index = {
        'analysis_output_index':{
        'BAM-BWA': {'file_types': ['.bam','.bam.bai']},
        'BAM-DD': {'file_types': ['.dd.bam', '.dd.bam.bai']},
        'BAM-GATK-RA': {'file_types': []},
        'BAM-GATK-RA-RC': {'file_types': ['.dd.ra.rc.bam', '.dd.ra.rc.bam.bai']},
        'FASTQ-CLEAN': {'file_types': ['.fastq.gz']},
        'FASTQ-TRIMMED': {'file_types': ['.trim.fastq.gz']},
        'QC-coverage': {'file_types': ['.sample_summary', '.sample_cumulative_coverage_counts', '.sample_cumulative_coverage_proportions', '.sample_interval_summary', '.sample_summary']},
        'QC-fragment-sizes': {'file_types': ['.freq.csv', '.png', '.stats.csv']},
        'QC-target-reads': {'file_types': ['.bed.sample_statistics', '.bed.sample_summary', '.genome.sample_statistics', '.genome.sample_summary', '.pad100.sample_statistics', '.pad100.sample_summary', '.pad500.sample_statistics', '.pad500.sample_summary']},
        'VCF-GATK-HC': {'file_types': ['.original.vcf', '.original.vcf.idx', '.vcf']},
        'VCF-GATK-HC-annot': {'file_types': ['.combined.txt', '.hg19_multianno.txt', '.vcf.txt']},
        'VCF-LoFreq': {'file_types': ['.original.vcf', '.original.vcf.bgz', '.original.vcf.bgz.csi', '.vcf']},
        'VCF-LoFreq-annot': {'file_types': ['.combined.txt', '.hg19_multianno.txt', '.vcf.txt']},
        'VCF-MuTect2': {'file_types': ['.original.vcf', '.original.vcf.idx', '.vcf']},
        'VCF-MuTect2-annot': {'file_types': ['.combined.txt', '.hg19_multianno.txt', '.vcf.txt']},
        'logs-align-bwa-mem': {'file_types': ['.flagstat.txt']},
        'logs-bam-dedup-sambamba': {'file_types': ['.flagstat.txt', '.log.txt']},
        'logs-bam-ra-rc-gatk': {'file_types': ['.csv', '.pdf']},
        'logs-qsub': {'file_patterns': ['.o*']},
        'logs-trimmomatic': {'file_types': ['.txt']},
        'sns': {},
        'summary': {'file_types': ['.VCF-GATK-HC-annot.csv', '.VCF-LoFreq-annot.csv', '.align-bwa-mem.csv', '.bam-dedup-sambamba.csv', '.fastq-clean.csv', '.fastq-trim-trimmomatic.csv', '.qc-coverage-gatk.csv', '.qc-fragment-sizes.csv', '.qc-target-reads-gatk.csv'], 'file_patterns': ['*:*.VCF-MuTect2-annot.csv']}
        }
        }
        self.analysis_output_index = config.sns['analysis_output_index']

        # self.set_dir(name = 'VCF-GATK-HC', path = find.find(search_dir = self.dir, inclusion_patterns = "VCF-GATK-HC", search_type = "dir", level_limit = 0))
        for name, attributes in self.analysis_output_index.items():
            self.set_dir(name = name, path = find.find(search_dir = self.dir, inclusion_patterns = name, search_type = "dir", level_limit = 0))

        # SINGLE FILES
        # samplesheet file with the run's paired samples
        self.set_file(name = 'paired_samples', path = find.find(search_dir = self.dir, inclusion_patterns = "samples.pairs.csv", search_type = 'file', num_limit = 1, level_limit = 0))

        # file with the original starting .fastq file paths & id's
        self.set_file(name = 'samples_fastq_raw', path = find.find(search_dir = self.dir, inclusion_patterns = "samples.fastq-raw.csv", search_type = 'file', num_limit = 1, level_limit = 0))

        # summary table produced at the end of the WES pipeline
        self.set_file(name = 'summary_combined_wes', path = find.find(search_dir = self.dir, inclusion_patterns = "summary-combined.wes.csv", search_type = 'file', num_limit = 1, level_limit = 0))

        # file with settings for the analysis
        self.set_file(name = 'settings', path = find.find(search_dir = self.dir, inclusion_patterns = "settings.txt", search_type = 'file', num_limit = 1, level_limit = 0))

        # the .bed file with the chromosome target regions
        self.set_file(name = 'targets_bed', path = find.find(search_dir = self.dir, inclusion_patterns = "*.bed", exclusion_patterns = '*.pad10.bed', search_type = 'file', num_limit = 1, level_limit = 0))




        # get the samples for the analysis
        self.samples = self.get_samples()


    def get_samples(self):
        '''
        Get the samples in the run from the samples_fastq_raw file
        '''
        self.logger.debug("Getting samples for the analysis")
        samples = []
        samples_fastq_raw_file = self.list_none(self.get_files(name = 'samples_fastq_raw'))
        if samples_fastq_raw_file:
            with open(samples_fastq_raw_file, "rb") as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    samples.append(row[0])
            samples = [SnsAnalysisSample(x, extra_handlers = self.extra_handlers) for x in set(samples)]
        return(samples)

    def __repr__(self):
        return("SnsWESAnalysisOutput {0} ({1})\nlocated at {2}".format(self.id, self.results_id, self.dir))



class SnsAnalysisSample(AnalysisItem):
    '''
    Container for metadata about a sample in the sns WES targeted exome sequencing run analysis output
    '''

    def __init__(self, id, extra_handlers = None):
        AnalysisItem.__init__(self)
        self.id = str(id)
        # set up per-sample logger
        self.logger = log.build_logger(name = self.id)
        if extra_handlers:
            self.logger = log.add_handlers(logger = self.logger, handlers = extra_handlers)
        self.logger.debug("Initialized logging for sample: {0}".format(self.id))

        # file matching pattern based on the sample's id
        self.search_pattern = '{0}*'.format(self.id)

    def __repr__(self):
        return(self.id)
    def __str__(self):
        return(self.id)
    def __len__(self):
        return(len(self.id))
