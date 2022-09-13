#!/bin/bash

for sub in `cat $1`
do 
	fsleyes render -of $(basename $(dirname $(dirname $(dirname $(dirname $(dirname $sub)))))).png \
	$(dirname $(dirname $sub))/mean_func.nii.gz $(dirname $sub)/zstat1.nii.gz -cm brain_colours_flow \
	-in linear -ll -cr -2 2 -ic -cmr 1024
done
