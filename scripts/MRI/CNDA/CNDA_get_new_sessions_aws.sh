#! /bin/bash

# usage: bash CNDA_get_new_sessions.sh 

#source /data/perlman/moochie/resources/server_access/MRIenv/bin/activate

echo "Looking for new sessions:"
echo "========================="

bash ./LCBDtools/scripts/MRI/CNDA/CNDA_get_sessions_aws.sh ./CNDA_downloads/CNDA_sessions_new.txt

# for any new sessions (diff between old and new)
# run python emailer to remind RAs to go enter usability

# if the new file exists
if [[ -f ./CNDA_downloads/CNDA_sessions_new.txt ]]; then
	
	# and if it has more lines than the original one
	if [[ $(wc -l < ./CNDA_downloads/CNDA_sessions_new.txt) -ge $(wc -l < ./CNDA_downloads/CNDA_sessions.txt) ]]; then

			
		for new_session in `comm -23 <(sort "./CNDA_downloads/CNDA_sessions_new.txt") <(sort "./CNDA_downloads/CNDA_sessions.txt")`
		do
			python LCBDtools/scripts/MRI/CNDA/email_new_CNDA_session_aws.py $new_session
		done

		aws s3 rm s3://moochie/study_data/CARE/CNDA_downloads/CNDA_sessions.txt
		aws s3 cp ./CNDA_downloads/CNDA_sessions_new.txt s3://moochie/study_data/CARE/CNDA_downloads/CNDA_sessions.txt

	# if it doesn't, something went wrong (probably fail to reach CNDA) and just skip this time around by removing new file
	else
		aws s3 rm s3://moochie/study_data/CARE/CNDA_downloads/CNDA_sessions_new.txt
	fi

fi