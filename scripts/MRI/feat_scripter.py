import os
from os.path import join

with open("/home/claytons/fsl_subs.txt", 'r') as fsl_subs:
    with open("/home/claytons/fsl_template_changeme_chpc.fsf", 'r') as template:
        for sub_line in fsl_subs:

            # sub-50461/ses-0/func/sub-50461_ses-0_task-movieA_dir-PA_run-1_space-MNIPediatricAsym_cohort-2_res-2_desc-preproc_bold_smoothed7mm.nii.gz
            subject = sub_line.split('/')[0].split('-')[1]
            session = sub_line.split('/')[1].split('-')[1]
            task = os.path.split(sub_line)[1].split('_')[2].split('-')[1]
            run = os.path.split(sub_line)[1].split('_')[4].split('-')[1]
            
            #print(subject)
            #print(session)
            #print(task)
            #print(run)
            
            with open("/scratch/claytons/MRI_data_clean/derivatives/fmriprep/{}/.feat_script.fsf".format(os.path.split(sub_line)[0]), 'w') as outfile:

                for line in template:
                    outfile.write(line.replace("SUBJECT", subject).replace("SESSION", session).replace("TASK", task).replace("RUN", run))

            print("Wrote:", "{}/.feat_script.fsf".format(os.path.split(sub_line)[0]))
