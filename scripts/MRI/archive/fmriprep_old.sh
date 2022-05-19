#!/bin/bash

# usage: ./fmriprep.sh /path/to/BIDS/dataset  

# source /data/perlman/moochie/resources/server_access/MRIenv/bin/activate.csh

export FREESURFER_HOME="/usr/local/pkg/freesurfer"

docker run -ti --rm \
	--name FMRIPREP \
	--cpu-shares 2048 \
	-v $1:/data:ro \
	-v $1/derivatives/fmriprep/:/out \
	-v $FREESURFER_HOME/license.txt:/opt/freesurfer/license.txt \
	nipreps/fmriprep:latest \
	/data /out/out \
	participant \
	--skip_bids_validation \
        --use-aroma \
	--participant-label $(cat participant_list.txt)  
