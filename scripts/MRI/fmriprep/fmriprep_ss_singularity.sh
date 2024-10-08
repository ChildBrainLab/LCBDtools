#!/bin/bash

# usage: ./fmriprep.sh </path/to/BIDS/dataset> <subject>

# source /data/perlman/moochie/resources/server_access/MRIenv/bin/activate.csh

ml singularity
ml freesurfer

export FREESURFER_HOME="/export/freesurfer/freesurfer-7.2.0/"
export TEMPLATEFLOWHOME="/scratch/claytons/tlbx/templateflow"
export SINGULARITYENV_TEMPLATEFLOW_HOME="/templateflow"

unset PYTHONPATH; singularity run --cleanenv \
	--no-home \
	--home $1 \
	-B $1:/data \
	-B $FREESURFER_HOME \
	-B $TEMPLATEFLOWHOME:/templateflow \
	-B /scratch/claytons/tmp/fmriprep_work:/work \
	/scratch/claytons/tlbx/singularity/fmriprep-22.0.2.simg \
	/data /data/derivatives/fmriprep \
	participant --participant-label $2 \
	-w /work/"${$2}" \
	--fs-license-file $FREESURFER_HOME/.license \
	--skip_bids_validation \
	--use-aroma \
	--nthreads 8 \
	--mem-mb 60000 \
	--output-spaces MNIPediatricAsym:cohort-2:res-2 \
	#--low-mem \
