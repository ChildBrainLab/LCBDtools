#!/bin/bash

# make sourcedata, if not already exists
# sudo cp -r /data/perlman/moochie/study_data/CARE/MRI_data_clean_anon/sourcedata /data/perlman/moochie/study_data/CARE_MRI_data_clean/

# first pass 
docker run -it \
	-v /data/perlman/moochie/study_data/CARE/MRI_data_clean/:/dataset jmtyszka/bidskit \
	bidskit -d /dataset \
	--name BIDSKIT_p1 \
	--cpu-shares 2048 \
	--memory 62916 \
	--clean-conv-dir \
	--overwrite \
	--no-anon

# chmod -R 777 /data/perlman/moochie/study_data/CARE/MRI_data_clean/code 

# for making our Protocol_Translator as we already know it for care...
# sudo cp /data/perlman/moochie/study_data/CARE/MRI_data_clean/Protocol_Translator.json /data/perlman/moochie/study_data/CARE/MRI_data_clean/code/Protocol_Translator.json

# second pass
docker run -it \
	-v /data/perlman/moochie/study_data/CARE/MRI_data_clean/:/dataset jmtyszka/bidskit \
	bidskit -d /dataset \
	--name BIDSKIT_p2 \
	--cpu-shares 2048 \
	--memory 62916 \
	--clean-conv-dir \
	--overwrite \
	--no-anon


