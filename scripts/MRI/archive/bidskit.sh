#!/bin/bash

# make sourcedata, if not already exists
# sudo cp -r /data/perlman/moochie/study_data/CARE/MRI_data_clean_anon/sourcedata /data/perlman/moochie/study_data/CARE_MRI_data_clean/

#usage bash bidskit.sh /path/to/BIDS/folder

# first pass 
docker run -it \
	--name BIDSKIT_p1 \
	--cpu-shares 2048 \
	-v $1:/dataset jmtyszka/bidskit \
	bidskit -d /dataset \
	--clean-conv-dir \
	--overwrite \
	--no-anon

chmod -R u+rwx $1/code 

# for making our Protocol_Translator as we already know it for care...
# sudo cp /data/perlman/moochie/study_data/CARE/MRI_data_clean/Protocol_Translator.json /data/perlman/moochie/study_data/CARE/MRI_data_clean/code/Protocol_Translator.json

# second pass
docker run -it \
	--name BIDSKIT_p2 \
	--cpu-shares 2048 \
	-v $1:/dataset jmtyszka/bidskit \
	bidskit -d /dataset \
	--clean-conv-dir \
	--overwrite \
	--no-anon


