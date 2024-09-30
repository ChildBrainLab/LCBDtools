#!/bin/bash

command=$1
list_file=$2

while read option
do
    bash $command $option
done < $list_file
