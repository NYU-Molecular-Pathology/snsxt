#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Functions to load the tasks_lists
'''
# ~~~~~ LOGGING ~~~~~~ #
import logging
import os
import sys
import yaml

# this script's location
scriptdir = os.path.dirname(os.path.realpath(__file__))
scriptname = os.path.basename(__file__)


def read_tasklist_text(input_file, comment_char = '#'):
    '''
    Read the list of tasks from a text file
    '''
    with open(input_file) as f:
        lines = f.read().split("\n")
    # removed commented items
    for i, item in enumerate(lines):
        if item.startswith(comment_char):
            lines.pop(i)
    # remove empty strings
    for i, item in enumerate(lines):
        if item == '':
            lines.pop(i)
    return(lines)

def read_tasklist_yaml(input_file):
    '''
    Load a task list from a YAML formatted file
    should contain a 'tasks' dict with nested subdicts for 'task_name: run_func'
    returns 'tasks_list' as dict, with key 'tasks'
    '''
    with open(input_file, "r") as f:
        tasks_list = yaml.load(f)
    return(tasks_list)


def get_tasks(input_file):
    '''
    Returns the task list dict
    put pre and post-parsing steps here
    '''
    tasks_list = read_tasklist_yaml(input_file = input_file)
    return(tasks_list)
