#!/bin/sh 
#BSUB -G compute-perlmansusan
#BSUB -q general
#BSUB -m general
#BSUB -a 'docker(nipreps/fmriprep:latest)'
#BSUB -n 16
#BSUB -R 'rusage[mem=30GB] select[mem>30000 && tmp>250]'

JOBFOLDER=`ls /tmp/`
HOMEDIR=`ls /home/`

cd /tmp/$JOBFOLDER/

mkdir /tmp/$JOBFOLDER/scratch
mkdir /tmp/$JOBFOLDER/output

/opt/conda/envs/fmriprep/bin/fmriprep /input /tmp/$JOBFOLDER/output participant --participant-label sub-$SUBJECT -w /tmp/$JOBFOLDER/scratch --fs-license-file /freesurfer/license.txt --output-spaces MNI152NLin6Asym:res-2 MNI152NLin2009cAsym:res-2 MNIPediatricAsym:cohort-2:res-2 --n_cpus 16 --mem 24 --low-mem --skip-bids-validation 

cp -r /tmp/$JOBFOLDER/output/. /output/

for file in `find /output/ -name *$SUBJECT*.gz` ; do
    gzip -d $file
done