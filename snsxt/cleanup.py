#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Functions for cleaning up after an analysis is finished
"""
# ~~~~~ LOGGING ~~~~~~ #
import os
import sys
import shutil
import yaml
from util import tools
import logging
import config

logger = logging.getLogger(__name__)


# ~~~~~ LOAD CONFIGS ~~~~~ #
configs = config.config


# ~~~~ CUSTOM FUNCTIONS ~~~~~~ #
def save_configs(analysis_dir):
    """
    Saves the global ``configs`` object to a YAML file in the analysis dir

    Parameters
    ----------
    analysis_dir: str
        path to a directory to hold the analysis output

    Notes
    -----
    Some config items are added or modified during program run time, so final configs may not exactly match starting configs set in external config YAML files

    """
    # save the configs to a YAML file
    output_config_yaml = os.path.join(analysis_dir, 'snsxt_config.yml')
    logger.debug('Saving program configs to file: {0}'.format(output_config_yaml))
    with open(output_config_yaml, 'w') as outfile:
        yaml.dump(configs, outfile, default_flow_style = False)

def analysis_complete(analysis):
    """
    Actions to take after an analysis is done

    Parameters
    ----------
    analysis: SnsWESAnalysisOutput
        object representing output from an `sns wes` analysis pipeline output on which to run downstream analysis tasks

    """
    analysis_dir = analysis.dir
    save_configs(analysis_dir)
