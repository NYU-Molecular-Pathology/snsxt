#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Functions for validating aspects of the pipeline
"""
# ~~~~~ LOGGING ~~~~~~ #
import os
from util import log
from util import tools
import logging
import _exceptions as _e

logger = logging.getLogger(__name__)

# ~~~~~ GLOBALS ~~~~~ #
# list to capture background output that should be validated after all jobs finish
background_output_files = []
"""
By default, a task will validated its expected output files upon task completion. However, tasks that submit qsub jobs and do not wait for them to complete will not be able to validate their expected output files. Instead, the paths to those expected files will be collected in this list, and they will be evaluated once all qsub jobs have been monitored to completion and validated.
"""


# ~~~~~ FUNCTIONS ~~~~~~ #
def validate_background_output_files():
    """
    Validates the global ``background_output_files`` list contents. 
    """
    if background_output_files:
        logger.debug('Background output files will be validated')
        validate_items(items = background_output_files)
    else:
        logger.debug('No background jobs were found for validation')

def validate_items(items):
    """
    Runs validations on a list of items

    Parameters
    ----------
    items: list
        a list of file or dir paths to be validated

    Todo
    ----
    Need to figure out what should be returned if no items were passed
    """
    logger.debug('validating {0} items'.format(len(items)))
    if len(items) < 1 or not items:
        logger.error('No items were passed')
        # TODO: what to return here??
        return()

    # make sure all files and dirs exist
    invalid_items = []
    for item in items:
        if not tools.item_exists(item):
            invalid_items.append(item)

    if invalid_items:
        raise _e.AnalysisFileMissing(message = 'Expected files did not exist:\n{0}'.format([item for item in invalid_items]), errors = '')
