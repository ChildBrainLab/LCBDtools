#!/bin/bash

# Usage:
# ./bids-validator.sh <path-to-bids-dataset>

docker run -ti --rm \
	--name BIDS_validator \
	-v $1:/data:ro \
	bids/validator /data \
	# --memory 31458000000

