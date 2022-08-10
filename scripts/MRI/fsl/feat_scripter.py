"""
usage: python3 feat_scripter.py

Reads /home/USER/fsl_subs.txt (made by get_fsl_subs.py) and default CARE MRI_data_clean dir
Then parses the template in this script's directory, replacing certain values: 
    - subject number
    - session number
    - task name
    - run number
    - number of volumes
with the values gathered from their BIDS information, creating a first-level FSL script
for each individual scan in fsl_subs.txt
"""

import os
from os.path import join
import sys
import nibabel as nib
from tqdm import tqdm

f = open("/home/"+str(os.environ.get("USER"))+"/fsl_subs.txt", 'r')
fsl_subs = f.readlines()
f.close()

for sub_line in tqdm(fsl_subs):
    sub_line = sub_line.strip()
    # ex:
    # sub-50461/ses-0/func/sub-50461_ses-0_task-movieA_dir-PA_run-1_space-MNIPediatricAsym_cohort-2_res-2_desc-preproc_bold_smoothed7mm.nii.gz
    subject = sub_line.split('/')[0].split('-')[1]
    session = sub_line.split('/')[1].split('-')[1]
    task = os.path.split(sub_line)[1].split('_')[2].split('-')[1]
    run = os.path.split(sub_line)[1].split('_')[4].split('-')[1]
    mri = nib.load("/scratch/claytons/MRI_data_clean/derivatives/fmriprep/{}".format(sub_line))
    vols = str(mri.shape[3])
    voxs = str(mri.shape[0] * mri.shape[1] * mri.shape[2])

    #print(subject, session, task, run)

    with open(
        str(os.path.dirname(os.path.realpath(sys.argv[0])))+"/fsl_template_changeme_chpc.fsf", 'r')\
            as template:
        with open(
            "/scratch/claytons/MRI_data_clean/derivatives/fmriprep/{}/feat_script.fsf".format(
                os.path.split(sub_line)[0]), 'w')\
                    as outfile:

            for line in template:
                outfile.write(line.replace(
                    "SUBJECT", subject).replace(
                        "SESSION", session).replace(
                            "TASK", task).replace(
                                "RUN", run).replace(
                                    "VOLUMES", vols).replace(
                                        "VOXELS", voxs))

    print("Wrote:", "{}/feat_script.fsf".format(os.path.split(sub_line)[0]))
