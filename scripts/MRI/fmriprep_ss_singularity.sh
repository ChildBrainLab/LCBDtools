#!/bin/bash

# usage: ./fmriprep.sh </path/to/BIDS/dataset> <subject>

# source /data/perlman/moochie/resources/server_access/MRIenv/bin/activate.csh

ml singularity
ml freesurfer

export FREESURFER_HOME="/export/freesurfer/freesurfer-7.2.0/"
export TEMPLATEFLOWHOME="/scratch/claytons/tlbx/templateflow"
export SINGULARITYENV_TEMPLATEFLOW_HOME="/home/fmriprep/.cache/templateflow"
export SINGULARITYENV_TEMPLATEFLOW_AUTOUPDATE=0

sub=$2

singularity run \
	--cleanenv \
	--no-home \
	-B $1:/data \
	-B $1/derivatives:/out \
	-B $1/work:/work \
	-B $TEMPLATEFLOWHOME:$SINGULARITYENV_TEMPLATEFLOW_HOME \
	-B $FREESURFER_HOME/.license:/opt/freesurfer/license.txt \
	/scratch/claytons/tlbx/singularity/fmriprep.simg \
	/data /out \
	participant \
	-w /work \
	--fs-license-file /opt/freesurfer/license.txt \
	--longitudinal \
	--skip_bids_validation \
	--use-aroma \
	--nthreads 16 \
	--low-mem \
	--mem-mb 30000 \
	--output-spaces MNIPediatricAsym:cohort-2:res-2 \
	--participant-label $2
