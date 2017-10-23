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

sns_tasks_file = os.path.join(scriptdir, 'sns_tasks.yml')
with open(sns_tasks_file, "r") as f:
    sns_tasks = yaml.load(f)

Delly2_file = os.path.join(scriptdir, 'Delly2.yml')
with open(Delly2_file, "r") as f:
    Delly2 = yaml.load(f)

GATK_DepthOfCoverage_custom_file = os.path.join(scriptdir, 'GATK_DepthOfCoverage_custom.yml')
with open(GATK_DepthOfCoverage_custom_file, "r") as f:
    GATK_DepthOfCoverage_custom = yaml.load(f)

Summary_Avg_Coverage_file = os.path.join(scriptdir, 'Summary_Avg_Coverage.yml')
with open(Summary_Avg_Coverage_file, "r") as f:
    Summary_Avg_Coverage = yaml.load(f)

Annotation_inplace_file = os.path.join(scriptdir, 'Annotation_inplace.yml')
with open(Annotation_inplace_file, "r") as f:
    Annotation_inplace = yaml.load(f)

HapMap_variant_ref_file = os.path.join(scriptdir, 'HapMap_variant_ref.yml')
with open(HapMap_variant_ref_file, "r") as f:
    HapMap_variant_ref = yaml.load(f)



# logger.debug(Delly2)
# logger.debug(GATK_DepthOfCoverage_custom)
