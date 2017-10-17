#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Module to send email output of the pipeline results
'''
# ~~~~~ LOGGING ~~~~~~ #
import os
import shutil
from util import log
import logging
import config
from util import tools as t

logger = logging.getLogger(__name__)

# path to the script's dir
scriptdir = os.path.dirname(os.path.realpath(__file__))
scriptname = os.path.basename(__file__)
script_timestamp = log.timestamp()

# ~~~~~ LOAD CONFIGS ~~~~~ #
configs = config.config


# ~~~~ CUSTOM FUNCTIONS ~~~~~~ #




# ~~~~ NOTES ~~~~~~ #

# function from lyz for email
# def email_results(self):
#     '''
#     Send an email using the object's INFO log as the body of the message
#     '''
#     email_recipients = self.email_recipients
#     email_subject_line = self.email_subject_line
#     reply_to = self.reply_to
#     message_file = log.logger_filepath(logger = self.logger, handler_name = 'emaillog')
#
#     email_command = mutt.mutt_mail(recipient_list = email_recipients, reply_to = reply_to, subject_line = email_subject_line, message = 'This message should have been replaced by the script log file contents. If you are reading it, something broke, sorry', message_file = message_file, return_only_mode = True, quiet = True)
#
#     self.logger.debug('Email command is:\n\n{0}\n\n'.format(email_command))
#     mutt.subprocess_cmd(command = email_command)
#
# def get_reply_to_address(self, server):
#     '''
#     Get the email address to use for the 'reply to' field in the email
#     '''
#     username = getpass.getuser()
#     address = username + '@' + server
#     return(address)



# ~~~~ RUN ~~~~~~ #
def email_analysis_results(analysis, analysis_id = None, results_id = None):
    '''
    Send an email with analysis results
    '''
    analysis_dir = analysis.dir
