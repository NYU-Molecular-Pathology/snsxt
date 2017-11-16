#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Initialize the sns_tasks module and import task classes
"""
# demo classes
from _DemoQsubSampleTask import DemoQsubSampleTask
from _DemoQsubAnalysisTask import DemoQsubAnalysisTask
from _DemoMultiQsubSampleTask import DemoMultiQsubSampleTask
from _DemoSnsTask import DemoSnsTask

# sns tasks
from _StartSns import StartSns
from _SnsWes import SnsWes
from _SnsWesPairsSnv import SnsWesPairsSnv
from _SnsSetupPairs import SnsSetupPairs

# task classes
from _HapMapVariantRef import HapMapVariantRef
from _GATKDepthOfCoverageCustom import GATKDepthOfCoverageCustom
from _SummaryAvgCoverage import SummaryAvgCoverage
from _Delly2 import Delly2
from _MuTect2_split import MuTect2Split
