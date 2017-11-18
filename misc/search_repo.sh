#!/bin/bash

# convenience wrapper for searching code in the repo

args="$@"
repo_dir="$(dirname "$0")"

set -x
find "${repo_dir}/" -type f ! -path "*logs/*" ! -path "*.git/*" ! -name "*.pyc" $args
