#!/bin/bash 
#BSUB -G compute-perlmansusan
#BSUB -g /dennys/preprocessing
#BSUB -q general
#BSUB -m general
#BSUB -J movie-regressors
#BSUB -a 'docker(gcr.io/ris-registry-shared/fsl6:latest)'
#BSUB -n 8
#BSUB -oo logs/post_processing/movie-regressors.log
#BSUB -R 'rusage[mem=10GB] select[mem>10000 && tmp>50]'



LCBDtools=/storage1/fs1/perlmansusan/Active/moochie/github/LCBDtools/
#HOME=/home/$USER

OUTPUT_DIR=/storage1/fs1/perlmansusan/Active/moochie/analysis/CARE/ME_fMRIPrep_data/
bash $LCBDtools/scripts/MRI/fsl/place_cropped_movie_regs.sh $OUTPUT_DIR

OUTPUT_DIR=/storage1/fs1/perlmansusan/Active/moochie/analysis/CARE/MRI_data/
bash $LCBDtools/scripts/MRI/fsl/place_cropped_movie_regs.sh $OUTPUT_DIR