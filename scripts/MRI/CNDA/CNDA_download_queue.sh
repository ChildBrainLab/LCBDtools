#!/bin/bash

source /data/perlman/moochie/resources/server_access/MRIenv/bin/activate

/usr/bin/python3.7 /data/perlman/moochie/github/LCBDtools/scripts/MRI/CNDA/CNDA_get_undownloaded_sessions.py

cat /data/perlman/moochie/study_data/CARE/CNDA_downloads/CNDA_download_queue.txt | while read line; do

	echo $line
	# get CNDA session label and visit label
	arline=($line)
	CNDAses=${arline[0]}
	visit=${arline[1]}
	# strip V from visit
	visit="ses-"$(echo $visit | sed 's/V//')

	# pull xnat session
	bash /data/perlman/moochie/github/LCBDtools/scripts/MRI/CNDA/xnat_pull_session.sh $CNDAses	

	# get path to downloaded session
	#dlses=$(echo /data/perlman/moochie/study_data/CARE/CNDA_downloads/NP1166/*/$CNDAses)

	shopt -s nullglob

	for dlses in `echo /data/perlman/moochie/study_data/CARE/CNDA_downloads/NP1166/*/$CNDAses`; do

		# if glob is null, just knowingly send email with error path
		# and then continue	
		if [ -z "$dlses" ]; then
			/usr/bin/python3.7 /data/perlman/moochie/github/LCBDtools/scripts/MRI/CNDA/email_doanloaded_session.py /data/perlman/moochie/study_data/CARE/CNDA_downloads/NP1166/$CNDAses
			continue
		fi

		# get subject folder name
		subname=$(basename $(dirname $dlses))
		pref="CARE_"
		subnum=$(echo ${subname#"$pref"} | tr -d '-')
		sub="sub-"$subnum

		# make target directory name
		#tses="/data/perlman/moochie/study_data/CARE/CNDA_downloads/NP1166/"$sub"/"$visit"/"
		tses="/data/perlman/moochie/study_data/CARE/CNDA_downloads/NP1166/"

		# move named subject folder to number-only
		# (merge using rsync and rm -rf)
		if [[ -d $tses/$sub ]]; then
			rsync -av $dlses $tses/$sub
			rm -rf $(dirname $dlses)
		else
			mv $(dirname $dlses) $tses/$sub
		fi
	
		# move named session folder to visit-number
		# (merge using rsync and rm -rf)
		if [[ -d $tses/$sub/$visit ]]; then
			rsync -av $tses/$sub/$(basename $dlses) $tses/$sub/$visit
			rm -rf $tses/$sub/$(basename $dlses)
		else
			mv $tses/$sub/$(basename $dlses) $tses/$sub/$visit
		fi
		
		# Convert UIH dcm to nii
		`dcm2niix $sub`

		# Send email that session was downloaded
		/usr/bin/python3.7 /data/perlman/moochie/github/LCBDtools/scripts/MRI/CNDA/email_downloaded_session.py $tses/$sub/$visit
	
	done
done
