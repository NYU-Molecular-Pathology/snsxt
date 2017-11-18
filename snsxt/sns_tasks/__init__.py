#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Initialize the sns_tasks module and import task classes
"""
# demo classes
from DemoQsubSampleTask import DemoQsubSampleTask
from DemoQsubAnalysisTask import DemoQsubAnalysisTask
from DemoMultiQsubSampleTask import DemoMultiQsubSampleTask
from DemoSnsTask import DemoSnsTask

# sns tasks
from _SnsSetupPairs import SnsSetupPairs
from StartSns import StartSns
from SnsWes import SnsWes
from SnsWesPairsSnv import SnsWesPairsSnv
from SnsRnaStar import SnsRnaStar

# task classes
from HapMapVariantRef import HapMapVariantRef
from GATKDepthOfCoverageCustom import GATKDepthOfCoverageCustom
from SummaryAvgCoverage import SummaryAvgCoverage
from Delly2 import Delly2
from MuTect2_split import MuTect2Split
