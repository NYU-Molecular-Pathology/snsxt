#!/bin/bash

fastq_dir="/ifs/data/molecpathlab/quicksilver/170918_NB501073_0025_AHH35JBGX3/Data/Intensities/BaseCalls/Unaligned/NS17-22"

shrink () {
    # get a small sample of the fastq.gz file
    local input_file="$1"
    local input_basename="$(basename "$input_file")"
    zcat "$input_file" | head -n 1200 | gzip > "$input_basename"
}

cat samplenames.tsv | while read line; do
    if [ ! -z "$line" ]; then
        echo "$line"

    find "$fastq_dir" -type f -name "${line}*" | while read filename; do
        echo "$filename"
        shrink "$filename"
    done

        echo ''
    fi
done
