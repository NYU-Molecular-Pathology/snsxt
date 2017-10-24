#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Module for the start_sns function to start a new analysis
'''
# ~~~~~ LOGGING ~~~~~~ #
import os
from util import tools as t
import logging
logger = logging.getLogger(__name__)


def start_sns(configs, **kwargs):
    '''
    Start a new sns wes pipeline analysis
    when finished, return the output_dir for use in the downstream processing

    sns/gather-fastqs /fastq_dir/
    sns/generate-settings hg19
    sns/run wes
    sns/run wes-pairs-snv
    '''
    logger.debug(configs)
    logger.debug(kwargs)

    fastq_dirs = kwargs.pop('fastq_dirs', [])
    output_dir = kwargs.pop('output_dir', None)

    if kwargs:
        raise TypeError('Unexpected **kwargs: %r' % kwargs)

    extra_handlers = configs.get('extra_handlers', [])

    return(output_dir)
