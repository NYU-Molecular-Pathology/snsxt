#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sends email output of the pipeline results
"""
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
"""
This list should contain file paths output by analysis tasks for inclusion as email attachments at the end of a successful analysis pipeline. It should be accessed by other parts of the program external to this module

Examples
--------
Example usage::

    task_output_file = 'foo.txt'
    mail.email_files.append(task_output_file)

"""

# ~~~~ CUSTOM FUNCTIONS ~~~~~~ #
def validate_email_files():
    """
    Makes sure all the items in the ``email_files`` list exist and are considered valid for inclusion in email output

    Notes
    -----
    Since the email output is sent by an external program such as ``mutt``, it is important that file attachments be valid before attempting to include them, since it will be more difficult to ensure that the email is sent successfully.

    """
    for i, item in enumerate(email_files):
        if not tools.item_exists(item):
            logger.error('email file does not exist: {0}'.format(item))
            email_files.pop(i)

def email_error_output(message_file, *args, **kwargs):
    """
    Sends an email in the event that errors occurred during the analysis.

    Parameters
    ----------
    message_file: str
        path to a file to use as the body of the email, typically the program's log file

    Keyword Arguments
    -----------------
    subject_line: str
        the subject line that should be used for the email
    recipient_list: str
        the recipients for the email, in the format ``recipient_list = "user1@server.com,user2@server.com" ``

    """
    email_output(message_file = message_file, subject_line = error_subject_line_base, recipient_list = error_recipients)

def email_output(message_file, *args, **kwargs):
    """
    Sends an email upon the successful completion of the analysis pipeline. If any ``email_files`` were set by the program while running, they will be validated and included as email attachments.

    Parameters
    ----------
    message_file: str
        path to a file to use as the body of the email, typically the program's log file
    args: list
        a list containing extra args to pass to ``email_output()``
    kwargs: dict
        a dictionary containing extra args to pass to ``email_output()``

    Keyword Arguments
    -----------------
    recipient_list: str
        the recipients for the email, in the format ``recipient_list = "user1@server.com,user2@server.com" ``
    reply_to: str
        email address to use in the 'Reply To' field of the email
    subject_line: str
        the subject line that should be used for the email
    """
    recipient_list = kwargs.pop('recipient_list', default_recipients)
    reply_to = kwargs.pop('reply_to', default_reply_to)
    subject_line = kwargs.pop('subject_line', default_subject_line_base)

    validate_email_files()

    logger.debug('email_files: {0}'.format(email_files))

    mail_command = mutt.mutt_mail(recipient_list = recipient_list,
                    reply_to = reply_to,
                    subject_line = subject_line,
                    message_file = message_file,
                    attachment_files = email_files,
                    return_only_mode = True)
    tools.SubprocessCmd(command = mail_command).run()
