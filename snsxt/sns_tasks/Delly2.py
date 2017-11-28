#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re
from task_classes import QsubSampleTask

class Delly2(QsubSampleTask):
    """
    Class for for running Delly2 with the sns pipeline
    """
    def __init__(self, analysis, taskname = 'Delly2', config_file = 'Delly2.yml', extra_handlers = None):
        """
        """
        QsubSampleTask.__init__(self, taskname = taskname, config_file = config_file, analysis = analysis, extra_handlers = extra_handlers)

    def delly2_cmd(self, sampleID, bam_file, output_dir):
        """
        Build the terminal commands to run Delly2 on a single sample

        Make a separate command for each SV calling type, concatenate them all together
        """
        # get params from config
        delly2_bin = self.task_configs['bin']
        bcftools_bin = self.task_configs['bcftools_bin']
        hg19_fa = self.task_configs['hg19_fa']
        call_types = self.task_configs['call_types']
        output_SV_bcf_ext = self.task_configs['output_SV_bcf_ext']
        output_SV_vcf_ext = self.task_configs['output_SV_vcf_ext']

        # empty list to hold individual command strings
        SV_calling_commands = []

        # make a command for each SV calling type:
        for call_type_name, call_type_arg in call_types:
            # make filepath for the .bcf output
            sample_output_SV_bcf_basename = ''.join([sampleID, '.' + call_type_name, output_SV_bcf_ext])
            sample_output_SV_bcf = os.path.join(output_dir, sample_output_SV_bcf_basename)

            # make filepath for the .vcf converted output
            sample_output_SV_vcf_basename = ''.join([sampleID, '.' + call_type_name, output_SV_vcf_ext])
            sample_output_SV_vcf = os.path.join(output_dir, sample_output_SV_vcf_basename)

            # delly call -t DEL -g "genome.fa" -o "results_dir/delly2-snv/Sample1.deletions.bcf" "results_dir/BAM-GATK-RA-RC/Sample1.dd.ra.rc.bam"
            # bcftools view "results_dir/delly2-snv/Sample1.deletions.bcf" > "results_dir/delly2-snv/Sample1.deletions.vcf"
            command = """
    {0} call -t {1} -g "{2}" -o "{3}" "{4}"

    {5} view "{6}" "{7}"
    """.format(
    delly2_bin,
    call_type_arg,
    hg19_fa,
    sample_output_SV_bcf,
    bam_file,

    bcftools_bin,
    sample_output_SV_bcf,
    sample_output_SV_vcf
    )
            SV_calling_commands.append(command)

        # concatenate all commands
        delly2_command = '\n'.join(SV_calling_commands)
        return(delly2_command)

    def main(self, sample, extra_handlers = None):
        """
        Main control function for the program
        Runs Delly2 on a single sample from an sns analysis
        sample is an SnsAnalysisSample object
        return the qsub job for the sample
        """
        # TODO: does this need to be here?
        self.setup_report()

        qsub_log_dir = self.qsub_log_dir
        # qsub_log_dir = sample.list_none(sample.analysis_config['dirs']['logs-qsub'])
        self.logger.debug('qsub_log_dir: {0}'.format(qsub_log_dir))

        sample_bam = self.get_sample_file_inputpath(sampleID = sample.id, suffix = self.input_suffix)
        # sample_bam = sample.list_none(sample.get_output_files(analysis_step = self.task_configs['input_dir'], pattern = self.task_configs['input_pattern']))

        # make sure the files and locations exist
        self.validate_items([sample_bam, qsub_log_dir])


        self.logger.debug('sample_bam: {0}'.format(sample_bam))

        # make the shell command to run
        command = self.delly2_cmd(sampleID = sample.id, bam_file = sample_bam, output_dir = self.output_dir)

        # submit the command as a qsub job on the HPC
        # commands to create debug jobs
        job = self.qsub.submit(command = command, name = self.taskname + '.' + sample.id, stdout_log_dir = qsub_log_dir, stderr_log_dir = qsub_log_dir, verbose = True, sleeps = 1) #

        return(job)
