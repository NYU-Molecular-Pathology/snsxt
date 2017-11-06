#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Custom exceptions to use in the program to trigger custom actions in case of error
'''
# ~~~~~ LOGGING ~~~~~~ #
import os
import sys
import logging
logger = logging.getLogger(__name__)

# ~~~~~ EXCEPTIONS ~~~~~ #
class AnalysisInvalid(Exception):
    '''
    Base exception to use if the analysis is invalid
    '''
    def __init__(self, message, errors):
        super(AnalysisInvalid, self).__init__(message)
        self.errors = errors

class AnalysisFileMissing(Exception):
    '''
    Base exception to use if a file needed for the analysis is missing
    '''
    def __init__(self, message, errors):
        super(AnalysisFileMissing, self).__init__(message)
        self.errors = errors

class InputFileMissing(AnalysisFileMissing):
    '''
    A file needed as input for an analysis task is missing
    '''
    def __init__(self, message, errors):
        super(InputFileMissing, self).__init__(message, errors)
        self.errors = errors

class OutputFileMissing(AnalysisFileMissing):
    '''
    A file expected to be produced by an analysis task is missing
    '''
    def __init__(self, message, errors):
        super(OutputFileMissing, self).__init__(message, errors)
        self.errors = errors

class ComputeJobInvalid(Exception):
    '''
    Base exception to use if an HPC cluster qsub job is invalid
    '''
    def __init__(self, message, errors):
        super(ComputeJobInvalid, self).__init__(message)
        self.errors = errors
