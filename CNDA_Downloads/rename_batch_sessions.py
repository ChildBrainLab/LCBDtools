#Usage: python3.8 rename_batch_sessions.py /full/path/to/CNDAfolder/

import pydicom as pyd
import zipfile
import os
from os import listdir, rename, mkdir
from os.path import join
import sys
import shutil
from datetime import date


def unzip(zippath, out_folder):
    with zipfile.ZipFile(join(zippath, out_folder), 'r') as zip_ref:
        zip_ref.extractall(join(mri_dir, "temp_dir", out_folder))
    return(join(mri_dir,"temp_dir", out_folder))

def main():
    if len(sys.argv) != 2:
        print("This script requires 1 additional argument: CNDApath")
        raise Exception
        sys.exit(3)

    CNDApath = sys.argv[1]
    # visit = sys.argv[2]

    # if CNDApath[-4:] != ".zip":
    #     print("Please enter the full path to the .zip as argument 1.")
    #     raise FileNotFoundError
    #     sys.exit(3)

    if not os.path.isdir(CNDApath):
        print("Please enter the full path to the CNDA dir as argument.")
        raise FileNotFoundError
        sys.exit(3)

    mri_dir = join(os.path.split(zippath)[0], "MRI_data_raw")
    if not os.path.isdir(mri_dir):
        print("Error: ", mri_dir, " does not exist.")
        raise FileNotFoundError
        sys.exit(3)

    zips = []
    dates = []
    session_folders = []

    for f in os.listdir(CNDApath):
        if f[-4:] != ".zip":
            continue

        try:
            dates.append(
                datetime.fromisoformat(
                    "20"+f.split('-')[0].replace('_', '-')))
        except:
            print('Failure:', f)
            continue

        try:
            zips.append(join(mri_dir, "temp_dir", f))
        except:
            print("Failure:", f)
            dates.pop(-1)
            continue

        try:
            session_folders.append(
                unzip(join(mri_dir, "temp_dir"), f)
        except:
            print("Failure:", f)
            dates.pop(-1)
            zips.pop(-1)
            continue

        except:
            print("Error. Haulting transfer.")
            sys.exit(3)

    subject_session_dict = {}

    for f in session_folders:
        try:
            subject_session_dict[os.path.split(f)[1].split('_')[1:]] =


subfolders = os.listdir(join(mri_dir, "temp_dir"))
if len(subfolders) != 1:
    print("Only one folder should be downloaded at a time. Exiting.")
    raise Exception
    sys.exit(3)

try:
    subject_name = os.listdir(join(mri_dir, "temp_dir"))[0].split('_')[1:]

    subject_name_str = ""
    for part in subject_name:
        subject_name_str += part
    subject_name = subject_name_str


    shutil.move(
        join(mri_dir, "temp_dir", os.listdir(join(mri_dir, "temp_dir"))[0]),
        join(mri_dir, "temp_dir", subject_name))

    shutil.move(
        join(mri_dir, "temp_dir", subject_name),
        join(mri_dir, subject_name))

    os.rmdir(join(mri_dir, "temp_dir"))
    os.remove(zippath)

    CNDAids = os.listdir(join(mri_dir, subject_name))

    if len(CNDAids) != 1:
        print("More than one session downloaded in same zip folder. Exiting.")
        raise Exception
        sys.exit(3)

    shutil.move(
        join(mri_dir, subject_name, CNDAids[0]),
        join(mri_dir, subject_name, visit))

    folder = join(mri_dir, subject_name, visit)

except:
    print("Failure.")
    sys.exit(3)

try:
    seqs = listdir(folder)
    mkdir(folder + '/ignore')
except:
    raise Warning('Folder not found. Did you enter the full filepath to the folder?')

for seq_num in seqs:
    try:
        if os.path.isdir(folder + '/{0}/SNAPSHOTS'.format(seq_num)):
            shutil.rmtree(folder + '/{0}/SNAPSHOTS'.format(seq_num))

        dicoms = listdir(folder + '/{0}/DICOM'.format(seq_num))
        temp_header = pyd.filereader.dcmread(folder + '/{0}/DICOM/{1}'.format(seq_num,dicoms[0]))
        seq_name = seq_num + '_' + temp_header['0x08','103e'].value
        rename(folder + '/{0}'.format(seq_num), folder + '/{0}'.format(seq_name))
    except:

        raise Warning('Sequence number {0} does not have dicoms and could not be renamed. Moved to ignore folder.'.format(seq_num))
        rename(folder + '/{0}'.format(seq_num), folder + '/ignore/{0}'.format(seq_num))
