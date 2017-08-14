#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
unit tests for the program
'''
import unittest
from .find import multi_filter

class TestMultiFilter(unittest.TestCase):

    def test_fail(self):
        self.assertTrue(True, 'Demo assertion')

if __name__ == '__main__':
    unittest.main()
