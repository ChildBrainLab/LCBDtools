#!/bin/bash

#usage: bash CNDA_get_sessions.sh <output_file.txt>

source /data/perlman/moochie/resources/server_access/MRIenv/bin/activate
export XNAT_HOST=https://cnda.wustl.edu

if [ -f "$1" ]; then
	rm $1
fi

sub_prefix="+ Subject: "
ses_prefix="* Session: "

Xnatquery -p NP1166 | grep "$sub_prefix" | while read sub; do
	CNDAsub=${sub#"$sub_prefix"}
	
	Xnatquery -p NP1166 -s $CNDAsub | grep "$ses_prefix" | while read ses; do
		CNDAses=${ses#"$ses_prefix"}
		echo $CNDAses >> $1
	done
done
