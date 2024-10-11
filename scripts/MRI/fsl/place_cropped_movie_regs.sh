#!/bin/bash

# usage: bash placeblablabla.sh /path/to/bids/dir

bidsdir=$1
ratingdir=/storage1/fs1/perlmansusan/Active/moochie/analysis/CARE/

#ml fsl

#for sub in `/bin/ls -d $bidsdir/derivatives/fmriprep/sub*/ses-0/func/* | grep preproc_bold.nii.gz`
for sub in `find $bidsdir -name '*preproc_bold.nii' | sort -r`
do
	# the case that there are ratings in this functional folder
	if [[ $(/bin/ls -d $(dirname $sub) | grep AHKJ | grep rating | grep .txt) ]]
	then
		# do nothing
		echo "Skipping $sub"
	# the case the rating is not present
	else
		# get task name
		#sentence=$(basename $sub)
		#for word in ${sentence//_/ }; do
		#	if [[ "task-movie" == *"$word"* ]]
		#	then
		#		movie=$(echo $word | sed 's/task-//')
		#	fi
		#done
		
		IFS='_' read -ra array <<< $(basename $sub)
		for element in "${array[@]}"
		do
  			if [[ "task-movieA" == $element ]]
			then
				movie='A'
			fi
			if [[ 'task-movieB' == $element ]]
			then
				movie='B'
			fi
			if [[ 'task-movieC' == $element ]]
			then
				movie='C'
			fi
		done

		# get the number of volumes in the 4D smoothed file
		a=$(fslnvols $sub)
		
		# for each file in ratings-containing folder
		# if it matches the movie name
		# copy the head -n $a version of it to func
		for rating in `find $ratingdir -maxdepth 1 -name "*AHKJ*movie$movie*.txt"`
		do

			# copy the rating
			# there should probably be three now
			echo "Copying $(basename $rating): length $a"
			head -n $a $rating > $(dirname $sub)/$(basename $rating)
			echo "Done"

		done				
	fi
done

