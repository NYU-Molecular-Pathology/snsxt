#!/bin/bash

# script to submit the snsxt program to run on the computer cluster
# example:
# $ snsxt/qsub_run.sh --analysis_id example_analysis --results_id results1 new demo3-qsub-test/fastq/ -o demo3-qsub-test/sns_output

# $ module list
# Currently Loaded Modulefiles:
#   1) sge/2011.11p1         4) gcc/4.4               7) jre/1.8              10) bzip2/1.0.6          13) pcre/8.38
#   2) local                 5) python/2.7            8) java/1.8             11) curl/7.48.0          14) r/3.3.0
#   3) default-environment   6) git/2.6.5             9) gcc/5.2.0            12) xz/5.2.2

args="$@"
parent_dir="$(dirname $0)"
snsxt_run_script="${parent_dir}/run.py"
qsub_logdir="${parent_dir}/logs"
job_name='snsxt'

echo "snsxt_run_script is $snsxt_run_script"
echo "qsub_logdir is $qsub_logdir"

# make sure run script exists
if [ ! -f "$snsxt_run_script" ]; then
    printf 'ERROR: File does not exist: %s\n' "$snsxt_run_script"
    printf 'Did you run this from the parent snsxt directory?'
    printf 'Exiting...\n'
    exit 1
fi

# make sure qsub_logdir exists
[ ! -d "$qsub_logdir" ] && mkdir -p "$qsub_logdir"

# submit qsub job
qsub -wd $PWD -o :${qsub_logdir}/ -e :${qsub_logdir}/ -j y -N "$job_name" <<E0F
module unload python
module load python/2.7
set -x
$snsxt_run_script $args
set +x
E0F
