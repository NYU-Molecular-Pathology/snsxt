[![Build Status](https://travis-ci.org/NYU-Molecular-Pathology/snsxt.svg?branch=master)](https://travis-ci.org/NYU-Molecular-Pathology/snsxt)
[![Documentation Status](https://readthedocs.org/projects/snsxt/badge/?version=latest)](http://snsxt.readthedocs.io/en/latest/snsxt.html)

# snsxt
Bioinformatics pipeline framework for data analysis, designed as a wrapper & extension for the [`sns`](https://github.com/NYU-Molecular-Pathology/sns) pipeline

__Documentation located [[here](http://snsxt.readthedocs.io/en/latest/index.html)]__

__Overview presentation located [[here](https://github.com/NYU-Molecular-Pathology/snsxt/blob/pdf/pdf/snsxt.pdf)]__

# Overview

This program is meant to be an extension to the [`sns wes` pipeline](https://github.com/NYU-Molecular-Pathology/sns) for bioinformatic analysis of whole/target exome sequencing data. 

`snsxt` is a BYOC framework (Bring Your Own Code) for setting up new `sns` analyses, and running downstream analysis tasks on their output.

`snsxt` includes built-in handling of HPC cluster jobs, email output, and a modular reporting framework which includes a base `sns wes` report along with the ability to add R Markdown formatted report entries for your custom downstream tasks. 

# Usage

- Create a new directory for your analysis

```bash
mkdir /path/to/analysis
cd /path/to/analysis
```

- Clone this repository and navigate to its directory

```bash
git clone --recursive https://github.com/NYU-Molecular-Pathology/snsxt.git
cd snsxt
```

- Run the `run.py` script 

```bash
snsxt/run.py -d .

```

- __Example command:__

```bash
$ snsxt/run.py -d mini_analysis-controls/ -f mini_analysis-controls/fastq/ -a mini_analysis -r results1 -t task_lists/dev.yml --pairs_sheet mini_analysis-controls/samples.pairs.csv_usethis --debug_mode
```

## Arguments

### Required

- `-d`, `--analysis_dir`: Path to the to use for the analysis. For a new sns analysis, this will become the output directory. For an existing sns analysis output, this will become the input directory

## Optional

- `-f`, `--fastq_dir`: Directories containing .fastq.gz files (required for a new `sns` analysis)

- `-a`, `--analysis_id`: An identifier for the analysis (e.g. NextSeq run ID)

- `-r`, `--results_id`: A sub-identifier for the analysis (e.g. a timestamp)

- `-t`, `--task-list`: A YAML formatted list of downstream analysis tasks for `snsxt`, defaults to `task_lists/default.yml`

- `--targets`: A .bed file with genomic regions for the analysis, defaults to the included `targets.bed` file

- `--probes`: Probes .bed file with regions for CNV analysis, defaults to the included `probes.bed` file

- `--pairs_sheet`: "samples.pairs.csv" samplesheet to use for paired analysis


# Program Components

_Names and locations of these items may change with development_

Starting at the parent `snsxt` (this repo's parent dir):

- `snsxt`: main directory containing all code for the program

- `snsxt/config`: configuration module for the main program

- `snsxt/fixtures`: dummy analysis output files and directories for unit testing

- `snsxt/logs/`: default program log output directory

- [`snsxt/sns_classes`](https://github.com/NYU-Molecular-Pathology/sns_classes): submodule with Python classes for interacting with `sns` pipeline output

- `snsxt/sns_tasks`: submodule containing additional analysis tasks to be performed in the program

- [`snsxt/util`](https://github.com/NYU-Molecular-Pathology/util): submodule with utility functions and classes for usage in the program

- `snsxt/report`: directory containing files and configuration for the parent analysis report

- `snsxt/logging.yml`: configurations for program logging

- `snsxt/test.py`: script to run all unit tests in the program and its submodules

- `snsxt/run.py`: main script used to run the program

# Analysis Tasks

The `sns_tasks` submodule contains code for the various analysis tasks to be run in the program, which are derived from the [`AnalysisTask`](https://github.com/NYU-Molecular-Pathology/snsxt/blob/2c6f446e8dd0e1165e1e2dfc06e7c7679dc23589/snsxt/sns_tasks/task_classes.py#L58) custom class. Examples of other analysis task classes can be seen [here](https://github.com/NYU-Molecular-Pathology/snsxt/blob/2c6f446e8dd0e1165e1e2dfc06e7c7679dc23589/snsxt/sns_tasks/_Delly2.py) and [here](https://github.com/NYU-Molecular-Pathology/snsxt/blob/2c6f446e8dd0e1165e1e2dfc06e7c7679dc23589/snsxt/sns_tasks/_HapMapVariantRef.py), and a [class template](https://github.com/NYU-Molecular-Pathology/snsxt/blob/2c6f446e8dd0e1165e1e2dfc06e7c7679dc23589/snsxt/sns_tasks/_template.py) has also been included. Task classes must be imported into the [`sns_tasks/__init__.py`](https://github.com/NYU-Molecular-Pathology/snsxt/blob/2c6f446e8dd0e1165e1e2dfc06e7c7679dc23589/snsxt/sns_tasks/__init__.py) file in order to be made accessible to the rest of the program. 

## Task Types

Tasks can come in a few flavors, which are described by the following template Python base classes:

- `AnalysisTask`: a task that operate on the entire analysis at once

- `AnalysisSampleTask`: a task that operate on ever sample in the analysis individually

- `QsubAnalysisTask`: a task that submits a single qsub HPC job for the entire analysis

- `QsubSampleTask`: a task that will submit a single qsub HPC job for every sample in the analysis

These base classes each come with predefined attributes and methods to use for completing the task, including a `run()` method which will run the task by calling the task's `main()` method (created by the end-user). These classes are not meant to be used directly, but as templates for the end user's custom task classes, which will implement a `main()` method to run the task's custom actions. 

One other special type of task is included:

- `SnsTask`: a task that runs the `sns` analysis pipeline

This special type of task class is used to set up a new `sns` analysis, and run the various `sns` pipelines when a new analysis is being created. The end user should not have to modify these tasks, but can specify them in their custom task list. 

## Task Lists

The `snsxt` program uses a YAML formatted 'task list' file in order to determine which tasks should be run, and in what order. By default, the [`task_lists/default.yml`](https://github.com/NYU-Molecular-Pathology/snsxt/blob/2c6f446e8dd0e1165e1e2dfc06e7c7679dc23589/task_lists/default.yml) file is used. Tasks names listed should correspond to the name of the Python class for each analysis task, and extra parameters to be passed to the task's `run()` function can be included. 

## Adding New Tasks

You can add new analysis task modules to `snsxt` by following this workflow:

- enter the `sns_tasks` subdirectory and make a copy of the :

```bash
cd snsxt/sns_tasks
cp _template.py _MyNewTask.py
```

- edit the new task's custom Python class following the template shown, putting the main logic to run the task in the class's `main()` method, and setting the `run()` method as a wrapper around the required parent run method. 

- make a copy of the config file for the new module:

```
cp config/template.yml config/MyNewTask.yml
```

- edit the new YAML config file with the corresponding info for the task (recommended to use Sublime Text or Atom)

- import the module inside the [`sns_tasks/__init__.py` ](https://github.com/NYU-Molecular-Pathology/snsxt/blob/2c6f446e8dd0e1165e1e2dfc06e7c7679dc23589/snsxt/sns_tasks/__init__.py)

- add the new module to a task list to be run

## Adding Task Reports

Analysis task modules can have associated report files. These should be R Markdown formatted documents designed to be imported as child-documents to the parent report included in `snsxt/report`. A module specific report can be added like this:

- set the names of all report file(s) in the [config for your task module](https://github.com/NYU-Molecular-Pathology/snsxt/blob/2c6f446e8dd0e1165e1e2dfc06e7c7679dc23589/snsxt/sns_tasks/config/GATK_DepthOfCoverage_custom.yml#L23). 

- add an entry for your new report and its data input directory in the [`snsxt/report` config file](https://github.com/NYU-Molecular-Pathology/snsxt/blob/2c6f446e8dd0e1165e1e2dfc06e7c7679dc23589/snsxt/report/report_config.yml#L7). 

The new report should now be detected by the parent reporting R Markdown document and included in the final report output. 

# Tests

Unit tests for the various modules included in the program can be run with the `test.py` script. Individual modules can be tested with their corresponding `test_*.py` scripts.

# Software
Designed and tested in Python 2.7

Designed to run on Linux systems, tested under CentOS 6

Requires `pandoc` version 1.13+ for reporting

# Credits

[`sh.py`](https://github.com/amoffat/sh) is used as an included dependency.

[sns](https://github.com/NYU-Molecular-Pathology/sns) pipeline output is required to run this. 

`snsxt` uses the [util](https://github.com/NYU-Molecular-Pathology/util) and [sns_classes](https://github.com/NYU-Molecular-Pathology/sns_classes) libraries as dependecies

this is a test

