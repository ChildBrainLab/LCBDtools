#! /bin/bash

# usage: bash CNDA_get_new_sessions.sh 

#source /data/perlman/moochie/resources/server_access/MRIenv/bin/activate

# clean up any existing transfer files if needed
#if [[ -f "/data/perlman/moochie/study_data/CARE/CNDA_sessions_new.txt" ]]; then
#
#	rm /data/perlman/moochie/study_data/CARE/CNDA_sessions.txt
#	mv /data/perlman/moochie/study_data/CARE/CNDA_sessions_new.txt /data/perlman/moochie/study_data/CARE/CNDA_sessions.txt
#
#fi

echo "Looking for new sessions:"
echo "========================="

bash /data/perlman/moochie/github/LCBDtools/scripts/MRI/CNDA/CNDA_get_sessions.sh /data/perlman/moochie/study_data/CARE/CNDA_downloads/CNDA_sessions_new.txt

# for any new sessions (diff between old and new)
# run python emailer to remind RAs to go enter usability

# if the new file exists
if [[ -f /data/perlman/moochie/study_data/CARE/CNDA_downloads/CNDA_sessions_new.txt ]]; then
	
	# and if it has more lines than the original one
	if [[ $(wc -l < /data/perlman/moochie/study_data/CARE/CNDA_downloads/CNDA_sessions_new.txt) -ge $(wc -l < /data/perlman/moochie/study_data/CARE/CNDA_downloads/CNDA_sessions.txt) ]]; then

			
		for new_session in `comm -23 <(sort "/data/perlman/moochie/study_data/CARE/CNDA_downloads/CNDA_sessions_new.txt") <(sort "/data/perlman/moochie/study_data/CARE/CNDA_downloads/CNDA_sessions.txt")`
		do
			/usr/bin/python3.7 /data/perlman/moochie/github/LCBDtools/scripts/MRI/CNDA/email_new_CNDA_session.py $new_session
		done

		rm /data/perlman/moochie/study_data/CARE/CNDA_downloads/CNDA_sessions.txt
		mv /data/perlman/moochie/study_data/CARE/CNDA_downloads/CNDA_sessions_new.txt /data/perlman/moochie/study_data/CARE/CNDA_downloads/CNDA_sessions.txt

	# if it doesn't, something went wrong (probably fail to reach CNDA) and just skip this time around by removing new file
	else
		rm /data/perlman/moochie/study_data/CARE/CNDA_downloads/CNDA_sessions_new.txt
	fi

fi
