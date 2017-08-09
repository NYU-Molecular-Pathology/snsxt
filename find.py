#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Functions for finding files and dirs

tested with python 2.7
'''
import logging
logger = logging.getLogger("find")
logger.debug("loading find module")

import os
import sys
import itertools
import fnmatch

def find(search_dir, inclusion_patterns = ('*',), exclusion_patterns = (), search_type = 'all', num_limit = None, level_limit = None):
    '''
    Function to search for
    num_limit is the number of matches to return; use None for no limit
    level_limit is the number of directory levels to recurse; 0 is parent dir only
    '''
    import sys
    import itertools
    if num_limit != None:
        matches = []
        for item in find_gen(search_dir = search_dir, inclusion_patterns = inclusion_patterns, exclusion_patterns = exclusion_patterns, search_type = search_type, level_limit = level_limit):
            if len(matches) <= int(num_limit):
                matches.append(item)
        logger.debug("Matches found: {0}".format(matches))
        return(matches)
    else:
        matches = [item for item in find_gen(search_dir = search_dir, inclusion_patterns = inclusion_patterns, exclusion_patterns = exclusion_patterns, search_type = search_type, level_limit = level_limit)]
        logger.debug("Matches found: {0}".format(matches))
        return(matches)

def find_gen(search_dir, inclusion_patterns = ('*',), exclusion_patterns = (), search_type = 'all', level_limit = None):
    '''
    Generator function to return file matches
    search_type = 'all', 'file', or 'dir'
    '''
    import os
    import sys
    import fnmatch
    search_dir = search_dir.rstrip(os.path.sep)
    assert os.path.isdir(search_dir)
    num_sep = search_dir.count(os.path.sep)
    logger.debug("Searching {0} for {1} matching {2}, level limit: {3}".format(search_dir, search_type, inclusion_patterns, level_limit))
    for root, dirs, files in os.walk(search_dir):
        # choose which items to search
        if search_type == 'all':
            items = dirs + files
        elif search_type == 'dir':
            items = dirs
        elif search_type == 'file':
            items = files
        else:
            logger.error("Search type '{0}' not valid, exiting script".format(search_type))
            sys.exit()
        # yeild the results
        for item in super_filter(names = items, inclusion_patterns = inclusion_patterns, exclusion_patterns = exclusion_patterns):
            yield(os.path.join(root, item))
        # check for a level limit
        if level_limit != None:
            num_sep_this = root.count(os.path.sep)
            if num_sep + int(level_limit) <= num_sep_this:
                del dirs[:]


def super_filter(names, inclusion_patterns = ('*',), exclusion_patterns = ()):
    '''
    Enhanced version of fnmatch.filter() that accepts multiple inclusion and exclusion patterns.

    Filter the input names by choosing only those that are matched by
    some pattern in inclusion_patterns _and_ not by any in exclusion_patterns.
    Adapted from:
    https://codereview.stackexchange.com/questions/74713/filtering-with-multiple-inclusion-and-exclusion-patterns
    '''
    included = multi_filter(names, patterns = inclusion_patterns)
    excluded = multi_filter(names, patterns = exclusion_patterns)
    for item in set(included) - set(excluded):
        yield(item)

def multi_filter(names, patterns):
    '''
    Generator function which yields the names that match one or more of the patterns.
    '''
    for name in names:
        # in case a single string was passed as a pattern
        if isinstance(patterns, str):
            if fnmatch.fnmatch(name, patterns):
                yield name
        else:
            for pattern in patterns:
                if fnmatch.fnmatch(name, pattern):
                    yield name



# deprecated

def find_files(search_dir, search_filename):
    '''
    return the paths to all files matching the supplied filename in the search dir
    '''
    import os
    print('Now searching for file "{0}" in directory {1}'.format(search_filename, search_dir))
    file_list = []
    for root, dirs, files in os.walk(search_dir):
        for file in files:
            if file == search_filename:
                found_file = os.path.join(root, file)
                file_list.append(found_file)
    print('Found {0} matches'.format(len(file_list)))
    return(file_list)

def walklevel(some_dir, level=1):
    '''
    Recursively search a directory for all items up to a given depth
    use it like this:
    file_list = []
    for item in pf.walklevel(some_dir):
        if ( item.endswith('my_file.txt') and os.path.isfile(item) ):
            file_list.append(item)
    '''
    import os
    some_dir = some_dir.rstrip(os.path.sep)
    assert os.path.isdir(some_dir)
    num_sep = some_dir.count(os.path.sep)
    for root, dirs, files in os.walk(some_dir):
        # yield root, dirs, files
        for dir in dirs:
            yield os.path.join(root, dir)
        for file in files:
            yield os.path.join(root, file)
        num_sep_this = root.count(os.path.sep)
        if num_sep + level <= num_sep_this:
            del dirs[:]
