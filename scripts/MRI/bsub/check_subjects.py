import os


def check_subjects(bids_folder = None, trad_fmriprep_folder = None, ME_fmriprep_folder = None, tedana_folder = None, xcp_folder = None):

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


    bids_subjects = next(os.walk(bids_folder))[1]
    trad_fmriprep_subjects = next(os.walk(trad_fmriprep_folder))[1]
    ME_fmriprep_subjects = next(os.walk(ME_fmriprep_folder))[1]
    tedana_subjects = next(os.walk(tedana_folder))[1]
    xcp_subjects = next(os.walk(xcp_folder))[1]

    print(f"BIDSified subjects: {len(bids_subjects)}")
    print(f'ME fMRIPrep Processed Subjects: {len(ME_fmriprep_subjects)}')
    print(f'Traditional fMRIPrep Processed Subjects: {len(trad_fmriprep_subjects)}')
    print(f'Tedana Processed Subjects: {len(tedana_subjects)}')
    print(f'XCP-D Processed Subjects: {len(xcp_subjects)}')


    print('\n\nAvailable subjects to run traditional fMRIPrep on...')
    for subject in sorted(bids_subjects):
        if subject[:4] != 'sub-': continue
        if subject in trad_fmriprep_subjects or subject in exclude: continue
        print(subject.split('-')[1])

    print('\n\nAvailable subjects to run ME fMRIPrep on...')
    for subject in sorted(bids_subjects):
        if subject[:4] != 'sub-': continue
        if subject in ME_fmriprep_subjects or subject in exclude: continue
        print(subject.split('-')[1])

    print('\n\nAvailable subjects to run Tedana on...')
    for subject in sorted(ME_fmriprep_subjects):
        if subject[:4] != 'sub-' or subject in exclude: continue
        if subject in tedana_subjects: continue
        print(subject.split('-')[1])

    print('\n\nAvailable subjects to run XCP-D on...')
    for subject in sorted(tedana_subjects):
        if subject[:4] != 'sub-' or subject in exclude: continue
        if subject in xcp_subjects: continue
        print(subject.split('-')[1])


if __name__ == "__main__":
    check_subjects()

