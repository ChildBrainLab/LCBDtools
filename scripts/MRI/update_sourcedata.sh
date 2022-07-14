#! /bin/bash

# usage: bash update_sourcedata.sh <study_name>

study=$1
date=$(date +%F)
user=$USER

echo "Looking for new subjects:"
echo "========================="

ls "/data/perlman/moochie/study_data/${study}/MRI_data/" | grep -v "pilot" > "/home/usr/${user}/${study}_source_${date}.txt"

ls "/data/perlman/moochie/analysis/${study}/MRI_data_clean/sourcedata/" > "/home/usr/${user}/${study}_bids_${date}.txt"

# sed -e s/sub-//g -i "/home/usr/${user}/${study}_bids_${date}.txt"

comm -23 <(sort "/home/usr/${user}/${study}_source_${date}.txt") <(sort "/home/usr/${user}/${study}_bids_${date}.txt") > "/home/usr/${user}/${study}_transfer_subs_${date}.txt"

for sub in `cat "/home/usr/${user}/${study}_transfer_subs_${date}.txt"`
do
	echo "Transferring: ${sub}"
	# copy it from raw to sourcedata
	cp -r "/data/perlman/moochie/study_data/${study}/MRI_data/${sub}" "/data/perlman/moochie/analysis/${study}/MRI_data_clean/sourcedata/"
	# strip V from any visit numbers
	for visit in `ls "/data/perlman/moochie/analysis/${study}/MRI_data_clean/sourcedata/${sub}" | grep "V"`
	do
		mv "/data/perlman/moochie/analysis/${study}/MRI_data_clean/sourcedata/${sub}/${visit}" "/data/perlman/moochie/analysis/${study}/MRI_data_clean/sourcedata/${sub}/$(echo $visit | sed 's/V//')"
	done

	# delete the child ignore folder

	echo "Subject ${sub} complete"
done
	
echo "Looking for new sessions in existing subjects:"
echo "=============================================="

for sub in `comm -12 <(sort "/home/usr/${user}/${study}_source_${date}.txt") <(sort "/home/usr/${user}/${study}_bids_${date}.txt")`
do
	raw_visits=$(ls "/data/perlman/moochie/study_data/${study}/MRI_data/${sub}" | grep -v "p" | sort | sed 's/V//')
	#echo "Source visits: ${raw_visits}"
	
	bids_visits=$(ls "/data/perlman/moochie/analysis/${study}/MRI_data_clean/sourcedata/${sub}" | sort)
	#echo "BIDS visits: ${bids_visits}"

	for visit in `comm -23 <(echo $raw_visits) <(echo $bids_visits)`
	do
		echo "Transferring subject ${sub} visit V${visit}:"
		cp -r "/data/perlman/moochie/study_data/${study}/MRI_data/${sub}/V${visit}" "/data/perlman/moochie/analysis/${study}/MRI_data_clean/sourcedata/${sub}/${visit}"
		echo "Subject ${sub} visit V${visit} complete"
	done
done
		
