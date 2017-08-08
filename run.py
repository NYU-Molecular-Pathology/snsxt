#!/usr/bin/env python
# tested under Python 2.7

'''
Template Python script
'''

# ~~~~ LOAD PACKAGES ~~~~~~ #
import os
import sys
import csv

import find


# ~~~~ CUSTOM CLASSES ~~~~~~ #
class SnsAnalysisSample(object):
    '''
    Container for metadata about a sample in the sns WES targeted exome sequencing run analysis output
    '''
    def __init__(self, id):
        self.id = str(id)
        self.search_pattern = '{0}*'.format(self.id)
    def __repr__(self):
        return(self.id)
    def __str__(self):
        return(self.id)
    def __len__(self):
        return(len(self.id))


class SnsWESAnalysisOutput(object):
    '''
    Container for metadata about a sns WES targeted exome sequencing run analysis
    '''
    def __init__(self, dir, id, results_id = None):
        # path to the directory containing analysis output
        self.dir = os.path.abspath(dir)
        # ID for the analysis run output; should match NextSeq ID
        self.id = str(id)
        # timestamped ID for the analysis results
        self.results_id = results_id
        # samplesheet file with the run's paired samples
        self.paired_samples_file = self.list_none(find.find(search_dir = self.dir, pattern = "samples.pairs.csv", search_type = 'file', num_limit = 1))
        # file with the original starting .fastq file paths & id's
        self.samples_fastq_raw_file = self.list_none(find.find(search_dir = self.dir, pattern = "samples.fastq-raw.csv", search_type = 'file', num_limit = 1))
        # summary table produced at the end of the WES pipeline
        self.summary_combined_wes_file = self.list_none(find.find(search_dir = self.dir, pattern = "summary-combined.wes.csv", search_type = 'file', num_limit = 1))
        # file with settings for the analysis
        self.settings_file = self.list_none(find.find(search_dir = self.dir, pattern = "settings.txt", search_type = 'file', num_limit = 1))

        self.sample_list = self.get_sample_list()

        # the .bed file with the chromosome target regions
        # TODO: need find exclusion filter to keep from picking up '.pad10.bed'
        # https://codereview.stackexchange.com/questions/74713/filtering-with-multiple-inclusion-and-exclusion-patterns
        # self.targets_bed_file = self.list_none(find.find(search_dir = self.dir, pattern = "*.bed", search_type = 'file', num_limit = 1, level_limit = None))

    def list_none(self, l):
        '''
        return None for an empty list, or the first element of a list if present
        '''
        if len(l) == 0:
            return(None)
        elif len(l) == 1:
            return(l[0])
        else:
            return(l)

    def get_sample_list(self):
        '''
        Get a list of samples in the run from the samples_fastq_raw_file
        '''
        samples = []
        with open(self.samples_fastq_raw_file, "rb") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                samples.append(row[0])
        samples = [SnsAnalysisSample(x) for x in set(samples)]
        return(samples)

    def __repr__(self):
        return("SnsWESAnalysisOutput {0} ({1})\nlocated at {2}".format(self.id, self.results_id, self.dir))



# ~~~~ CUSTOM FUNCTIONS ~~~~~~ #
def main():
    '''
    Main control function for the program
    '''
    analysis_id = "170623_NB501073_0015_AHY5Y3BGX2"
    results_id = "results_2017-06-26_20-11-26"
    results_dir = "results_dir"
    x = SnsWESAnalysisOutput(dir = results_dir, id = analysis_id, results_id = results_id)
    print(x)

    print(x.list_none(find.find(search_dir = x.dir, pattern = "*.foood", search_type = 'file', num_limit = 1, level_limit = None)))

    # print(x.paired_samples_file)
    # print(x.samples_fastq_raw_file)
    # print(x.summary_combined_wes_file)
    # print(x.settings_file)
    # print(x.targets_bed_file)
    print(x.sample_list)

def run():
    '''
    Run the monitoring program
    arg parsing goes here, if program was run as a script
    '''
    main()

if __name__ == "__main__":
    run()
