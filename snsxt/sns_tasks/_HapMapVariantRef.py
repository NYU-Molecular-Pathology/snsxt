#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re
from task_classes import AnalysisTask

class HapMapVariantRef(AnalysisTask):
    '''
    Class for comparing each HapMap sample variant calls against
    a known list of previously sequenced HapMap variants
    Save the overlapping variants in a new files to load in the report

    from HapMap_variant_ref_dev import HapMapVariantRef
    x = HapMapVariantRef(analysis = None)
    '''
    def __init__(self, analysis, taskname = 'HapMap_variant_ref', config_file = 'HapMap_variant_ref.yml', extra_handlers = None):
        '''
        '''
        AnalysisTask.__init__(self, taskname = taskname, config_file = config_file, analysis = analysis, extra_handlers = extra_handlers)

    def main(self, sample):
        '''
        Main function for running the analysis task
        '''
        self.logger.debug('Sample is: {0}'.format(sample))

        # get paths to files for the sample
        # file with the sample's ANNOVAR annotations
        sample_annot_file = sample.list_none(sample.get_output_files(analysis_step = self.task_configs['input_dir'], pattern = self.task_configs['input_pattern']))
        self.logger.debug('sample_annot_file is: {0}\nand has {1} entries'.format(sample_annot_file, self.tools.num_lines(sample_annot_file, skip = 1)))

        # reference HapMap variants file
        hapmap_variant_file = os.path.join(self.main_configs['tasks_files_dir'], self.task_configs['hapmap_variant_file'])

        # file to save the variants not in the reference list
        output_file = os.path.join(self.output_dir, os.path.basename(sample_annot_file))

        # check if the sample ID indicates that it is HapMap sample
        if re.match('hapmap', sample.id, re.IGNORECASE):
            self.logger.debug('Sample is a HapMap sample')



            # reference HapMap variants file; copy it over
            self.logger.debug('hapmap_variant_file is: {0}\nand has {1} entries'.format(hapmap_variant_file, self.tools.num_lines(hapmap_variant_file, skip = 1)))

            logger.debug('Output file will be: {0}'.format(output_file))

            # find the new variants
            logger.debug('Overlapping the sample_annot_file against the hapmap_variant_file...')
            self.tools.write_tabular_overlap(file1 = sample_annot_file, ref_file = hapmap_variant_file, output_file = output_file, delim = '\t', inverse = True)
            logger.debug('{0} non-overlapping variants were output'.format(self.tools.num_lines(output_file, skip = 1)))
        return(hapmap_variant_file)

    def run(self, *args, **kwargs):
        '''
        Run the analysis step
        '''
        self.run_sample_task(analysis = self.analysis, *args, **kwargs)
        self.setup_report()
