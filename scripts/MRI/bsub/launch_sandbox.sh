#!/bin/bash

export LSF_DOCKER_VOLUMES="/storage1/fs1/perlmansusan/Active:/storage1/fs1/perlmansusan/Active $HOME:$HOME"

bsub -G compute-perlmansusan -J $USER-sandbox -a 'docker(continuumio/anaconda3:latest)' -Is -n 8 -R 'select[mem>10GB && tmp>100]' /bin/bash 
