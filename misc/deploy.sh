#!/bin/bash

# script to deploy a new copy of the program in another location

input_dir="$1"

deploy () {
    # set up a new copy of the program
    local input_dir="$1"
    (
    cd "$input_dir"
    git clone --recursive https://github.com/NYU-Molecular-Pathology/snsxt.git
    )
}

# check if the dir exists
if [ -d "$input_dir" ]; then
    printf "Setting up new snsxt in location: %s\n" "${input_dir}"
    deploy "$input_dir"
else
    printf "Directory %s does not exist, it will be created\n" "${input_dir}"
    mkdir -p "$input_dir"
    deploy "$input_dir"
fi
