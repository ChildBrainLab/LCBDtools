#!/bin/bash

# usage: bash update_CARE_sourcedata.sh

date=$(date +%F)

# use better glob shell
shopt -s extglob
shopt -s nullglob

# clean up any existing transfer files if needed
# done bc we append to these files each time it runs,
# rather than writing over overtly. only files from the
# same date will be deleted

sourcedatafile="/data/perlman/moochie/study_data/CARE/CNDA_downloads/bids_logs/sourcedata_${date}.txt"
bidsdatafile="/data/perlman/moochie/study_data/CARE/CNDA_downloads/bids_logs/bidsdata_${date}.txt"
transferfile="/data/perlman/moochie/study_data/CARE/CNDA_downloads/bids_logs/transfersubs_${date}.txt"

if [ ! -d /data/perlman/moochie/study_data/CARE/CNDA_downloads/bids_logs ]
then
	mkdir /data/perlman/moochie/study_data/CARE/CNDA_downloads/bids_logs
fi

if [ -f $sourcedatafile ]
then
	rm $sourcedatafile
fi

if [ -f $bidsdatafile ]
then
	rm $bidsdatafile
fi

echo "Looking for unconverted sessions:"
echo "========================="

# get all in raw study dir
for ses in /data/perlman/moochie/study_data/CARE/CNDA_downloads/NP1166/*/*
do
	echo $(basename $(dirname $ses))/$(basename $ses) >> $sourcedatafile
done

# get all in BIDS sourcedata dir
touch $bidsdatafile
for ses in /data/perlman/moochie/analysis/${study}/MRI_data_clean/sourcedata/*/*
do
	# pretend they are named with sub- and ses- convention
	echo sub-$(basename $(dirname $ses))/ses-$(basename $ses) >> $bidsdatafile
done

# get the difference between the two lists
comm -23 <(sort $sourcedatafile) <(sort $bidsdatafile) > $transferfile

# for each in the diff list
for ses in `cat $transferfile`
do
	echo "Transferring: ${ses}"

	sourcesub=$(dirname $ses)
	sourceses=$(basename $ses)

	bidssub=${sourcesub#"sub-"}
	bidsses=${sourceses#"ses-"}

	# if subject folder doesn't exist in sourcedata, make it
	# but strip sub- from subject folder
	if [ ! -d "/data/perlman/moochie/analysis/CARE/MRI_data_clean/sourcedata/$bidssub/" ]
	then
		mkdir "/data/perlman/moochie/analysis/CARE/MRI_data_clean/sourcedata/$bidssub"
	fi

	# make session directory in subject folder, with any 'v' or 'V' character stripped
	mkdir "/data/perlman/moochie/analysis/CARE/MRI_data_clean/sourcedata/$bidssub/$bidsses"

	# for every scan (acquisition)
	#for acq in `ls /data/perlman/moochie/study_data/CARE/CNDA_downloads/NP1166/${ses}`
	#do

		# make the directory for it
		#mkdir "/data/perlman/moochie/analysis/CARE/MRI_data_clean/sourcedata/$bidssub/$bidsses/${acq}"
	
		# sym link all the things in acq/DICOM here
	#	ln -s -t /data/perlman/moochie/analysis/CARE/MRI_data_clean/sourcedata/$bidssub/$bidsses/ /data/perlman/moochie/study_data/CARE/CNDA_downloads/NP1166/${ses}/${acq}/DICOM/*
	
	#done

	# link all things in any acquisition/DICOM folder to the session directory
	ln -s -t /data/perlman/moochie/analysis/CARE/MRI_data_clean/sourcedata/$bidssub/$bidsses/ /data/perlman/moochie/study_data/CARE/CNDA_downloads/NP1166/${ses}/*/DICOM/*

	# symbolic link everything the session directory
	# ln -s /data/perlman/moochie/study_data/${study}/MRI_data/${ses}/!(*ignore*)/ /data/perlman/moochie/analysis/${study}/MRI_data_clean_2/sourcedata/$(dirname $ses)/$(basename $ses | tr -d v | tr -d V)/

	# copy session folder from raw study dir to sourcedata,
	# and truncate any characters 'v' or 'V' from the session dir
	# cp -r "/data/perlman/moochie/study_data/${study}/MRI_data/${sub}" "/data/perlman/moochie/analysis/${study}/MRI_data_clean/sourcedata/$(dirname $sub)/$(basename $sub | tr -d v | tr -d V)"

	# strip V from any visit numbers
	#for visit in `ls "/data/perlman/moochie/analysis/${study}/MRI_data_clean/sourcedata/${sub}" | grep "V"`
	#do
	#	mv "/data/perlman/moochie/analysis/${study}/MRI_data_clean/sourcedata/${sub}/${visit}" "/data/perlman/moochie/analysis/${study}/MRI_data_clean/sourcedata/${sub}/$(echo $visit | sed 's/V//')"
	#done

	# delete the child ignore folder

	echo "Session ${ses} transfer complete"
done

echo "Done"
