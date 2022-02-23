#Usage: python3.8 rename_sequences.py /full/path/to/CNDAzip/ Vx

import pydicom as pyd
import zipfile
import os
from os import listdir, rename, mkdir
from os.path import join
import sys
import shutil


if len(sys.argv) != 3:
    print("This script requires 2 additional arguments:\n",
        "1. zip filepath\n",
        "2. Vx")
    print("If there is no visit-data available, enter Vx as 'None'.")
    print("Usage: python3.8 rename_sequences.py /full/path/to/CNDAzip/ Vx")
    raise Exception
    sys.exit(3)

zippath = sys.argv[1]
visit = sys.argv[2]
if visit == "None":
    visit = None

if zippath[-4:] != ".zip":
    print("Please enter the full path to the .zip as argument 1.")
    raise FileNotFoundError
    sys.exit(3)

if not os.path.isfile(zippath):
    print("Please enter the full path to the .zip as argument 1.")
    raise FileNotFoundError
    sys.exit(3)

mri_dir = os.path.split(zippath)[0]

if os.path.isdir(join(mri_dir, "temp_dir")):
    print("Warning: Temp dir already exists - deleting.")
    shutil.rmtree(join(mri_dir, "temp_dir"))

# extract all to "temp_dir"
print("Extracting zip file:")
with zipfile.ZipFile(zippath, 'r') as zip_ref:
    zip_ref.extractall(join(mri_dir, "temp_dir"))

subfolders = os.listdir(join(mri_dir, "temp_dir"))
if len(subfolders) != 1:
    print("Only one scan folder should be downloaded at a time. Exiting.")
    raise Exception
    sys.exit(3)

subject_name = os.listdir(join(mri_dir, "temp_dir"))

if len(subject_name[0].split('_')) > 1:
    subject_name = subject_name[0].split('_')[1:]

    # cleanup of subject name to replace hyphens and stuff
    subject_name_str = ""
    for part in subject_name:
        subject_name_str += part

subject_name = subject_name_str.replace('-', '')

print("Subject name:", subject_name)

# move temp dir subfolders to subject name
shutil.move(
    join(mri_dir, "temp_dir", os.listdir(join(mri_dir, "temp_dir"))[0]),
    join(mri_dir, "temp_dir", subject_name))

CNDAids = os.listdir(join(mri_dir, "temp_dir", subject_name))

if len(CNDAids) != 1:
    print("More than one session downloaded in same zip folder. Exiting.")
    raise Exception
    sys.exit(3)

# if we are using a visit num
if visit is not None:
    shutil.move(
        join(mri_dir, "temp_dir", subject_name, CNDAids[0]),
        join(mri_dir, "temp_dir", subject_name, visit))

    folder = join(mri_dir, "temp_dir", subject_name, visit)
else:
    shutil.move(
        join(mri_dir, "temp_dir", subject_name, CNDAids[0]),
        join(mri_dir, "temp_dir", subject_name))

    folder = join(mri_dir, "temp_dir", subject_name)

# bring up contents from temp dir

new_mri_dir = join(os.path.split(mri_dir)[0], "MRI_data")

if not os.path.isdir(
    join(new_mri_dir, subject_name)): 
        shutil.copytree(
            join(mri_dir, "temp_dir", subject_name),
            join(new_mri_dir, subject_name))
else:
    print("Subject MRI folder already existed, only copying visit folder.")
    shutil.copytree(
        join(mri_dir, "temp_dir", subject_name, visit),
        join(new_mri_dir, subject_name, visit))

print("Moved successfully.")

# delete temp dir
print("Deleting temp files.")
shutil.rmtree(join(mri_dir, "temp_dir"))
folder = folder.replace("/temp_dir", "")
# delete OG zip
#print("Removing .zip file.")
print("Skipping removal of .zip file. Do it manually if it's in MRI_data! Or place in CNDA_download_repo.")
# os.remove(zippath)
# rename Zip to be subject_visit
print("Renaming ", zippath, "to ", subject_name+"_"+visit, ":")
shutil.move(
    zippath,
    join(os.path.split(zippath)[0], subject_name+"_"+visit)+".zip")


folder = folder.replace(mri_dir, new_mri_dir)

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
