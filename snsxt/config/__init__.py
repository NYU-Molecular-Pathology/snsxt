#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Module to load all of the individual config files
Set up internal config dictionary for use throughout the program
do any config re-mapping & aggregation here
'''
# ~~~~~ LOGGING ~~~~~~ #
import logging
logger = logging.getLogger("config")
logger.debug("loading config module")

# ~~~~~ SETUP ~~~~~~ #
import yaml
import os

# path to this file's dir
scriptdir = os.path.dirname(os.path.realpath(__file__))

logger.debug("loading configurations...")

# ~~~~ GET EXTERNAL CONFIGS ~~~~~~ #
with open(os.path.join(scriptdir, "sns.yml"), "r") as f:
    sns = yaml.load(f)

with open(os.path.join(scriptdir, "snsxt.yml"), "r") as f:
    snsxt = yaml.load(f)

with open(os.path.join(scriptdir, "misc.yml"), "r") as f:
    misc = yaml.load(f)

with open(os.path.join(scriptdir, "NextSeq.yml"), "r") as f:
    NextSeq = yaml.load(f)


# ~~~~ CREATE INTERNAL CONFIGS ~~~~~~ #
config = {}

config['analysis_output_index'] = sns['analysis_output_index']

# email
config['email_recipients'] = snsxt['email_recipients']
config['mail_files'] = snsxt['mail_files']


# report
config['report_dir'] = snsxt['report_dir']
config['report_files'] = snsxt['report_files']
config['main_report'] = snsxt['main_report']
config['report_compile_script'] = snsxt['report_compile_script']
config['analysis_id_file'] = snsxt['analysis_id_file']
config['results_id_file'] = snsxt['results_id_file']
