#!/bin/bash

# Usage:
# ./bidskit_p1.sh <path/to/MRI_data_folder/>

# first pass 
docker run -it \
	--name BIDSKIT_p1 \
	--cpu-shares 2048 \
	--memory 31458000000 \
	-v $1:/dataset jmtyszka/bidskit \
	bidskit -d /dataset \
	--clean-conv-dir \
	--overwrite \
	--no-anon

