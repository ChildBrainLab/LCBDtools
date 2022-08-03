#!/bin/bash

# Usage:
# bash bidskit_p1.sh <path/to/MRI_data_folder/> <ses | no-ses>

# ex: bash bidskit_p1.sh /data/perlman/moochie/analysis/EmoGrow/MRI_data_clean/ False

# first pass 
if [[ $2 == "ses" ]]; then
	docker run -it \
		--name BIDSKIT_p1 \
		--cpu-shares 2048 \
		-v $1:/dataset jmtyszka/bidskit \
		bidskit -d /dataset \
		--clean-conv-dir \
		--overwrite \
		--no-anon
elif [[ $2 == "no-ses" ]]; then
        docker run -it \
		--name BIDSKIT_p1 \
		--cpu-shares 2048 \
		-v $1:/dataset jmtyszka/bidskit \
		bidskit -d /dataset \
		--clean-conv-dir \
		--overwrite \
		--no-anon \
		--no-sessions
else
	echo "See usage notes to correctly use <ses | no-ses>."
fi
