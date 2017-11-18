#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module to load all of the individual config files
Set up internal config dictionary for use throughout the program
do any config re-mapping & aggregation here
"""
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
with open(os.path.join(scriptdir, "snsxt.yml"), "r") as f:
    snsxt = yaml.load(f)


# ~~~~ CREATE INTERNAL CONFIGS ~~~~~~ #
config = {}

config.update(snsxt)
