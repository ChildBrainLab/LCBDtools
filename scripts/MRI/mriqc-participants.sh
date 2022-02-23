#!/bin/bash

# usage: ./mriqc-participants </data/perlman/.../path/to/BIDS/dataset/>

docker run -it --rm \
	--name MRIQC \
	--cpu-shares 1024 \
	-v $1:/data:ro \
	-v $1/derivatives/MRIQC/:/out poldracklab/mriqc:0.16.1 \
	/data /out participant 
