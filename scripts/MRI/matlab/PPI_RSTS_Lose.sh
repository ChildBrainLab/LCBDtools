#!/bin/bash

#usage: bash PPI_RSTS_Lose.sh <list_of_Subj.txt>

for sub in `cat $1`
do
	echo "Submitting: $sub"
	sbatch /home/claytons/LCBDtools/scripts/MRI/sbatch/PPI_RSTS_Lose_sbatch.sh $sub
done
