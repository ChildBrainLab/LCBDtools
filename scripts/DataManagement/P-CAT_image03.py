import os, sys, h5py
from glob import glob
import nibabel as nib
import pandas as pd

PCAT_audio_description = {
    "files": {
        "restructured_data/audio_data/interview/*/*_interview_audio.m4a": {
            "image_description": "Interview audio",
            "image_modality": "AUDIO"
        }
    }  
}

PCAT_eyetracker_description = {
    "files": {
        "restructured_data/eyetracker_data/jumble/*/*.*": {
            "image_description": "Jumble task eye tracking",
            "image_modality": "EYETRACKING"
        },
        "restructured_data/eyetracking_data/tsst/*/*.*": {
            "image_description": "TSST task eye tracking",
            "image_modality": "EYETRACKING"
        }
    }
}

PCAT_fNIRS_description = {
    "files": {
        "NIRS_data/*/*_DB-DOS/*/*.snirf": {
            "image_description": "fNIRS",
            "image_modality": "fNIRS",
            "image_file_format": "SNIRF",
            "scan_type": "Functional Near Infrared Spectroscopy(fNIRS)",
            "patient_position": "Sitting",
            "image_num_dimensions": 2, 
            "image_extent2": 20, 
            "image_unit1": "Second",
            "image_unit2": "channels",
            "image_resolution1": 1.0,
            "image_resolution2": 0.12820512820512822,
            "slice_timing": "N/A", 
            "channels": "[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]", 
            "fnirs_probe_config": "Forward and backward optodes", 
            "channel_wavelengths": "[760, 850]",
            "optodes": "['S1_D1 760', 'S1_D1 850', 'S2_D1 760', 'S2_D1 850', 'S2_D2 760', 'S2_D2 850', 'S3_D2 760', 'S3_D2 850', 'S4_D2 760', 'S4_D2 850', 'S5_D3 760', 'S5_D3 850', 'S6_D3 760', 'S6_D3 850', 'S7_D3 760', 'S7_D3 850', 'S7_D4 760', 'S7_D4 850', 'S8_D4 760', 'S8_D4 850']",
            "sampling_rate": 7.8, 
            "signal_type": "HbO",
            "probe_source_count": 8,
            "probe_detector_count": 4
        },
        "NIRS_data/*/*_Flanker/*/*.snirf": {
            "image_description": "fNIRS",
            "image_modality": "fNIRS",
            "image_file_format": "SNIRF",
            "scan_type": "Functional Near Infrared Spectroscopy(fNIRS)",
            "patient_position": "Sitting",
            "image_num_dimensions": 2, 
            "image_extent2": 20, 
            "image_unit1": "Second",
            "image_unit2": "channels",
            "image_resolution1": 1.0,
            "image_resolution2": 0.12820512820512822,
            "slice_timing": "N/A", 
            "channels": "[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]", 
            "fnirs_probe_config": "Forward and backward optodes", 
            "channel_wavelengths": "[760, 850]",
            "optodes": "['S1_D1 760', 'S1_D1 850', 'S2_D1 760', 'S2_D1 850', 'S2_D2 760', 'S2_D2 850', 'S3_D2 760', 'S3_D2 850', 'S4_D2 760', 'S4_D2 850', 'S5_D3 760', 'S5_D3 850', 'S6_D3 760', 'S6_D3 850', 'S7_D3 760', 'S7_D3 850', 'S7_D4 760', 'S7_D4 850', 'S8_D4 760', 'S8_D4 850']",
            "sampling_rate": 7.8, 
            "signal_type": "HbO",
            "probe_source_count": 8,
            "probe_detector_count": 4
        }
    }
}

PCAT_beh_description = {
    "files": {
        "restructured_data/task_data/dbdos/*/*.*": {
            "image_description": "DB-DOS task behavioral response data",
            "image_modality": "behavioral",
            "image_file_format": "CSV",
            "scan_type": "behavioral"
        },
        "restructured_data/task_data/flanker/*/*.*": {
            "image_description": "Flanker task behavioral response data",
            "image_modality": "behavioral",
            "image_file_format": "CSV",
            "scan_type": "behavioral"
        },
        "restructured_data/task_data/jumble/*/*.*": {
            "image_description": "Jumble task behavioral response data",
            "image_modality": "behavioral",
            "image_file_format": "CSV",
            "scan_type": "behavioral"
        },
        "restructured_data/task_data/posner/*/*.*": {
            "image_description": "Posner task behavioral response data",
            "image_modality": "behavioral",
            "image_file_format": "CSV",
            "scan_type": "behavioral"
        }
    }
}

PCAT_video_description = {
    "files": {
        "restructured_data/video_data/dbdos/*/*.mp4": {
            "image_description": "DB-DOS task video",
            "image_modality": "External Camera Photography",
        },
        "restructured_data/video_data/flanker/*/*.mp4": {
            "image_description": "Flanker task video",
            "image_modality": "External Camera Photography",
        },
        "restructured_data/video_data/interview/*/*.mp4": {
            "image_description": "Interview video",
            "image_modality": "External Camera Photography",
        },
        "restructured_data/video_data/tsst/*/*.mp4": {
            "image_description": "Tsst task video",
            "image_modality": "External Camera Photography",
        }
    }
}


image03_header = {
    'subjectkey': None, 
    'src_subject_id': None, 
    'interview_date': "", 
    'interview_age': 0, 
    'sex': None,
    'image_file': None,
    'image_description': None, 
    'image_modality': None, 
}

bids_directory = "/storage1/fs1/perlmansusan/Active/moochie/study_data/P-CAT/R56/"
guid_df = pd.read_excel(f"{bids_directory}NDA/PCAT_R56_WUSTL_guid_tracker.xlsx", engine="openpyxl", index_col = None)

# For each data type 
image03 = []
for data_description in [PCAT_audio_description, PCAT_eyetracker_description, PCAT_fNIRS_description, PCAT_beh_description, PCAT_video_description]:
            
    for file_identifier, description in data_description["files"].items():
        # Grab all files related to the file
        files = glob(f"{bids_directory}{file_identifier}") # Grab all examples of real file
        for file in files:
            file_image03 = image03_header.copy()
            file_image03['image_file'] = file

            # Break down file to subject and session/experiment ID numbers
            subject_id = file.split('/1')[1].split('/')[0]
            if "_P" in file:
                cp = "P"
            if "_C" in file:
                cp = "C"
            else:
                cp = "C"
            subject_id = f"1{subject_id}{cp}"

            # Find subject in NDA GUID output
            subject_col = guid_df.loc[guid_df['PID'] == subject_id]
            if len(subject_col.values) == 0:
                print(f"Subject not identifiable! ({subject_id} {cp}){file}")
                continue
            nda_col = subject_col.values[0]
            dob = nda_col[2]
            mob = nda_col[3]
            yob = nda_col[4]
            guid = nda_col[8]
            sex = nda_col[6]

            file_image03['subjectkey'] = guid
            file_image03['src_subject_id'] = subject_id 
            file_image03['sex'] = sex

            # Add file descriptions
            for key, value in description.items():
                file_image03[key] = value

            file_image03 = pd.DataFrame([file_image03])
            image03.append(file_image03)
                
final_image03 = pd.concat(image03, ignore_index = True)

final_image03.to_csv(f'{bids_directory}image03.csv')# Save the image03
 