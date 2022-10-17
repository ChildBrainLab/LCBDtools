#!/bin/bash

# usage: ./fmriprep.sh </path/to/BIDS/dataset> <subject>

# source /data/perlman/moochie/resources/server_access/MRIenv/bin/activate.csh

ml singularity
ml freesurfer

export FREESURFER_HOME="/export/freesurfer/freesurfer-7.2.0/"
export TEMPLATEFLOWHOME="/scratch/claytons/tlbx/templateflow"
export SINGULARITYENV_TEMPLATEFLOW_HOME="/templateflow"

singularity run --cleanenv \
	--no-home \
	--home $1 \
	-B $1:/data \
	-B $FREESURFER_HOME \
	-B $TEMPLATEFLOWHOME:/templateflow \
	-B /scratch/claytons/tmp/fmriprep_work:/work \
	/scratch/claytons/tlbx/singularity/fmriprep_21.0.2.sif \
	/data /data/derivatives/fmriprep \
	participant --participant-label $2 \
	-w /work \
	--fs-license-file $FREESURFER_HOME/.license \
	--skip_bids_validation \
	--use-aroma \
	--nthreads 8 \
	--low-mem \
	--mem-mb 60000 \
	--output-spaces MNIPediatricAsym:cohort-2:res-2 \
