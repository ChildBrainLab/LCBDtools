#!/bin/bash

# Usage:
# bash bidskit_p1.sh <path/to/MRI_data_folder/> <ses | no-ses>

# ex: bash bidskit_p1.sh /data/perlman/moochie/study_data/CARE/MRI_data/50021 ses

# cp -r $1 /data/perlman/moochie/analysis/$(basename $(dirname $1))/MRI_conversion_dir/sourcedata/

# first pass 
if [[ $2 == "ses" ]]; then
	docker run -it \
		--name BIDSKIT_p1_$3 \
		--cpu-shares 2048 \
		-v /data/perlman/moochie/analysis/$(basename $(dirname $1))/MRI_conversion_dir/:/dataset jmtyszka/bidskit \
		bidskit -d /dataset \
		--clean-conv-dir \
		--no-anon
elif [[ $2 == "no-ses" ]]; then
        docker run -it \
		--name BIDSKIT_p1 \
		--cpu-shares 2048 \
		-v $1:/dataset jmtyszka/bidskit \
		bidskit -d /dataset \
		--clean-conv-dir \
		--no-anon \
		--no-sessions
else
	echo "See usage notes to correctly use <ses | no-ses>."
	exit
fi

# append to proper BIDS participants.tsv
tail -n +2 /data/perlman/moochie/analysis/$(basename $(dirname $1))/MRI_conversion_dir/participants.tsv >> /data/perlman/moochie/analysis/$(basename $(dirname $1))/MRI_data_clean/participants.tsv

# copy the data from temp /sourcedata to proper BIDS /sourcedata
cp -r /data/perlman/moochie/analysis/$(basename $(dirname $1))/MRI_conversion_dir/sourcedata/* /data/perlman/moochie/analysis/$(basename $(dirname $1))/MRI_data_clean/sourcedata/

# clean the old sourcedata out
rm -r /data/perlman/moochie/analysis/$(basename $(dirname $1))/MRI_conversion_dir
mkdir /data/perlman/moochie/analysis/$(basename $(dirname $1))/MRI_conversion_dir
mkdir /data/perlman/moochie/analysis/$(basename $(dirname $1))/MRI_conversion_dir/sourcedata
