#!/bin/bash

# Usage:
# ./bids-validator.sh <path-to-bids-dataset>

docker run -ti --rm \
	-v $1:/data:ro \
	bids/validator /data \
	--name BIDS_validator \
	--cpu-shares 2048 \
	--memory 62916 \

