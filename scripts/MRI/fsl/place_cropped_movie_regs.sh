#!/bin/bash

# usage: bash placeblablabla.sh /path/to/bids/dir

bidsdir=$1

ml fsl

for sub in `/bin/ls -d $bidsdir/derivatives/fmriprep/sub*/ses-0/func/* | grep preproc_bold.nii.gz`
do
	# the case that there are ratings in this functional folder
	if [[ $(/bin/ls -d $(dirname $sub) | grep AHKJ | grep rating | grep .txt) ]]
	then
		# do nothing
		:
	# the case the rating is not present
	else
		# get task name
		sentence=$(basename $sub)
		for word in ${sentence//_/ }; do
			if [[ "task-movie" == *"$word"* ]]
			then
				movie=$(echo $word | sed 's/task-//')
			fi
		done
		
		# get the number of volumes in the 4D smoothed file
		a=$(fslnvols $sub)
		
		# for each file in ratings-containing folder
		# if it matches the movie name
		# copy the head -n $a version of it to func
		for rating in `/bin/ls -d /scratch/claytons/chpctransfer/* | grep "$movie" | grep ".txt"`
		do

			# copy the rating
			# there should probably be three now
			echo "Copying $(basename $rating):"
			head -n $a $rating > $(dirname $sub)/$(basename $rating)
			echo "Done"

		done				
	fi
done

