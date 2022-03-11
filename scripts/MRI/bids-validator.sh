docker run -ti --rm \
	-v /data/perlman/moochie/study_data/CARE/MRI_data_clean:/data:ro \
	bids/validator /data \
	--name BIDS_validator \
	--cpu-shares 2048 \
	--memory 62916 \

