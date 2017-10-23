#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Initialize the sns_tasks module and import submodules
'''

# snsxt analysis tasks
import Delly2
import GATK_DepthOfCoverage_custom
import Summary_Avg_Coverage
import HapMap_variant_ref


# task classes
from task_classes import HapMapVariantRef
from task_classes import GATKDepthOfCoverageCustom
from task_classes import SummaryAvgCoverage
