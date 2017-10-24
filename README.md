[![Build Status](https://travis-ci.org/NYU-Molecular-Pathology/snsxt.svg?branch=master)](https://travis-ci.org/NYU-Molecular-Pathology/snsxt)
# snsxt
Extension to the sns pipeline

# Overview

This program is meant to be an extension to the [`sns wes` pipeline](https://github.com/NYU-Molecular-Pathology/sns) for whole/target exome sequencing data analysis. 

`snsxt` is a BYOC framework (Bring Your Own Code) for running downstream analysis tasks on sns-wes pipeline output. 

Use this framework to run any extra analysis tasks you like after an `sns` pipeline analysis has finished.

# Usage

__NOTE:__ Usage may change as development progresses

- Navigate to the directory containing your `sns` analysis output

```bash
cd /path/to/sns_output
```

- Clone this repository and navigate to its directory

```bash
git clone --recursive https://github.com/NYU-Molecular-Pathology/snsxt.git
cd snsxt
```

- Run the `run.py` script

```bash
snsxt/run.py ../ --analysis_id "<analysis_id>" --results_id "<results_id>" 
```

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

Tasks can come in a few flavors:

- tasks that operate on the entire analysis at once

- tasks that operate on a single sample at a time

Additionally, tasks can be run a few different ways:

- run in the current program session

- submitted as a compute job to the HPC cluster with `qsub`

Each combination of task type and run type utilizes a separate ['run' function](https://github.com/NYU-Molecular-Pathology/snsxt/blob/2c6f446e8dd0e1165e1e2dfc06e7c7679dc23589/snsxt/sns_tasks/task_classes.py#L158), which should be wrapped by the task's [`run()` method](https://github.com/NYU-Molecular-Pathology/snsxt/blob/2c6f446e8dd0e1165e1e2dfc06e7c7679dc23589/snsxt/sns_tasks/_GATKDepthOfCoverageCustom.py#L126).

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
