#!/bin/sh

# ----------- System Environment Variables-------------- #
PATH=$PATH:/usr/lib/ants:/opt/freesurfer/bin:/opt/freesurfer/tktools:/opt/freesurfer/mni/bin:/opt/fsl/lib:/opt/fsl/bin:/opt/c3d/bin:/usr/lib/afni/bin:/usr/local/miniconda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export HOSTNAME=104d06f00d8b
export OS=Linux
export FIX_VERTEX_AREA=
export CPATH=/usr/local/miniconda/include:
export LANG=C.UTF-8
export LC_ALL=C.UTF-8
export PYTHONNOUSERSITE=1
export AFNI_MODELPATH=/usr/lib/afni/models
export AFNI_IMSAVE_WARNINGS=NO
export AFNI_TTATLAS_DATASET=/usr/share/afni/atlases
export AFNI_PLUGINPATH=/usr/lib/afni/plugins
export C3DPATH=/opt/c3d/bin
export FSLDIR=/opt/fsl
export FSLOUTPUTTYPE=NIFTI_GZ
export FSLMULTIFILEQUIT=TRUE
export FSLLOCKDIR=
export FSLMACHINELIST=
export FSLREMOTECALL=
export FSLGECUDAQ=cuda.q
export LD_LIBRARY_PATH=/opt/fsl/lib:
export FSL_DEPS='libquadmath0;libnewimage.so;libmiscmaths.so'
export FREESURFER_HOME=/opt/freesurfer
export FSF_OUTPUT_FORMAT=nii.gz
export FUNCTIONALS_DIR=/opt/freesurfer/sessions
export LOCAL_DIR=/opt/freesurfer/local
export MINC_BIN_DIR=/opt/freesurfer/mni/bin
export MINC_LIB_DIR=/opt/freesurfer/mni/lib
export MNI_DIR=/opt/freesurfer/mni
export MNI_DATAPATH=/opt/freesurfer/mni/data
export MNI_PERL5LIB=/opt/freesurfer/mni/lib/perl5/5.8.5
export PERL5LIB=/opt/freesurfer/mni/lib/perl5/5.8.5
export SUBJECTS_DIR=/opt/freesurfer/subjects
export ANTSPATH=/usr/lib/ants
export MKL_NUM_THREADS=1
export OMP_NUM_THREADS=1
export HOME=/home/xcp_d

# Grab passed in subject
export SUBJECT=$1

# Define storage allocations areas of interest
export STORAGE_ALLOCATION=/storage1/fs1/perlmansusan/Active/
export FMRIPREP_DIR=${STORAGE_ALLOCATION}moochie/analysis/CARE/ME_fMRIPrep_data/derivatives/fmriprep/
export SCRATCH_DIR=${STORAGE_ALLOCATION}moochie/analysis/CARE/ME_scratch/
export LICENSE_DIR=${STORAGE_ALLOCATION}moochie/github/LCBDtools/scripts/MRI/fmriprep/
export CONFOUND_DIR=${STORAGE_ALLOCATION}moochie/analysis/CARE/custom_confounds/

# Alter the XCP_D entry point to be /bin/bash so it cooperated with bsub and XCP_D
# is not automatically called upon entering the docker image without options.
export LSF_DOCKER_ENTRYPOINT=/bin/bash

# Potentially unimportant variable, used to make sure the environmental variables 
# in the current shell transfer to the docker image being loaded but does not appear
# to work.
export LSF_DOCKER_PRESERVE_ENVIRONMENT=true

#export HOME="/scratch1/fs1/perlmansusan"

# -------- Call to bsub to run the bsub file ------------ #
export OUTPUT_DIR=${STORAGE_ALLOCATION}moochie/analysis/CARE/ME_XCP_khalil_data/
export LSF_DOCKER_VOLUMES="/storage1/fs1/perlmansusan/Active:/storage1/fs1/perlmansusan/Active /scratch1/fs1/perlmansusan:/scratch1/fs1/perlmansusan ${FMRIPREP_DIR}:/fmriprep ${OUTPUT_DIR}:/output ${LICENSE_DIR}:/freesurfer ${CONFOUND_DIR}:/custom_confounds /home/$USER:/home/$USER"
bsub -J $SUBJECT-xcp_d-khalil -oo logs/xcp_d/$SUBJECT-xcp_d-khalil.log -g /$USER/preprocessing < xcp-d_bsub_khalil.sh

export OUTPUT_DIR=${STORAGE_ALLOCATION}moochie/analysis/CARE/ME_XCP_kirk_data/
export LSF_DOCKER_VOLUMES="/storage1/fs1/perlmansusan/Active:/storage1/fs1/perlmansusan/Active /scratch1/fs1/perlmansusan:/scratch1/fs1/perlmansusan ${FMRIPREP_DIR}:/fmriprep ${OUTPUT_DIR}:/output ${LICENSE_DIR}:/freesurfer ${CONFOUND_DIR}:/custom_confounds /home/$USER:/home/$USER"
bsub -J $SUBJECT-xcp_d-kirk -oo logs/xcp_d/$SUBJECT-xcp_d-kirk.log -g /$USER/preprocessing < xcp-d_bsub_kirk.sh

export OUTPUT_DIR=${STORAGE_ALLOCATION}moochie/analysis/CARE/ME_XCP_kirk_data_2/
export LSF_DOCKER_VOLUMES="/storage1/fs1/perlmansusan/Active:/storage1/fs1/perlmansusan/Active /scratch1/fs1/perlmansusan:/scratch1/fs1/perlmansusan ${FMRIPREP_DIR}:/fmriprep ${OUTPUT_DIR}:/output ${LICENSE_DIR}:/freesurfer ${CONFOUND_DIR}:/custom_confounds /home/$USER:/home/$USER"
bsub -J $SUBJECT-xcp_d-kirk_2 -oo logs/xcp_d/$SUBJECT-xcp_d-kirk_2.log -g /$USER/preprocessing < xcp-d_bsub_kirk_2.sh
