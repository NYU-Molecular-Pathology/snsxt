#!/bin/bash

(

module unload python
module load python/2.7

# download
if [ ! -d blais-snakefood-6d55510bd30b ]; then
    {
        wget https://bitbucket.org/blais/snakefood/get/6d55510bd30b.zip
    } && {
        unzip -o 6d55510bd30b.zip
    } && {
        rm -f 6d55510bd30b.zip
    }
fi
# install
if [ ! -d venv ]; then
    virtualenv venv --no-site-packages

    if [ -d venv ]; then
        source venv/bin/activate
        {
            cd blais-snakefood-6d55510bd30b
        } && {
            python setup.py install
        }
    fi
fi


printf "Run this:\n\nsource venv/bin/activate\n\n"
)
