#!/bin/sh


# ----------- System Environment Variables-------------- #

# Grab passed in subject
export SUBJECT=$1

# Define storage allocations areas of interest
export STORAGE_ALLOCATION=/storage1/fs1/perlmansusan/Active/
export BIDS_DIR=${STORAGE_ALLOCATION}moochie/analysis/CARE/ME_MRI_data/
export SCRATCH_DIR=${STORAGE_ALLOCATION}moochie/analysis/CARE/ME_scratch/
#export OUTPUT_DIR=${STORAGE_ALLOCATION}moochie/analysis/CARE/MRI_data/derivatives/fmriprep/
export LICENSE_DIR=${STORAGE_ALLOCATION}moochie/github/LCBDtools/scripts/MRI/fmriprep/
export OUTPUT_DIR=${STORAGE_ALLOCATION}moochie/analysis/CARE/MRI_data/fmriprep/

export LSF_DOCKER_VOLUMES="/storage1/fs1/perlmansusan/Active:/storage1/fs1/perlmansusan/Active /scratch1/fs1/perlmansusan:/scratch1/fs1/perlmansusan ${BIDS_DIR}:/input ${OUTPUT_DIR}:/output ${LICENSE_DIR}:/freesurfer /home/$USER:/home/$USER"

# Alter the fMRIprep entry point to be /bin/bash so it cooperated with bsub and fMRIprep
# is not automatically called upon entering the docker image without options.
export LSF_DOCKER_ENTRYPOINT=/bin/bash

# Potentially unimportant variable, used to make sure the environmental variables 
# in the current shell transfer to the docker image being loaded but does not appear
# to work.
export LSF_DOCKER_PRESERVE_ENVIRONMENT=true

# -------------- fMRIPrep Environmental Variables -------- #
# This section is used to set the fMRIprep environmental variables based off 
# nipreps/fmriprep:23.0.2. Normally this wouldn't be necessary when running 
# fmriprep on docker but due to RIS's environment all environmental variables
# are wiped when we load the docker image. This is all based off of fMRIprep's
# Dockerfile where they set ENV variables.
#
# NOTE: If fMRIprep stops working when updating to a new version, it could be
# due to one of these environmental variables changing or a new variable being added.
# Consider looking at the newer fMRIprep Dockerfile and comparing the ENV variables 
# set to environmental variables listed below.

export FREESURFER_HOME="/opt/freesurfer/bin/"
export PATH="$FREESURFER_HOME:$PATH"

export MAMBA_ROOT_PREFIX="/opt/conda"

export PATH="/opt/conda/envs/fmriprep/bin:$PATH" 
export UV_USE_IO_URING=0

export DEBIAN_FRONTEND="noninteractive" 
export LANG="en_US.UTF-8" 
export LC_ALL="en_US.UTF-8"

export OS="Linux" 
export FS_OVERRIDE=0 
export FIX_VERTEX_AREA="" 
export FSF_OUTPUT_FORMAT="nii.gz" 
export FREESURFER_HOME="/opt/freesurfer"

export SUBJECTS_DIR="$FREESURFER_HOME/subjects" 
export FUNCTIONALS_DIR="$FREESURFER_HOME/sessions" 
export MNI_DIR="$FREESURFER_HOME/mni" 
export LOCAL_DIR="$FREESURFER_HOME/local" 
export MINC_BIN_DIR="$FREESURFER_HOME/mni/bin" 
export MINC_LIB_DIR="$FREESURFER_HOME/mni/lib" 
export MNI_DATAPATH="$FREESURFER_HOME/mni/data"

export PERL5LIB="$MINC_LIB_DIR/perl5/5.8.5" 
export MNI_PERL5LIB="$MINC_LIB_DIR/perl5/5.8.5" 
export PATH="$FREESURFER_HOME/bin:$FREESURFER_HOME/tktools:$MINC_BIN_DIR:$PATH"

export PATH="/opt/afni-latest:$PATH"
export AFNI_IMSAVE_WARNINGS="NO" 
export AFNI_PLUGINPATH="/opt/afni-latest"

export MAMBA_ROOT_PREFIX="/opt/conda"

export PATH="/opt/conda/envs/fmriprep/bin:$PATH" 
export CPATH="/opt/conda/envs/fmriprep/include:$CPATH" 
export LD_LIBRARY_PATH="/opt/conda/envs/fmriprep/lib:$LD_LIBRARY_PATH"

export MKL_NUM_THREADS=1
export OMP_NUM_THREADS=1

export LANG="C.UTF-8" 
export LC_ALL="C.UTF-8" 
export PYTHONNOUSERSITE=1 
export FSLDIR="/opt/conda/envs/fmriprep" 
export FSLOUTPUTTYPE="NIFTI_GZ" 
export FSLMULTIFILEQUIT="TRUE" 
export FSLLOCKDIR=""
export FSLMACHINELIST=""
export FSLREMOTECALL=""
export FSLGECUDAQ="cuda.q"

export IS_DOCKER_8395080871=1

export PATH="/opt/workbench/bin_linux64:$PATH"
export LD_LIBRARY_PATH="/opt/workbench/lib_linux64:$LD_LIBRARY_PATH"
export LD_LIBRARY_PATH="/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH"

export PATH="/usr/bin/c3d_affine_tool:$PATH"

export HOME="/scratch1/fs1/perlmansusan"

# -------- Call to bsub to run the bsub file ------------ #

bsub -J $SUBJECT-fmriprep-traditional -oo logs/fmriprep/$SUBJECT-fmriprep-traditional.log -g /$USER/preprocessing < fmriprep_bsub_traditional.sh
