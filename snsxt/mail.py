#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Functions to send email output of the pipeline results
'''
# ~~~~~ LOGGING ~~~~~~ #
import os
import shutil
from util import log
import logging
import run_config
from util import tools as t

logger = logging.getLogger(__name__)

# path to the script's dir
scriptdir = os.path.dirname(os.path.realpath(__file__))
scriptname = os.path.basename(__file__)
script_timestamp = log.timestamp()
