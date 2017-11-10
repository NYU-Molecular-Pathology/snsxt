#!/bin/bash
set -x
{
    sfood ../snsxt/ -i | sfood-graph --fontsize=48 > deps.dot
} && {
    ./graph_deps.sh
}
