#!/bin/bash

# usage: ./fmriprep.sh </path/to/BIDS/dataset> ... optional: <participant-to-resume-with>

# source /data/perlman/moochie/resources/server_access/MRIenv/bin/activate.csh

python3 participant_list_builder_fmriprep.py $1

export FREESURFER_HOME="/usr/local/pkg/freesurfer"

if [ $# -eq 1 ]
then
	trigger=1
elif [ $# -eq 2 ]
then
	trigger=0
fi

for sub in $(cat $(dirname $1)/participant_list.txt)
do
	if [ $# -eq 2 ]
	then
		if [ $sub -eq $2 ]
		then
			trigger=1
		fi
	fi

	if [ $trigger ]
	then
		docker run -ti --rm -u $( id -u )\
			--name FMRIPREP_$(basename $(dirname $1)) \
			-v $1:/data:ro \
			-v $1/derivatives:/out \
			-v $FREESURFER_HOME/license.txt:/opt/freesurfer/license.txt \
			nipreps/fmriprep:latest \
			/data /out/fmriprep \
			participant \
			--fs-no-reconall \
			--skip_bids_validation \
        		--use-aroma \
			--mem-mb 30000 \
			--output-spaces MNIPediatricAsym:cohort-2:res-native:res-1 \
			--participant-label $sub

		docker system prune -f
	fi
done


