#!/bin/bash

export LSF_DOCKER_VOLUMES="/storage1/fs1/perlmansusan/Active:/storage1/fs1/perlmansusan/Active /scratch1/fs1/perlmansusan:/scratch1/fs1/perlmansusan $HOME:$HOME"

bsub -G compute-perlmansusan -J $USER-sandbox -a 'docker(continuumio/anaconda3:latest)' -Is -n 16 -R 'rusage[mem=26GB] select[mem>25000 && tmp>250]' /bin/bash 
