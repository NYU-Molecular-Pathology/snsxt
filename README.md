[![Build Status](https://travis-ci.org/NYU-Molecular-Pathology/snsxt.svg?branch=master)](https://travis-ci.org/NYU-Molecular-Pathology/snsxt)
# snsxt
Extension to the sns pipeline

# Overview

This program is meant to be an extension to the [sns](https://github.com/NYU-Molecular-Pathology/sns) WES pipeline for whole/target exome sequencing data analysis. 

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
