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
from classes import AnalysisItem
from classes import SnsAnalysisSample
from classes import SnsWESAnalysisOutput


# ~~~~ CUSTOM FUNCTIONS ~~~~~~ #
def run_delly2():
    '''
    Run Delly2 on a sample
    '''

def main():
    '''
    Main control function for the program
    '''
    analysis_id = "170623_NB501073_0015_AHY5Y3BGX2"
    results_id = "results_2017-06-26_20-11-26"
    results_dir = "results_dir"
    x = SnsWESAnalysisOutput(dir = results_dir, id = analysis_id, results_id = results_id)
    print(x)
    print(x.get_files(name = 'paired_samples'))
    print(x.get_files(name = 'samples_fastq_raw'))
    print(x.get_files(name = 'summary_combined_wes'))
    print(x.get_files(name = 'settings'))
    print(x.get_files(name = 'targets_bed'))




    # print(x.list_none(find.find(search_dir = x.dir, pattern = "*.foood", search_type = 'file', num_limit = 1, level_limit = None)))
    # print(x.paired_samples_file)
    # print(x.samples_fastq_raw_file)
    # print(x.summary_combined_wes_file)
    # print(x.settings_file)
    # print(x.targets_bed_file)
    # print(x.sample_list)

def run():
    '''
    Run the monitoring program
    arg parsing goes here, if program was run as a script
    '''
    main()

if __name__ == "__main__":
    run()
