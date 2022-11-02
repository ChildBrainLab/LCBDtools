#!/bin/bash

# usage: ./fmriprep.sh </path/to/BIDS/dataset> <subject>

# source /data/perlman/moochie/resources/server_access/MRIenv/bin/activate.csh

ml singularity

# Usage:
# ./bids-validator.sh <path-to-bids-dataset>

unset PYTHONPATH; singularity run --cleanenv \
	--no-home \
	--home $1 \
	-B $1:/data \
	/scratch/claytons/tlbx/singularity/bids-validator.simg \
	/data \
