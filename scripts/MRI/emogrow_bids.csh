#!/bin/csh

bash bidskit_p1.sh /data/perlman/moochie/analysis/EmoGrow/MRI_data_clean no-ses | tee /data/perlman/moochie/analysis/EmoGrow/logs/1_bidskit_p1.log

rm -rf /data/perlman/moochie/analysis/EmoGrow/MRI_data_clean/code/

cp /data/perlman/moochie/analysis/EmoGrow/Protocol_Translator.json /data/perlman/moochie/analysis/EmoGrow/MRI_data_clean/code/Protocol_Translator.json

bash bidskit_p2.sh /data/perlman/moochie/analysis/EmoGrow/MRI_data_clean no-ses | tee /data/perlman/moochie/analysis/EmoGrow/logs/2_bidskit_p2.log
