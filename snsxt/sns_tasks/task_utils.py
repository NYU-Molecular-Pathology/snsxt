#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Module for functions and classes to be used by all sns_task submodules
'''
# ~~~~~ LOGGING ~~~~~~ #
import logging

# ~~~~ LOAD MORE PACKAGES ~~~~~~ #
import os
import sys
import csv
import shutil



def get_report_files(configs):
    '''
    Get the files for the report based on the configs, return a list
    '''
    report_files = []
    report_dir = os.path.join(configs['script_dir'], configs['report_dir'])
    for item in configs['report_files']:
        file_path = os.path.join(report_dir, item)
        report_files.append(file_path)
    return(report_files)

def setup_report(output_dir, configs):
    '''
    Set up the report files output for the pipeline step
    by copying over every associated file for the report to the output dir
    '''
    report_files = get_report_files(configs)
    logger.debug("Report files are: {0}".format(report_files))
    for item in report_files:
        output_file = os.path.join(output_dir, os.path.basename(item))
        logger.debug("Copying report file '{0}' to '{1}' ".format(item, output_file))
        shutil.copy2(item, output_file)
