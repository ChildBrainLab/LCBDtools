#!/bin/bash

# Usage:
# bash bidskit.sh <path/to/MRI_data_folder/> <subject> <ses | no-ses>

# example: bash bidskit.sh /data/perlman/moochie/analysis/EmoGrow/MRI_data_clean/ no-ses
# example: b ash bidskit.sh /data/perlman/moochie/analysis/CARE/MRI_data_clean/ ses

# first pass 
if [[ $3 == "ses" ]]; then
	docker run \
		--name BIDSKIT_$2 \
		--cpu-shares 2048 \
		-v $1:/dataset jmtyszka/bidskit \
		bidskit -d /dataset \
		--clean-conv-dir \
		--no-anon \
		--subject $2 &
elif [[ $3 == "no-ses" ]]; then
        docker run \
		--name BIDSKIT_$2 \
		--cpu-shares 2048 \
		-v $1:/dataset jmtyszka/bidskit \
		bidskit -d /dataset \
		--clean-conv-dir \
		--no-anon \
		--no-sessions \
		--subject $2 &
else
	echo "See usage notes to correctly use <ses | no-ses>."
fi
