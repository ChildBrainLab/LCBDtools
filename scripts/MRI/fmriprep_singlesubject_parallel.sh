#!/bin/bash

# usage: ./fmriprep.sh </path/to/BIDS/dataset> ... optional: <participant-to-resume-with>

# source /data/perlman/moochie/resources/server_access/MRIenv/bin/activate.csh

export FREESURFER_HOME="/usr/local/pkg/freesurfer"

for sub in $(cat $(dirname $1)/parallel_subs.txt)
do
	#docker run --rm\
	docker run --rm -u $( id -u)\
		--name FMRIPREP_$(basename $(dirname $1))_$sub \
		-v $1:/data:ro \
		-v $1/derivatives:/out \
		-v $1/work:/work \
		-v $(dirname $1)/bids-database:/bids-database \
		-v $FREESURFER_HOME/license.txt:/opt/freesurfer/license.txt \
		-v /data/perlman/moochie/resources/templateflow:/home/fmriprep/.cache/templateflow \
		-e TEMPLATEFLOW_HOME='/home/fmriprep/.cache/templateflow' \
		nipreps/fmriprep:latest \
		/data /out/fmriprep \
		participant \
		-w /work \
		--longitudinal \
		--skip_bids_validation \
        	--use-aroma \
		--nthreads 16 \
		--low-mem \
		--mem-mb 15000 \
		--output-spaces MNIPediatricAsym:cohort-2:res-2 \
		--participant-label $sub &

	# docker system prune -f
done


