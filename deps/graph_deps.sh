#!/bin/bash
set -x
dot deps.dot -Tpdf -o deps.pdf && open deps.pdf &
