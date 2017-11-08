#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Runs all the unit tests found throughout the program
"""

import unittest

if __name__ == "__main__":
    loader = unittest.TestLoader()
    start_dir = '.'
    suite = loader.discover(start_dir)

    runner = unittest.TextTestRunner()
    runner.run(suite)
