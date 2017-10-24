#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Module for the start_sns function to start a new analysis
'''
# ~~~~~ LOGGING ~~~~~~ #
import os
import sys
import shutil
from util import tools as t
from util import qsub
import logging
logger = logging.getLogger(__name__)


def start_sns(configs, **kwargs):
    '''
    Start a new sns wes pipeline analysis
    when finished, return the output_dir for use in the downstream processing

    sns/gather-fastqs /fastq_dir/
    sns/generate-settings hg19
    sns/run wes
    sns/run wes-pairs-snv
    '''
    extra_handlers = configs.get('extra_handlers', [])
    snsxt_parent_dir = configs['snsxt_parent_dir']

    logger.debug('Starting new sns analysis')
    logger.debug(configs)
    logger.debug(kwargs)

    fastq_dirs = kwargs.pop('fastq_dirs', [])
    output_dir = kwargs.pop('output_dir', None)
    targets_bed = kwargs.pop('targets_bed', os.path.join(snsxt_parent_dir, 'targets.bed'))
    pairs_sheet = kwargs.pop('pairs_sheet', None)
    no_qsub_wait = kwargs.pop('no_qsub_wait', False) # True = do not wait, False = do wait

    if kwargs:
        raise TypeError('Unexpected **kwargs: %r' % kwargs)

    # make sure all input fastq directories exist

    for d in fastq_dirs:
        if not t.item_exists(item = d, item_type = 'dir'):
            logger.error('fastq dir does not exist: {0}'.format(d))
            sys.exit()

    # get the full paths to input fastq directories
    fastq_dir_paths = [os.path.realpath(d) for d in fastq_dirs]
    logger.debug('fastq_dir_paths are: {0}'.format(fastq_dir_paths))
    logger.debug('output_dir will be: {0}'.format(output_dir))
    logger.debug('targets_bed will be: {0}'.format(targets_bed))

    # set up output directory
    logger.debug('Creating output directory')
    t.mkdirs(output_dir)
    if not t.item_exists(item = output_dir, item_type = 'dir'):
        logger.error('output_dir does not exist: {0}'.format(output_dir))
        sys.exit()

    # copy targets bed
    if not t.item_exists(item = targets_bed, item_type = 'file'):
        logger.error('targets_bed does not exist: {0}'.format(targets_bed))
        sys.exit()

    output_targets_bed = os.path.join(output_dir, os.path.basename(targets_bed))
    logger.debug('Copying over targets .bed file to: {0}'.format(output_targets_bed))
    shutil.copy2(targets_bed, output_targets_bed)

    # copy sns repo
    sns_repo_dirpath = os.path.join(os.path.dirname(__file__), configs['sns_repo_dir'])
    output_sns_repo = os.path.join(output_dir, os.path.basename(configs['sns_repo_dir']))
    logger.debug('sns_repo_dirpath is {0}'.format(sns_repo_dirpath))
    logger.debug('sns repo will be copied to: {0}'.format(output_sns_repo))
    t.copy_and_overwrite(from_path = sns_repo_dirpath, to_path = output_sns_repo)
    if not t.item_exists(item = output_sns_repo, item_type = 'dir'):
        logger.error('output_sns_repo does not exist: {0}'.format(output_sns_repo))
        sys.exit()

    # remove samples_fastq_raw_file if it already exists
    samples_fastq_raw_file = configs['samples_fastq_raw_file']
    samples_fastq_raw_filepath = os.path.join(output_dir, samples_fastq_raw_file)
    if t.item_exists(samples_fastq_raw_filepath):
        new_filepath = os.path.join(output_dir, '{0}_old.{1}'.format(samples_fastq_raw_file, t.timestamp()))
        logger.debug('old file {0} will be renamed {1}'.format(samples_fastq_raw_filepath, new_filepath))
        os.rename(samples_fastq_raw_filepath, new_filepath)

    # change to the output directory
    with t.DirHop(output_dir) as d:
        # run 'sns/gather-fastqs' on the fastq dirs
        fastq_gather_commands = ['sns/gather-fastqs {0}'.format(d) for d in fastq_dir_paths]
        logger.debug(fastq_gather_commands)
        for fastq_gather_command in fastq_gather_commands:
            run_cmd = t.SubprocessCmd(command = fastq_gather_command).run()
            logger.debug(run_cmd.proc_stdout)
            logger.debug(run_cmd.proc_stderr)

        # generate sns settings
        settings_command = 'sns/generate-settings hg19'
        run_cmd = t.SubprocessCmd(command = settings_command).run()
        logger.debug(run_cmd.proc_stdout)
        logger.debug(run_cmd.proc_stderr)

        # run the main analysis
        sns_route_command = 'sns/run {0}'.format(configs['sns_route'])
        run_cmd = t.SubprocessCmd(command = sns_route_command).run()
        logger.debug(run_cmd.proc_stdout)
        logger.debug(run_cmd.proc_stderr)

        # capture the qsub jobs
        jobs = []
        for job in [qsub.Job(id = job_id, name = job_name) for job_id, job_name in qsub.find_all_job_id_names(text = run_cmd.proc_stdout)]:
            jobs.append(job)

        for job in [qsub.Job(id = job_id, name = job_name) for job_id, job_name in qsub.find_all_job_id_names(text = run_cmd.proc_stderr)]:
            jobs.append(job)

        logger.info('Submitted jobs: {0}'.format([job.id for job in jobs]))

        if not no_qsub_wait:
            logger.debug('Waiting for jobs to complete...')
            qsub.monitor_jobs(jobs = jobs)

        # run paired analysis
        if pairs_sheet:
            logger.debug('Running paired analysis')


    return(output_dir)
