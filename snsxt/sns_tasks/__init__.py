#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Initialize the sns_tasks module and import task classes
"""

# task classes
# from _template import TemplateAnalysisTask
# from _template import TemplateAnalysisSampleTask
from _HapMapVariantRef import HapMapVariantRef
from _GATKDepthOfCoverageCustom import GATKDepthOfCoverageCustom
from _SummaryAvgCoverage import SummaryAvgCoverage
from _Delly2 import Delly2
from _DemoQsubSampleTask import DemoQsubSampleTask
from _DemoQsubAnalysisTask import DemoQsubAnalysisTask

# sns tasks
from _StartSns import StartSns
from _SnsWes import SnsWes
from _SnsWesPairsSnv import SnsWesPairsSnv
