#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A demo custom SnsTask
"""
import os
from task_classes import SnsTask

class SnsValidate(SnsTask):
    """
    Run the sns wes analysis pipeline for unpaired variant calling on exome data
    """
    def __init__(self, analysis_dir, taskname = 'SnsValidate', extra_handlers = None, **kwargs):
        """
        """
        SnsTask.__init__(self, analysis_dir = analysis_dir, taskname = taskname, extra_handlers = extra_handlers)

    def get_qsub_logfiles(self, log_dirname = 'logs-qsub'):
        """
        Gets the list of log files from the analysis' qsub logs directory

        Parameters
        ----------
        log_dirname: str
            the path to the qsub log directory. If ``None``, a directory called ``logs-qsub`` will be searched for in the analysis output directory and used instead

        Returns
        -------
        list
            a list of file paths to qsub logs

        """
        log_files = []

        # path to the qsub logs dir
        qsub_logdir = os.path.join(self.analysis_dir, log_dirname)
        # make sure it exists
        if not self.tools.item_exists(item = qsub_logdir, item_type = 'dir'):
            raise self._exceptions.AnalysisFileMissing(message = 'Qsub log directory for {0} does not exist:\n{1}'.format(self, qsub_logdir), errors = '')

        # get all the files in the log dir
        for item in self.find.find(qsub_logdir, search_type = 'file'):
            log_files.append(item)
        return(log_files)

    def check_qsub_log_errors_present(self, log_files = None, err_patterns = ("ERROR:",)):
        """
        Checks the qsub log files for errors, by searching for lines that include known 'error' patterns

        Parameters
        ----------
        log_files: list
            a list of paths to qsub log files
        err_patterns: tuple
            an iterable object containing string error matching patterns to look for in the log files, indicating that an error occured

        Returns
        -------
        bool
            ``True`` or ``False`` whether or not errors are detected in the qsub log files. If ``True``, the paths to files with error messages will be printed in the log.
        """
        contains_errors = {}
        # try to find the log files from self
        if not log_files:
            log_files = self.get_qsub_logfiles()

        # make sure there are some log files
        if not log_files:
            raise self._exceptions.AnalysisFileMissing(message = 'Qsub log files not found for the analysis.', errors = '')

        # check all the files for the patterns
        for log_file in log_files:
            with open(log_file, 'rb') as f:
                lines = f.readlines()
            for line in lines:
                for err_pattern in err_patterns:
                    if err_pattern in line:
                        contains_errors[log_file] = True

        self.logger.debug(contains_errors)

        # return a boolean for presence of errors
        if len(contains_errors) < 1:
            return(False)
        else:
            # True or False; any values are True = some log(s) contained error(s)
            if any(contains_errors.values()):
                self.logger.error('Error messages were found in some qsub logs')
                self.logger.debug('qsub log files containing errors: {0}'.format('\n'.join([path for path, value in contains_errors.items() if value == True])))
            return(any(contains_errors.values()))

    def validate(self):
        """
        Validates an ``sns`` analysis output directory. Checks if the ``sns`` analysis completed successfully and is considered valid for downstream usage.

        Returns
        -------
        bool
            ``True`` or ``False`` whether or not the analysis passes validation criteria
        """
        self.validations = {}

        # make sure dir exists
        validation = {
            'dir_exists': {
            'status': self.tools.item_exists(item = self.analysis_dir, item_type = 'dir'),
            'note': 'Whether or not the analysis directory ({0}) exists'.format(self.analysis_dir)
            }
        }
        self.validations.update(validation)

        # check for qsub log errors
        validation = {
            'no_qsub_log_errors_present': {
            'status': not self.check_qsub_log_errors_present(),
            'note': 'Whether or not errors are present in the qsub logs'
            }
        }
        self.validations.update(validation)

        self.logger.debug(self.validations)
        all_valid = [subdict['status'] for key, subdict in self.validations.items()]
        is_valid = all(all_valid)
        self.logger.info('Analysis output passed validation: {0}'.format(is_valid))
        return(is_valid)

    def run(self, *args, **kwargs):
        """
        Runs the ``sns`` validation step
        """
        command = '''
        echo ""
        echo "this is the demo sns validation task, pwd is:"
        echo $PWD
        echo ""
        '''
        run_cmd = self.run_sns_command(command = command)
        self.logger.debug(run_cmd.proc_stdout)


        self.is_valid = self.validate()
        if not self.is_valid:
            err_message = "Sns analysis is invalid;\n{0}".format(self.validations)
            raise self._exceptions.AnalysisInvalid(message = err_message, errors = '')
        return()
