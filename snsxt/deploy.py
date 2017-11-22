#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script for preparing a new snsxt analysis directory
"""
# ~~~~~ LOGGING ~~~~~~ #
import os
from util import log
# path to this script's dir
scriptdir = os.path.dirname(os.path.realpath(__file__))
# name of this script
scriptname = os.path.basename(__file__)
script_timestamp = log.timestamp()
# path to parent dir 2 levels above this script
snsxt_parent_dir = os.path.realpath(os.path.dirname(os.path.dirname(__file__)) )
# /ifs/data/molecpathlab/scripts/snsxt/

# set a timestamped log file for debug log
log_file = os.path.join(snsxt_parent_dir, 'logs', '{0}.{1}.log'.format(scriptname, script_timestamp))
email_log_file = os.path.join(snsxt_parent_dir, 'logs', '{0}.{1}.email.log'.format(scriptname, script_timestamp))

# logging config files
primary_config_yaml = os.path.join(scriptdir, 'logging.yml')
backup_config_yaml = os.path.join(scriptdir, "basic_logging.yml")

# set  log module objects
log.log_file = log_file
log.email_log_file = email_log_file

logpath = log._logpath
"""
Bound function from ``log`` module
"""

email_logpath = log._email_logpath
"""
Bound function from ``log`` module
"""
logger = log.logger_from_configs(name = __name__, primary_config_yaml = primary_config_yaml, backup_config_yaml = backup_config_yaml, logger_name = 'deploy')

logger.debug("Hi")
