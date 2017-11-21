#!/bin/bash

# set the git remotes to ssh

git remote set-url origin git@github.com:NYU-Molecular-Pathology/snsxt.git

(
cd snsxt/util
git remote set-url origin git@github.com:NYU-Molecular-Pathology/util.git
)


(
cd snsxt/sns_classes
git remote set-url origin git@github.com:NYU-Molecular-Pathology/sns_classes.git
)
