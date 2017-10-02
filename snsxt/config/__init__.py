#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Configurations module

Developed and tested with Python 2.7
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
with open(os.path.join(scriptdir, "sns.yml"), "r") as f:
    sns = yaml.load(f)

with open(os.path.join(scriptdir, "snsxt.yml"), "r") as f:
    snsxt = yaml.load(f)

with open(os.path.join(scriptdir, "misc.yml"), "r") as f:
    misc = yaml.load(f)

with open(os.path.join(scriptdir, "NextSeq.yml"), "r") as f:
    NextSeq = yaml.load(f)


# logger.debug(sns)
# logger.debug(misc)
# logger.debug(NextSeq)
