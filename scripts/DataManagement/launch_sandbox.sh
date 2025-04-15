#!/bin/bash

CPUs=$1
RAM=$2
TMP=$3

export LSF_DOCKER_VOLUMES="/storage1/fs1/perlmansusan/Active:/storage1/fs1/perlmansusan/Active $HOME:$HOME"

bsub -G compute-perlmansusan -J $USER-sandbox -a 'docker(continuumio/anaconda3:latest)' -Is -n $CPUs -R "select[mem>${RAM}GB && tmp>${TMP}GB] rusage[mem=${RAM}GB]" /bin/bash 
