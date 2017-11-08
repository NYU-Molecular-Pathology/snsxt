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


# ~~~~~ FUNCTIONS ~~~~~~ #

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
