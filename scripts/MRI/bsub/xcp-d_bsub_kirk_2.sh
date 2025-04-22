#!/bin/sh 
#BSUB -G compute-perlmansusan
#BSUB -q general
#BSUB -m general
#BSUB -a 'docker(pennlinc/xcp_d:latest)'
#BSUB -n 16
#BSUB -R 'rusage[mem=26GB] select[mem>25000 && tmp>250]'

TMP_DIR=`ls /tmp/`

mkdir /tmp/$TMP_DIR/scratch

cd /tmp/$TMP_DIR/scratch

mkdir /tmp/$TMP_DIR/output

/usr/local/miniconda/bin/xcp_d /fmriprep /tmp/$TMP_DIR/output participant \
    --participant-label $SUBJECT \
    -w /tmp/$TMP_DIR/scratch \
    --low-mem \
    --fs-license-file $LICENSE_DIR\license.txt \
    --mode none \
    --input-type fmriprep \
    --file-format nifti \
    --despike y \
    -p 36P \
    --smoothing 0 \
    --motion-filter-type none \
    -r 40 \
    -f 0.3 \
    --min-time 0 \
    --output-type censored \
    --min-coverage 0.25 \
    --abcc-qc n \
	--combine-runs n \
	--linc-qc n \
	--warp-surfaces-native2std  n 

cp -r /tmp/$TMP_DIR/output/. /output/


for file in `find /output/ -name *$SUBJECT*.gz` ; do
    gzip -d $file
done