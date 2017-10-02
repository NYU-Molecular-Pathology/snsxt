#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Configurations module

Developed and tested with Python 2.7
'''
# ~~~~~ LOGGING ~~~~~~ #
import logging
logger = logging.getLogger("config")
logger.debug("loading sns_tasks config module")

# ~~~~~ SETUP ~~~~~~ #
import yaml
import os

scriptdir = os.path.dirname(os.path.realpath(__file__))

logger.debug("loading configurations...")

with open(os.path.join(scriptdir, 'Delly2.yml'), "r") as f:
    Delly2 = yaml.load(f)

with open(os.path.join(scriptdir, 'GATK_DepthOfCoverage_custom.yml'), "r") as f:
    GATK_DepthOfCoverage_custom = yaml.load(f)


# logger.debug(Delly2)
# logger.debug(GATK_DepthOfCoverage_custom)
