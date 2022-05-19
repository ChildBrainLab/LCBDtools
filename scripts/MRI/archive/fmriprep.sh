#!/bin/bash

# usage: ./fmriprep.sh /path/to/BIDS/dataset  

# source /data/perlman/moochie/resources/server_access/MRIenv/bin/activate.csh

python3 participant_list_builder.py $1

export FREESURFER_HOME="/usr/local/pkg/freesurfer"

docker run -ti --rm -u $( id -u )\
	--name FMRIPREP \
	-v $1:/data:ro \
	-v $1/derivatives:/out \
	-v $FREESURFER_HOME/license.txt:/opt/freesurfer/license.txt \
	nipreps/fmriprep:latest \
	/data /out/fmriprep \
	participant \
	--fs-no-reconall \
	--skip_bids_validation \
        --use-aroma \
	--output-spaces MNIPediatricAsym:cohort-2:res-native:res-1 \
	--participant-label $(cat participant_list.txt)
