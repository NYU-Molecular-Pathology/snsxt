#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Run a series of analysis tasks, as an extension to the sns pipeline output

tested under Python 2.7
'''

# ~~~~ LOAD PACKAGES ~~~~~~ #
# system modules
import os
import sys
import csv

# this program's modules
import find
from classes import AnalysisItem
from classes import SnsAnalysisSample
from classes import SnsWESAnalysisOutput


# ~~~~ CUSTOM FUNCTIONS ~~~~~~ #
def run_delly2():
    '''
    Run Delly2 on a sample
    '''

def demo():
    '''
    Run a demo of the program
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
    print(x.samples)

def main():
    '''
    Main control function for the program
    '''
    demo()


def run():
    '''
    Run the monitoring program
    arg parsing goes here, if program was run as a script
    '''
    main()

if __name__ == "__main__":
    run()
