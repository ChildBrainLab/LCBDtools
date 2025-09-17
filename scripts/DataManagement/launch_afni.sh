#!/bin/bash

CPUs=$1
RAM=$2
TMP=$3

export LSF_DOCKER_VOLUMES="/storage1/fs1/perlmansusan/Active:/storage1/fs1/perlmansusan/Active $HOME:$HOME"
PATH=$HOME:/linux_centos_7_64:$PATH

bsub -G compute-perlmansusan -J $USER-afni -a 'docker(gcr.io/ris-registry-shared/afni-tortoise)' -Is -n $CPUs -R "select[mem>${RAM}GB && tmp>${TMP}GB] rusage[mem=${RAM}GB]" /bin/bash 
