#!/bin/bash
#BSUB -G compute-perlmansusan 
#BSUB -q general
#BSUB -m general
#BSUB -a 'docker(continuumio/anaconda3:latest)'
#BSUB -J test
#BSUB -n 4
#BSUB -R 'rusage[mem=10GB] select[mem>9000 && tmp>60]'
#BSUB -oo conda-test.log

echo 'Hello world'