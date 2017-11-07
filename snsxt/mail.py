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
from util import tools
from util import mutt

logger = logging.getLogger(__name__)

# path to the script's dir
scriptdir = os.path.dirname(os.path.realpath(__file__))
scriptname = os.path.basename(__file__)
script_timestamp = log.timestamp()

# ~~~~~ LOAD CONFIGS ~~~~~ #
configs = config.config

default_recipients = configs['email_recipients']
default_reply_to = mutt.get_reply_to_address(server = configs['reply_to_server'])
default_subject_line_base = '[NGS580] Success'
error_subject_line_base = '[NGS580] Error'
error_recipients = mutt.get_reply_to_address(server = configs['reply_to_server'])

# list to hold files to send as attachments
# other modults should append to this
# TODO: is there a better way to handle this ??
email_files = []

# ~~~~ CUSTOM FUNCTIONS ~~~~~~ #
def email_error_output(message_file, *args, **kwargs):
    '''
    Email to send if an error occured
    '''
    email_output(message_file = message_file, subject_line = error_subject_line_base, recipient_list = error_recipients)

def email_output(message_file, *args, **kwargs):
    '''
    The default email output for the program
    '''
    recipient_list = kwargs.pop('recipient_list', default_recipients)
    reply_to = kwargs.pop('reply_to', default_reply_to)
    subject_line = kwargs.pop('subject_line', default_subject_line_base)
    recipient_list = kwargs.pop('recipient_list', default_recipients)

    logger.debug('email_files: {0}'.format(email_files))

    mail_command = mutt.mutt_mail(recipient_list = recipient_list,
                    reply_to = reply_to,
                    subject_line = subject_line,
                    message_file = message_file,
                    attachment_files = email_files,
                    return_only_mode = True)
    tools.SubprocessCmd(command = mail_command).run()
