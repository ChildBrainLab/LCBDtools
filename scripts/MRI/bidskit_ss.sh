#!/bin/bash

# Usage:
# bash bidskit_ss.sh <path/to/MRI_data_folder/> <subject> <ses | no-ses>

# ex: bash bidskit_p1.sh /data/perlman/moochie/analysis/EmoGrow/MRI_data_clean/ False

# first pass 
if [[ $3 == "ses" ]]; then
	docker run -it \
		--name BIDSKIT_$2 \
		--cpu-shares 2048 \
		-v $1:/dataset jmtyszka/bidskit \
		bidskit -d /dataset \
		--clean-conv-dir \
		--no-anon \
		--subject $2
elif [[ $3 == "no-ses" ]]; then
        docker run -it \
		--name BIDSKIT_$2 \
		--cpu-shares 2048 \
		-v $1:/dataset jmtyszka/bidskit \
		bidskit -d /dataset \
		--clean-conv-dir \
		--no-anon \
		--no-sessions \
		--subject $2
else
	echo "See usage notes to correctly use <ses | no-ses>."
fi
