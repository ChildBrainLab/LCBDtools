#!/bin/bash

#SBATCH --job-name fsl_susan
#SBATCH --mail-type=END,FAIL 
#SBATCH --mail-user=claytons@wustl.edu
#SBATCH --nodes 1
#SBATCH --ntasks 1
#SBATCH --cpus-per-task 4
#SBATCH --mem 60G
#SBATCH --time 24:00:00
#SBATCH --output susan.log

pwd; hostname; date

module load fsl

export OPENBLAS_NUM_THREADS=1

f=$1

ext="${f#*.}"
fname="${f%.$ext}"
funcdir=$(dirname $f)

substr="desc-preproc_bold"
repl="boldref"
ref=$(echo "$f" | sed "s/$substr/$repl/")
#ref="$(ls $funcdir | grep "boldref")"

substr="preproc_bold"
repl="brain_mask"
mask=$(echo "$f" | sed "s/$substr/$repl/")
#mask="$(ls $funcir | grep "mask.nii.gz")"

substr="preproc_bold"
repl="brain_mask_inverse"
inv=$(echo "$f" | sed "s/$substr/$repl/")
#inv="$(ls $funcdir | grep "mask_inverse.nii.gz")"

a=$(fslstats $ref -k $mask -p 50)
b=$(fslstats $ref -k $inv -p 50)
c=$(echo "0.75*(${a}-${b})" | bc)

# susan <input> <bt> <dt> <dim> <use_median> <n_usans> [<usan1> <bt1> [<usan2> <bt2>]] <output>

susan $f $c 7 3 0 0 "${fname}_susan.${ext}"
