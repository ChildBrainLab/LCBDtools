eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_rsa_compute

rsync -r /data/perlman/moochie/analysis/CARE/MRI_data_clean/ khalilt@login3.chpc.wustl.edu:/scratch/claytons/MRI_data_clean -aav --copy-links --size-only
