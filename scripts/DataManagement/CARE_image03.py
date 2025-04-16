import os, sys, h5py
from glob import glob
import nibabel as nib



CARE_MRI_description = {
    "anat/sub-*_ses-*_T1w.nii.gz": {
        'image_description': 'DTI',
        'image_modality': 'MRI',
        'image_file_format': 'NIfTI',
        'scan_type': 'MR structural (MP2RAGE)',
        'mri_repetition_time_pd': 2.3,
        'mri_echo_time_pd': '0.00341',
        'flip_angle': '7',
        'image_slice_thickness': 1.0,
        'acquisition_matrix': '[240, 208]',
        'mri_field_of_view_pd': '[199.68744278, 208.0, 212.99993896]',
        'recieve_coil': 'HeadNeck_64',
        'patient_position': 'Laying down on back',
        'image_num_dimensions': 3,
        'image_extent1': 240,
        'image_extent2': 208,
        'image_extent3': 256,
        'image_unit1': 'Millimeters',
        'image_unit2': 'Millimeters',
        'image_unit3': 'Millimeters',
        'image_resolution1': 0.832031,
        'image_resolution2': 1.0,
        'image_resolution3': 0.832031,
        'image_orientation': 'Axial'
    },
    "func/sub-*_ses-*_task-movie*_echo-2_sbref.nii.gz": {
        'image_description': 'SBRef',
        'image_modality': 'fMRI',
        'image_file_format': 'NIfTI',
        'scan_type': 'fMRI',
        'mri_repetition_time_pd': 0.8,
        'mri_echo_time_pd': '0.03876',
        'flip_angle': '49',
        'image_slice_thickness': 3.0,
        'slice_acquisition': 1,
        'slice_timing': '[0, 0.0975, 0.195, 0.2925, 0.39, 0.4875, 0.585, 0.6825, 0.78, 0.8775, 0.975, 1.0725, 1.17, 1.2675, 1.365, 1.4625, 1.56, 1.6575, 1.755, 1.8525, 1.95, 2.0475, 2.145, 2.2425, 2.34, 2.4375, 2.535, 2.6325, 2.73,2.8275, 2.925, 3.0225, 3.12, 3.2175, 3.315, 3.4125, 3.51, 3.6075, 3.705, 3.8025]',
        'acquisition_matrix': '[68, 68]',
        'mri_field_of_view_pd': '[204.0, 204.0, 120.0]',
        'recieve_coil': 'HeadNeck_64',
        'patient_position': 'Laying down on back',
        'image_num_dimensions': 3,
        'image_extent1': 68,
        'image_extent2': 68,
        'image_extent3': 40,
        'image_unit1': 'Millimeters',
        'image_unit2': 'Millimeters',
        'image_unit3': 'Millimeters',
        'image_resolution1': 3.0,
        'image_resolution2': 3.0,
        'image_resolution3': 3.0,
        'image_orientation': 'Axial'
    },
    "func/sub-*_ses-*_task-movie*_echo-3_sbref.nii.gz": {
        'image_description': 'SBRef',
        'image_modality': 'fMRI',
        'image_file_format': 'NIfTI',
        'scan_type': 'fMRI',
        'mri_repetition_time_pd': 0.8,
        'mri_echo_time_pd': '0.06432',
        'flip_angle': '49',
        'image_slice_thickness': 3.0,
        'slice_acquisition': 1,
        'slice_timing': '[0, 0.0975, 0.195, 0.2925, 0.39, 0.4875, 0.585, 0.6825, 0.78, 0.8775, 0.975, 1.0725, 1.17, 1.2675, 1.365, 1.4625, 1.56, 1.6575, 1.755, 1.8525, 1.95, 2.0475, 2.145, 2.2425, 2.34, 2.4375, 2.535, 2.6325, 2.73,2.8275, 2.925, 3.0225, 3.12, 3.2175, 3.315, 3.4125, 3.51, 3.6075, 3.705, 3.8025]',
        'acquisition_matrix': '[68, 68]',
        'mri_field_of_view_pd': '[204.0, 204.0, 120.0]',
        'recieve_coil': 'HeadNeck_64',
        'patient_position': 'Laying down on back',
        'image_num_dimensions': 3,
        'image_extent1': 68,
        'image_extent2': 68,
        'image_extent3': 40,
        'image_unit1': 'Millimeters',
        'image_unit2': 'Millimeters',
        'image_unit3': 'Millimeters',
        'image_resolution1': 3.0,
        'image_resolution2': 3.0,
        'image_resolution3': 3.0,
        'image_orientation': 'Axial'
    },
    "func/sub-*_ses-*_task-movie*_echo-2_bold.nii.gz": {
        'image_description': 'fMRI',
        'image_modality': 'fMRI',
        'image_file_format': 'NIfTI',
        'scan_type': 'fMRI',
        'mri_repetition_time_pd': 0.8,
        'mri_echo_time_pd': '0.03876',
        'flip_angle': '49',
        'image_slice_thickness': 3.0,
        'slice_acquisition': 1,
        'slice_timing': '[0, 0.2925, 0.585, 0.0975, 0.39, 0.6825, 0.195, 0.4875, 0, 0.2925, 0.585, 0.0975, 0.39, 0.6825, 0.195, 0.4875, 0, 0.2925, 0.585, 0.0975, 0.39, 0.6825, 0.195, 0.4875, 0, 0.2925, 0.585, 0.0975, 0.39, 0.6825, 0.195, 0.4875, 0, 0.2925, 0.585, 0.0975, 0.39, 0.6825, 0.195, 0.4875]',
        'acquisition_matrix': '[68, 68]',
        'mri_field_of_view_pd': '[204.0, 204.0, 120.0]',
        'recieve_coil': 'HeadNeck_64',
        'patient_position': 'Laying down on back',
        'image_num_dimensions': 4,
        'image_extent1': 68,
        'image_extent2': 68,
        'image_extent3': 40,
        'image_unit1': 'Millimeters',
        'image_unit2': 'Millimeters',
        'image_unit3': 'Millimeters',
        'image_unit4': 'Seconds',
        'image_resolution1': 3.0,
        'image_resolution2': 3.0,
        'image_resolution3': 3.0,
        'image_resolution4': 0.8,
        'image_orientation': 'Axial'
    },
        "func/sub-*_ses-*_task-movie*_echo-3_bold.nii.gz": {
        'image_description': 'fMRI',
        'image_modality': 'fMRI',
        'image_file_format': 'NIfTI',
        'scan_type': 'fMRI',
        'mri_repetition_time_pd': 0.8,
        'mri_echo_time_pd': '0.06432',
        'flip_angle': '49',
        'image_slice_thickness': 3.0,
        'slice_acquisition': 1,
        'slice_timing': '[0, 0.2925, 0.585, 0.0975, 0.39, 0.6825, 0.195, 0.4875, 0, 0.2925, 0.585, 0.0975, 0.39, 0.6825, 0.195, 0.4875, 0, 0.2925, 0.585, 0.0975, 0.39, 0.6825, 0.195, 0.4875, 0, 0.2925, 0.585, 0.0975, 0.39, 0.6825, 0.195, 0.4875, 0, 0.2925, 0.585, 0.0975, 0.39, 0.6825, 0.195, 0.4875]',
        'acquisition_matrix': '[68, 68]',
        'mri_field_of_view_pd': '[204.0, 204.0, 120.0]',
        'recieve_coil': 'HeadNeck_64',
        'patient_position': 'Laying down on back',
        'image_num_dimensions': 4,
        'image_extent1': 68,
        'image_extent2': 68,
        'image_extent3': 40,
        'image_unit1': 'Millimeters',
        'image_unit2': 'Millimeters',
        'image_unit3': 'Millimeters',
        'image_unit4': 'Seconds',
        'image_resolution1': 3.0,
        'image_resolution2': 3.0,
        'image_resolution3': 3.0,
        'image_resolution4': 0.8,
        'image_orientation': 'Axial'
    },
        "dwi/sub-*_ses-*_dir-AP*dwi.nii.gz": {
        'image_description': 'DTI',
        'image_modality': 'MRI',
        'image_file_format': 'NIfTI',
        'scan_type': 'MR diffusion',
        'mri_repetition_time_pd': 3.23,
        'mri_echo_time_pd': '0.0892',
        'flip_angle': '49',
        'image_slice_thickness': 1.5,
        'slice_acquisition': 1,
        'slice_timing': '[0, 1.675, 0.14, 1.8125, 0.2775, 1.9525, 0.4175,2.0925, 0.5575, 2.2325, 0.6975, 2.3725, 0.8375, 2.5125, 0.975, 2.65, 1.115, 2.79, 1.255, 2.93, 1.395, 3.07, 1.535, 0, 1.675, 0.14, 1.8125, 0.2775, 1.9525, 0.4175, 2.0925, 0.5575, 2.2325, 0.6975, 2.3725, 0.8375, 2.5125, 0.975, 2.65, 1.115, 2.79, 1.255, 2.93, 1.395, 3.07, 1.535, 0, 1.675, 0.14, 1.8125, 0.2775, 1.9525, 0.4175, 2.0925, 0.5575, 2.2325, 0.6975, 2.3725, 0.8375, 2.5125, 0.975, 2.65, 1.115, 2.79, 1.255, 2.93, 1.395, 3.07, 1.535, 0, 1.675, 0.14, 1.8125, 0.2775, 1.9525, 0.4175, 2.0925, 0.5575, 2.2325, 0.6975, 2.3725, 0.8375, 2.5125, 0.975, 2.65, 1.115, 2.79, 1.255, 2.93, 1.395, 3.07, 1.535]',
        'acquisition_matrix': '[140, 140]',
        'recieve_coil': 'HeadNeck_64',
        'patient_position': 'Laying down on back',
        'image_num_dimensions': 4,
        'image_unit1': 'Millimeters',
        'image_unit2': 'Millimeters',
        'image_unit3': 'Millimeters',
        'image_unit4': 'Unitless (direction)',
        'image_resolution1': 1.5,
        'image_resolution2': 1.5,
        'image_resolution3': 1.5,
        'image_resolution4': 3.23,
        'image_orientation': 'Axial',
        'bvek_bval_files': 'Yes'
    },
        "dwi/sub-*_ses-*_dir-PA*dwi.nii.gz": {
        'image_description': 'DTI',
        'image_modality': 'MRI',
        'image_file_format': 'NIfTI',
        'scan_type': 'MR diffusion',
        'mri_repetition_time_pd': 3.23,
        'mri_echo_time_pd': '0.0892',
        'flip_angle': '49',
        'image_slice_thickness': 1.5,
        'slice_acquisition': 1,
        'slice_timing': '[0, 1.675, 0.14, 1.8125, 0.2775, 1.9525, 0.4175,2.0925, 0.5575, 2.2325, 0.6975, 2.3725, 0.8375, 2.5125, 0.975, 2.65, 1.115, 2.79, 1.255, 2.93, 1.395, 3.07, 1.535, 0, 1.675, 0.14, 1.8125, 0.2775, 1.9525, 0.4175, 2.0925, 0.5575, 2.2325, 0.6975, 2.3725, 0.8375, 2.5125, 0.975, 2.65, 1.115, 2.79, 1.255, 2.93, 1.395, 3.07, 1.535, 0, 1.675, 0.14, 1.8125, 0.2775, 1.9525, 0.4175, 2.0925, 0.5575, 2.2325, 0.6975, 2.3725, 0.8375, 2.5125, 0.975, 2.65, 1.115, 2.79, 1.255, 2.93, 1.395, 3.07, 1.535, 0, 1.675, 0.14, 1.8125, 0.2775, 1.9525, 0.4175, 2.0925, 0.5575, 2.2325, 0.6975, 2.3725, 0.8375, 2.5125, 0.975, 2.65, 1.115, 2.79, 1.255, 2.93, 1.395, 3.07, 1.535]',
        'acquisition_matrix': '[140, 140]',
        'recieve_coil': 'HeadNeck_64',
        'patient_position': 'Laying down on back',
        'image_num_dimensions': 4,
        'image_unit1': 'Millimeters',
        'image_unit2': 'Millimeters',
        'image_unit3': 'Millimeters',
        'image_unit4': 'Unitless (direction)',
        'image_resolution1': 1.5,
        'image_resolution2': 1.5,
        'image_resolution3': 1.5,
        'image_resolution4': 3.23,
        'image_orientation': 'Axial',
        'bvek_bval_files': 'Yes'
    },
        "dwi/sub-*_ses-*_dir-PA*_sbref.nii.gz": {
        'image_description': 'DTI',
        'image_modality': 'MRI',
        'image_file_format': 'NIfTI',
        'scan_type': 'MR diffusion',
        'mri_repetition_time_pd': 3.23,
        'mri_echo_time_pd': '0.0892',
        'flip_angle': '49',
        'image_slice_thickness': 1.5,
        'slice_acquisition': 1,
        'slice_timing': '[0, 0.14, 0.2775, 0.4175, 0.5575, 0.6975, 0.8375, 0.975, 1.115, 1.255, 1.395, 1.535, 1.675, 1.8125, 1.9525, 2.0925, 2.2325, 2.3725, 2.5125, 2.65, 2.79, 2.93, 3.07, 3.21, 3.3475, 3.4875, 3.6275, 3.7675, 3.9075, 4.0475, 4.185, 4.325, 4.465, 4.605, 4.745, 4.885, 5.0225, 5.1625, 5.3025, 5.4425, 5.5825, 5.7225, 5.86, 6, 6.14, 6.28, 6.42, 6.5575, 6.6975, 6.8375, 6.9775, 7.1175, 7.2575, 7.395, 7.535, 7.675, 7.815, 7.955, 8.095, 8.2325, 8.3725, 8.5125, 8.6525, 8.7925, 8.93, 9.07, 9.21, 9.35, 9.49, 9.63, 9.7675, 9.9075, 10.0475, 10.1875, 10.3275, 10.4675, 10.605, 10.745, 10.885, 11.025, 11.165, 11.3025, 11.4425, 11.5825, 11.7225, 11.8625, 12.0025, 12.14, 12.28, 12.42, 12.56, 12.7]',
        'acquisition_matrix': '[140, 140]',
        'recieve_coil': 'HeadNeck_64',
        'patient_position': 'Laying down on back',
        'image_num_dimensions': 4,
        'image_unit1': 'Millimeters',
        'image_unit2': 'Millimeters',
        'image_unit3': 'Millimeters',
        'image_unit4': 'Unitless (direction)',
        'image_resolution1': 1.5,
        'image_resolution2': 1.5,
        'image_resolution3': 1.5,
        'image_resolution4': 3.23,
        'image_orientation': 'Axial',
        'bvek_bval_files': 'Yes'
    },
        "fmap/sub-*_ses-*AP_epi.nii.gz": {
        'image_description': 'DTI',
        'image_modality': 'MRI',
        'image_file_format': 'NIfTI',
        'scan_type': 'MR diffusion',
        'mri_repetition_time_pd': 6.0,
        'mri_echo_time_pd': '0.04',
        'flip_angle': '49',
        'image_slice_thickness': 1.5,
        'slice_acquisition': 1,
        'slice_timing': '[2.99, 0, 3.14, 0.15, 3.2875, 0.2975, 3.4375, 0.4475, 3.5875, 0.5975, 3.7375, 0.7475, 3.8875, 0.8975, 4.035, 1.045, 4.185, 1.195, 4.335, 1.345, 4.485, 1.495, 4.635, 1.645, 4.7825, 1.7925, 4.9325, 1.9425, 5.0825, 2.0925, 5.2325, 2.2425, 5.3825, 2.3925, 5.53, 2.54, 5.68, 2.69, 5.83, 2.84]',
        'acquisition_matrix': '[68, 68]',
        'mri_field_of_view_pd': '[204.0, 204.0, 120.0]',
        'recieve_coil': 'HeadNeck_64',
        'patient_position': 'Laying down on back',
        'image_num_dimensions': 4,
        'image_extent1': 68,
        'image_extent2': 68,
        'image_extent3': 40,
        'image_extent3': 3,
        'image_unit1': 'Millimeters',
        'image_unit2': 'Millimeters',
        'image_unit3': 'Millimeters',
        'image_unit4': 'Seconds',
        'image_resolution1': 3.0,
        'image_resolution2': 3.0,
        'image_resolution3': 3.0,
        'image_resolution4': 6.0,
        'image_orientation': 'Axial'
    },
    "fmap/sub-*_ses-*PA_epi.nii.gz": {
        'image_description': 'DTI',
        'image_modality': 'MRI',
        'image_file_format': 'NIfTI',
        'scan_type': 'MR diffusion',
        'mri_repetition_time_pd': 6.0,
        'mri_echo_time_pd': '0.04',
        'flip_angle': '49',
        'image_slice_thickness': 3.0,
        'slice_acquisition': 1,
        'slice_timing': '[2.99, 0, 3.14, 0.15, 3.2875, 0.2975, 3.4375, 0.4475, 3.5875, 0.5975, 3.7375, 0.7475, 3.8875, 0.8975, 4.035, 1.045, 4.185, 1.195, 4.335, 1.345, 4.485, 1.495, 4.635, 1.645, 4.7825, 1.7925, 4.9325, 1.9425, 5.0825, 2.0925, 5.2325, 2.2425, 5.3825, 2.3925, 5.53, 2.54, 5.68, 2.69, 5.83, 2.84]',
        'acquisition_matrix': '[68, 68]',
        'mri_field_of_view_pd': '[204.0, 204.0, 120.0]',
        'recieve_coil': 'HeadNeck_64',
        'patient_position': 'Laying down on back',
        'image_num_dimensions': 4,
        'image_extent1': 68,
        'image_extent2': 68,
        'image_extent3': 40,
        'image_extent3': 3,
        'image_unit1': 'Millimeters',
        'image_unit2': 'Millimeters',
        'image_unit3': 'Millimeters',
        'image_unit4': 'Seconds',
        'image_resolution1': 3.0,
        'image_resolution2': 3.0,
        'image_resolution3': 3.0,
        'image_resolution4': 6.0,
        'image_orientation': 'Axial'
    }
}

CARE_fNIRS_description = {
  "*_fNIRS.snirf": {
    "image_description": "fNIRS synchrony",
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

CARE_beh_description = {
  "beh/sub-01_ses-01_task-flanker_behavioral.tsv": {
    "image_description": "Flanker task behavioral response data",
    "image_modality": "behavioral",
    "image_file_format": "TSV",
    "scan_type": "behavioral",
    "image_num_dimensions": 2,
    "image_extent1": 120,
    "image_extent2": 6,
    "image_unit1": "trials",
    "image_unit2": "features",
    "image_resolution1": 1/7.8,
    "image_resolution2": 1,
    "stimulus_timing": "[0.0, 2.0, 4.0, 6.0, 8.0, ...]",
    "stimulus_condition": "congruent, incongruent",
    "task_description": "Participants responded to the direction of a central arrow while ignoring flanking arrows.",
    "response_type": "keyboard",
    "response_mapping": "{left: 'index finger', right: 'middle finger'}",
    "data_columns": "[onset, duration, stimulus_type, response_time, response_accuracy, key_pressed]",
    "sampling_rate": "N/A",
    "time_window": "[0, 240]",
    "time_shift": "N/A"
  }
}


image03_header = {
    'subjectkey': None, 
    'src_subject_id': None, 
    'interview_date': None, 
    'interview_age': None, 
    'sex': None,
    'image_file': None,
    'image_description': None, 
    'image_modality': None, 
    'image_file_format': None, 
    'image_source': None, 
    'study': 'NP1166', 
    'scan_type': None, 
    'experiment_id': None, 
    'series_id': None, 
    'processing_status': None,
}


# Iterate through CARE tracking sheet and extract info on each subject session

# Grab ID, session dates, age, sex

# For each data type 
image03 = []
for data_description in [CARE_MRI_description, CARE_fNIRS_description, CARE_beh_description]:

    # For each MRI  file
    bids_directory = "/storage1/fs1/perlmansusan/Active/moochie/analysis/CARE/ME_MRI_data/"
    for file_identifier, description in data_description.items(): 

        # Grab all files related to the file
        files = glob(f"{bids_directory}{file_identifier}") # Grab all examples of real file

        for file in files:
            file_image03 = image03_header

            # Break down file to subject and session/experiment ID numbers
            subject_id = file.split('sub-')[1].split('_')[0]
            session = file.split('ses-')[1].split('_')[0]

            # Find subject in data tracker
            
            # Find the NDAR Global Unique Identifier (GUID) for research subject

            # Add subject and session ID to image03
            file_image03['visnum'] = session

            # Add in the json second file and description
            file_image03['data_file2'] = file.split('.nii.gz')[0] + '.json'
            file_image03['data_file2_type'] = 'JSON'

            # Add session date (MM/DD/YYYY)

            # Add DOB/age and convert to months

            # Grab and add comments?

            # Add file descriptions
            for key, value in description.items():
                file_image03[key] = value

            # Add fMRI specific info
            MRI_info = {'scan_object': 'Live',
                'transformation_performed': 'No',
                'scanner_manufacturer_pd': 'Siemens',
                'scanner_type_pd': 'MAGNETOM Prisma',
                'scanner_software_versions_pd': 'syngo MR XA30',
                'magnetic_field_strength': '3',
                'software_preproc': 'dcm2bids 3.1.1'}
            
            for key, value in MRI_info.items():
                file_image03[key] = value

            # If BOLD file, look for time length and add in
            if 'bold.nii.gz' == file[-11:]:
                image = nib.load(file)
                file_image03['image_extent4'] = image.header['dim'][4]

            # If a DWI file, add in the X, Y, Z and direction dimensions
            if file.split('/')[-2][:3] == 'dwi':
                image = nib.load(file)
                file_image03['image_extent1'] = image.header['dim'][1]
                file_image03['image_extent2'] = image.header['dim'][2]
                file_image03['image_extent3'] = image.header['dim'][3]
                file_image03['image_extent4'] = image.header['dim'][4]

                file_image03['mri_field_of_view_pd'] = f'[{round(image.header['dim'][1]/1.5, 1)}, {round(image.header['dim'][2]/1.5, 1)}, {round(image.header['dim'][3]/1.5, 1)}]'
                file_image03['bvecfile'] = file.split('.nii.gz')[0] + '.bvec'
                file_image03['bvalfile'] = file.split('.nii.gz')[0] + '.bval'
            

    for file, description in CARE_fNIRS_description.items():

        # For each fNIRS  file
        bids_directory = "/storage1/fs1/perlmansusan/Active/moochie/study_data/CARE/NIRS_data/"
        for file_identifier, description in data_description.items(): 

            # Grab all files related to the file
            files = glob(f"{bids_directory}{file_identifier}") # Grab all examples of real file

            for file in files:
                snirf = h5py.File(file, 'r')
                file_image03 = image03_header

                # Break down file to subject and session/experiment ID numbers
                subject_id = file.split('_')[0]
                session = file.split('V')[1].split('_')[0]

                # Find subject in data tracker
                
                # Find the NDAR Global Unique Identifier (GUID) for research subject

                # Add subject and session ID to image03
                file_image03['visnum'] = session

                # Add session date (MM/DD/YYYY)

                # Add DOB/age and convert to months

                # Grab and add comments?

                data = snirf['nirs']['data1']['dataTimeSeries']
                n_timepoints, n_channels = data.shape

                file_image03["image_extent1"] = n_timepoints

                # Add file descriptions
                for key, value in description.items():
                    file_image03[key] = value

 