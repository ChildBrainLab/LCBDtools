#!/bin/bash

# usage: bash unzipshittyagh.sh /path/to/where/shitty/zips/are

for f in `ls $1 | grep .tgz`; do tar -xvf $1/$f; done
