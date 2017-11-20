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
import _exceptions as _e

logger = logging.getLogger(__name__)

# path to the script's dir
scriptdir = os.path.dirname(os.path.realpath(__file__))
scriptname = os.path.basename(__file__)
script_timestamp = log.timestamp()

# ~~~~~ SETUP FUNCTIONS ~~~~~ #
def check_default_address(address, server, default_key = '__self__'):
    """
    Checks if the provided ``address`` matches the ``default_key``, and if so, returns a default email address made from the username of the user running the program + the ``server``.

    Parameters
    ----------
    address: str
        email address(es) in the format 'email1@server.com,email2@server.com'
    server: str
        email server to use for a default email address
    default_key: str
        value to use for recognizing when a default address should be returned

    Returns
    -------
    str
        either the original ``address`` string, or an email address composed of the user's system name + ``server``

    """
    if address == default_key:
        default_address = mutt.get_reply_to_address(server = server)
        return(default_address)
    else:
        return(address)


# ~~~~~ LOAD CONFIGS ~~~~~ #
configs = config.config

reply_to_server = configs['reply_to_server']

success_recipients = check_default_address(address = configs['success_recipients'], server = reply_to_server)
error_recipients = check_default_address(address = configs['error_recipients'], server = reply_to_server)
notification_recipients = check_default_address(address = configs['notification_recipients'], server = reply_to_server)
default_recipients = success_recipients

default_reply_to = mutt.get_reply_to_address(server = configs['reply_to_server'])

success_subject_line_base = configs['success_subject_line_base']
error_subject_line_base = configs['error_subject_line_base']
notification_subject_line_base = configs['notification_subject_line_base']

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
def sns_start_email(analysis_dir, **kwargs):
    """
    Emails the user when the sns pipeline starts

    Parameters
    ----------
    analysis_dir: str
        path to a directory to hold the analysis output
    kwargs: dict
        dictionary containing extra args to pass to `run_tasks`

    """
    recipient_list = kwargs.pop('recipient_list', notification_recipients)
    reply_to = kwargs.pop('reply_to', default_reply_to)
    subject_line = kwargs.pop('subject_line', notification_subject_line_base)

    subject_line = subject_line + ' sns analysis started'

    message = "sns analysis started in directory:\n{0}".format(analysis_dir)

    mail_command = mutt.mutt_mail(recipient_list = recipient_list,
                    reply_to = reply_to,
                    subject_line = subject_line,
                    message = message,
                    return_only_mode = True)
    run_cmd = tools.SubprocessCmd(command = mail_command).run()
    # print run command output messages
    logger.debug(run_cmd.proc_stdout)
    logger.debug(run_cmd.proc_stderr)


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
    subject_line = kwargs.pop('subject_line', success_subject_line_base)

    validate_email_files()

    logger.debug('email_files: {0}'.format(email_files))

    mail_command = mutt.mutt_mail(recipient_list = recipient_list,
                    reply_to = reply_to,
                    subject_line = subject_line,
                    message_file = message_file,
                    attachment_files = email_files,
                    return_only_mode = True)
    run_cmd = tools.SubprocessCmd(command = mail_command).run()
    # print run command output messages
    logger.debug(run_cmd.proc_stdout)
    logger.debug(run_cmd.proc_stderr)
    # check for success of the command
    if run_cmd.process.returncode != 0:
        err_message = 'The mutt email command did not complete successfully'
        raise _e.SubprocessCmdError(message = err_message, errors = '')
        # TODO: need a backup email function to run in case this gets raised
