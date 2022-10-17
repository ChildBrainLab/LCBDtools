#!/bin/bash

source /data/perlman/moochie/resources/server_access/MRIenv/bin/activate

/usr/bin/python3.7 /data/perlman/moochie/github/LCBDtools/scripts/MRI/CNDA/CNDA_get_undownloaded_sessions.py

cat /data/perlman/moochie/study_data/CARE/CNDA_download_queue.txt | while read line; do

	# get CNDA session label and visit label
	arline=($line)
	CNDAses=${arline[0]}
	visit=${arline[1]}

	# pull xnat session
	bash /data/perlman/moochie/github/LCBDtools/scripts/MRI/CNDA/xnat_pull_session.sh $CNDAses	

	# get path to downloaded session
	dlses=/bin/ls -d /data/perlman/moochie/study_data/CARE/CNDA_downloads/NP1166/*/$ses	

	# send email that session was downloaded
	/usr/bin/python3.7 /data/perlman/moochie/github/LCBDtools/scripts/MRI/CNDA/email_downloaded_session.py $dlses

	# get subject folder name
	#subname=$(basename $(dirname $dlses))	
	#pref="CARE_"
	#subnum=${subname#"$pref"}

	# move named subject folder to number-only
	#mv $(dirname $dlses) $(dirname $(dirname $dlses))/$subnum

	#echo $CNDAses
	#echo $visit


done
