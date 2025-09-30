import os
from glob import glob


def check_subjects(session = None, output_space = "MNI152NLin6Asym", bids_folder = None, trad_fmriprep_folder = None, ME_fmriprep_folder = None, tedana_folder = None, xcp_folder = None):

    exclude = ['sub-50503', 'sub-50532', 'sub-50581', 'sub-50571', 'sub-50551']

    if bids_folder == None:
        bids_folder = '/storage1/fs1/perlmansusan/Active/moochie/analysis/CARE/ME_MRI_data/'
    if trad_fmriprep_folder == None:
        trad_fmriprep_folder = '/storage1/fs1/perlmansusan/Active/moochie/analysis/CARE/MRI_data/derivatives/fmriprep/'
    if ME_fmriprep_folder == None:
        ME_fmriprep_folder = '/storage1/fs1/perlmansusan/Active/moochie/analysis/CARE/ME_fMRIPrep_data/derivatives/fmriprep/'
    if tedana_folder == None:
        tedana_folder = '/storage1/fs1/perlmansusan/Active/moochie/analysis/CARE/ME_tedana_data/'
    if xcp_folder == None:
        xcp_folder = '/storage1/fs1/perlmansusan/Active/moochie/analysis/CARE/ME_XCP_khalil_data/'


    bids_sessions = glob(f"{bids_folder}sub-*/ses-{session}")
    trad_fmriprep_sessions = glob(f"{trad_fmriprep_folder}sub-*/ses-{session}")
    ME_fmriprep_sessions = glob(f"{ME_fmriprep_folder}sub-*/ses-{session}")
    tedana_sessions = glob(f"{tedana_folder}sub-*/ses-{session}")
    xcp_sessions = glob(f"{xcp_folder}sub-*/ses-{session}")

    bids_subjects = [folder.split("/")[-2] for folder in bids_sessions]
    trad_fmriprep_subjects = [folder.split("/")[-2] for folder in trad_fmriprep_sessions]
    ME_fmriprep_subjects = [folder.split("/")[-2] for folder in ME_fmriprep_sessions]
    tedana_subjects = [folder.split("/")[-2] for folder in tedana_sessions]
    xcp_subjects = [folder.split("/")[-2] for folder in xcp_sessions]

    print(f" -- Session {session} -- ")

    print(f"BIDSified subjects: {len(bids_subjects)}")
    print(f'ME fMRIPrep Processed Subjects: {len(ME_fmriprep_subjects)}')
    print(f'Traditional fMRIPrep Processed Subjects: {len(trad_fmriprep_subjects)}')
    print(f'Tedana Processed Subjects: {len(tedana_subjects)}')
    print(f'XCP-D Processed Subjects: {len(xcp_subjects)}')


    print('\n\nAvailable subjects to run traditional fMRIPrep on...')
    for subject in sorted(bids_subjects):
        if len(glob(f'/storage1/fs1/perlmansusan/Active/moochie/analysis/CARE/MRI_data/derivatives/fmriprep/sub-{subject}/ses-{session}/**/*{output_space}*.nii')) > 0:
            continue
        if subject in trad_fmriprep_subjects or subject in exclude: continue
        print(subject.split('-')[1])

    print('\n\nAvailable subjects to run ME fMRIPrep on...')
    for subject in sorted(trad_fmriprep_subjects):
        if subject in ME_fmriprep_subjects or subject in exclude: continue
        print(subject.split('-')[1])

    print('\n\nAvailable subjects to run Tedana on...')
    for subject in sorted(ME_fmriprep_subjects):
        if subject in tedana_subjects or subject in exclude: continue
        print(subject.split('-')[1])

    print('\n\nAvailable subjects to run XCP-D on...')
    for subject in sorted(tedana_subjects):
        if subject[:4] != 'sub-' or subject in exclude: continue
        if subject in xcp_subjects: continue
        print(subject.split('-')[1])


if __name__ == "__main__":
    for ses in [0, 1, 2]:
        check_subjects(ses)

