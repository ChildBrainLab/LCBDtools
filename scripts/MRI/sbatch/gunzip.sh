#!/bin/bash

#SBATCH --job-name unzip
#SBATCH --mail-type=END,FAIL 
#SBATCH --mail-user=claytons@wustl.edu
#SBATCH --nodes 1
#SBATCH --ntasks 1
#SBATCH --cpus-per-task 4
#SBATCH --mem 60G
#SBATCH --time 18:00:00
#SBATCH --output unzip.log

pwd; hostname; date

gzimage=$1

gzip -d -k $gzimage
