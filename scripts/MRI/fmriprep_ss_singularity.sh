#!/bin/bash

# usage: ./fmriprep.sh </path/to/BIDS/dataset> <subject>

# source /data/perlman/moochie/resources/server_access/MRIenv/bin/activate.csh

ml singularity
ml freesurfer

export FREESURFER_HOME="/export/freesurfer/freesurfer-7.2.0/"
export TEMPLATEFLOWHOME="/scratch/claytons/tlbx/templateflow"
export SINGULARITYENV_TEMPLATEFLOW_HOME="/home/fmriprep/.cache/templateflow"

sub=$2

singularity run \
	--cleanenv \
	-B $1:/home/fmriprep \
	-B /home/claytons/.cache/fmriprep:/home/claytons/.cache/fmriprep \
	-B $1:/data \
	-B $1/derivatives:/out \
	-B $1/work:/work \
	-B $FREESURFER_HOME/.license:/opt/freesurfer/license.txt \
	/scratch/claytons/tlbx/singularity/fmriprep.simg \
	/data /out/fmriprep \
	participant \
	-w /work \
	--fs-license-file /opt/freesurfer/license.txt \
	--longitudinal \
	--skip_bids_validation \
	--use-aroma \
	--nthreads 16 \
	--low-mem \
	--mem-mb 15000 \
	--output-spaces MNIPediatricAsym:cohort-2:res-2 \
	--participant-label $sub 
