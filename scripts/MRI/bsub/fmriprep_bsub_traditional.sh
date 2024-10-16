#!/bin/sh 
#BSUB -G compute-perlmansusan
#BSUB -q general
#BSUB -m general
#BSUB -a 'docker(nipreps/fmriprep:latest)'
#BSUB -n 16
#BSUB -R 'rusage[mem=26GB] select[mem>25000 && tmp>250]'

cd /tmp/$JOBID.tmpdir

mkdir /tmp/$JOBID.tmpdir/scratch
mkdir /tmp/$JOBID.tmpdir/output

/opt/conda/envs/fmriprep/bin/fmriprep /input /tmp/$JOBID.tmpdir/output participant --participant-label sub-$SUBJECT -w /tmp/$JOBID.tmpdir/scratch --fs-license-file /freesurfer/license.txt --output-spaces MNI152NLin6Asym:res-2 MNI152NLin2009cAsym:res-2 --n_cpus 16 --mem 24 --low-mem --skip-bids-validation # MNIPediatricAsym:cohort-2:res-2

cp -r /tmp/$JOBID.tmpdir/output/. /output/

for file in `find /output/ -name *$SUBJECT*.gz` ; do
    gzip -d $file
done