#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Configurations module
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

with open(os.path.join(scriptdir, 'sns_tasks.yml'), "r") as f:
    sns_tasks = yaml.load(f)

with open(os.path.join(scriptdir, 'Delly2.yml'), "r") as f:
    Delly2 = yaml.load(f)

with open(os.path.join(scriptdir, 'GATK_DepthOfCoverage_custom.yml'), "r") as f:
    GATK_DepthOfCoverage_custom = yaml.load(f)

with open(os.path.join(scriptdir, 'Summary_Avg_Coverage.yml'), "r") as f:
    Summary_Avg_Coverage = yaml.load(f)

with open(os.path.join(scriptdir, 'Annotation_inplace.yml'), "r") as f:
    Annotation_inplace = yaml.load(f)



# logger.debug(Delly2)
# logger.debug(GATK_DepthOfCoverage_custom)
