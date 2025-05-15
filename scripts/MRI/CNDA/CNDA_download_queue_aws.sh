#!/bin/bash

#source /data/perlman/moochie/resources/server_access/MRIenv/bin/activate

python ./LCBDtools/scripts/MRI/CNDA/CNDA_get_undownloaded_sessions_aws.py

cat ./CNDA_downloads/CNDA_download_queue.txt | while read line; do

	echo $line
	# get CNDA session label and visit label
	arline=($line)
	CNDAses=${arline[0]}
	visit=${arline[1]}
	# strip V from visit
	visit="ses-"$(echo $visit | sed 's/V//')

	# pull xnat session
	bash LCBDtools/scripts/MRI/CNDA/xnat_pull_session_aws.sh $CNDAses	

	# get path to downloaded session
	#dlses=$(echo /data/perlman/moochie/study_data/CARE/CNDA_downloads/NP1166/*/$CNDAses)

	shopt -s nullglob

	for dlses in `echo ./CNDA_downloads/NP1166/*/$CNDAses`; do

		# if glob is null, just knowingly send email with error path
		# and then continue	
		if [ -z "$dlses" ]; then
			python ./LCBDtools/scripts/MRI/CNDA/email_downloaded_session_aws.py s3://moochie/study_data/CARE/CNDA_downloads/NP1166/$CNDAses
			continue
		fi

		# get subject folder name
		subname=$(basename $(dirname $dlses))
		pref="CARE_"
		subnum=$(echo ${subname#"$pref"} | tr -d '-')
		sub="sub-"$subnum

		# make target directory name
		#tses="/data/perlman/moochie/study_data/CARE/CNDA_downloads/NP1166/"$sub"/"$visit"/"
		tses="s3://moochie/study_data/CARE/CNDA_downloads/NP1166/"

		# move named subject folder to number-only
		# (merge using rsync and rm -rf)
		if [[ -d $tses/$sub ]]; then
			aws s3 rsync -av $dlses $tses/$sub
			aws s3 rm -rf $(dirname $dlses)
		else
			aws s3 mv --recursive $(dirname $dlses) $tses/$sub
		fi
	
		# move named session folder to visit-number
		# (merge using rsync and rm -rf)
		if [[ -d $tses/$sub/$visit ]]; then
			aws s3 rsync -av $tses/$sub/$(basename $dlses) $tses/$sub/$visit
			aws s3 rm -rf $tses/$sub/$(basename $dlses)
		else
			aws s3 mv $tses/$sub/$(basename $dlses) $tses/$sub/$visit
		fi
		
		# Convert UIH dcm to nii
		python LCBDtools/scripts/MRI/CNDA/enhanced_dcm_converter_aws.py $sub

		# Send email that session was downloaded
		python LCBDtools/scripts/MRI/CNDA/email_downloaded_session_aws.py $tses/$sub/$visit
	
	done
done
