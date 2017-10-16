#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Set up the configs for the 'run.py' script here, so they can also be accessed
by other submodules
do any config re-mapping & aggregation here
'''
# ~~~~ GET EXTERNAL CONFIGS ~~~~~~ #
import config
email_recipients = config.snsxt['email_recipients']
analysis_output_index = config.sns['analysis_output_index']


# ~~~~ CREATE INTERNAL CONFIGS ~~~~~~ #
sns_config = {}
sns_config['email_recipients'] = email_recipients
sns_config['analysis_output_index'] = analysis_output_index

sns_config['report_dir'] = config.snsxt['report_dir']
sns_config['report_files'] = config.snsxt['report_files']
sns_config['main_report'] = config.snsxt['main_report']
sns_config['report_compile_script'] = config.snsxt['report_compile_script']
sns_config['analysis_id_file'] = config.snsxt['analysis_id_file']
sns_config['results_id_file'] = config.snsxt['results_id_file']
