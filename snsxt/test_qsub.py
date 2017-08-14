#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
unit tests for the find module
'''
import unittest
import os
from qsub import Job


class TestJob(unittest.TestCase):
    def setUp(self):
        self.scriptdir = os.path.dirname(os.path.realpath(__file__))
        self.fixture_dir = os.path.join(self.scriptdir, "fixtures")
        self.qstat_stdout_all_Eqw_file = os.path.join(self.fixture_dir, "qstat_stdout_all_Eqw.txt")
        self.qstat_stdout_Eqw_qw_file = os.path.join(self.fixture_dir, "qstat_stdout_Eqw_qw.txt")
        self.qstat_stdout_r_Eqw_file = os.path.join(self.fixture_dir, "qstat_stdout_r_Eqw.txt")

        with open(self.qstat_stdout_all_Eqw_file, "rb") as f:
            self.qstat_stdout_all_Eqw_str = f.read()
        # print(self.qstat_stdout_all_Eqw_str)

        with open(self.qstat_stdout_Eqw_qw_file, "rb") as f:
            self.qstat_stdout_Eqw_qw_str = f.read()
        # print(self.qstat_stdout_Eqw_qw_str)

        with open(self.qstat_stdout_r_Eqw_file, "rb") as f:
            self.qstat_stdout_r_Eqw_str = f.read()
        # print(self.qstat_stdout_r_Eqw_str)

        self.debug_job = Job(id = '', debug = True)

    def tearDown(self):
        del self.scriptdir
        del self.fixture_dir

        del self.qstat_stdout_all_Eqw_file
        del self.qstat_stdout_all_Eqw_str

        del self.qstat_stdout_Eqw_qw_file
        del self.qstat_stdout_Eqw_qw_str

        del self.qstat_stdout_r_Eqw_file
        del self.qstat_stdout_r_Eqw_str
        return()
        # del self.fixture

    def test_true(self):
        self.assertTrue(True, 'Demo assertion')

    def test_fail(self):
        self.assertFalse(False)

    def test_error(self):
        self.assertRaises(ValueError)

    def test_running_job1(self):
        '''
        Find running job
        id = '2495634'
        self.qstat_stdout_r_Eqw_file

        qstat_stdout_r_Eqw_file = "fixtures/qstat_stdout_r_Eqw.txt"
        with open(qstat_stdout_r_Eqw_file, "rb") as f: qstat_stdout_r_Eqw_str = f.read()
        from qsub import Job
        x = Job(id = '2495634', debug = True)
        '''
        self.job = Job(id = '2495634', debug = True)
        self.job._debug_update(qstat_stdout = self.qstat_stdout_r_Eqw_str)
        self.assertTrue(self.job.is_running)




    # def test_super_filter_all_Eqw(self):
    #     filenames = ['fixtures/qstat_stdout_all_Eqw.txt', 'fixtures/qstat_stdout_r_Eqw.txt', 'fixtures/qstat_stdout_Eqw_qw.txt']
    #     match_result = [x for x in super_filter(names = filenames, inclusion_patterns = "*Eqw*")]
    #     self.assertTrue(filenames == match_result)
    #



if __name__ == '__main__':
    unittest.main()
