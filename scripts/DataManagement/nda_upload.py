

image03_template_filepath = '/storage1/fs1/perlmansusan/Active/moochie/study_data/CARE/CARE_image03.csv'

bids_folder = '/storage1/fs1/perlmansusan/Active/moochie/analysis/CARE/ME_MRI_data/'

experiment_ids = {
    'AHKJ Task Episode A': 1890,
    'AHKJ Task Episode B': 1891,
    'AHKJ Task Episode C': 1892
}

experiment_files = {
    'fMRI': '_echo-1_bold.nii',
    'anatomical': '_T1w.nii',
    'DWI': '_dir-AP_dwi.nii'
}

fmri_image03_json  = {  
    'subjectkey' : None,
    'src_subject_id': None,
    'interview_date': None,
    'interview_age': None,
    'sex': None,
    'comments_misc': None,
    'image_file': None,
    'image_description': 'fMRI',
    'experiment_id': None,
    'scan_type': "fMRI",
    'scan_object': "Live",
    'image_file_format': "NIFTI",
    'image_modality': "MRI",
    'scanner_manufacturer_pd': "Siemens",
    'scanner_type_pd': "Magnetom Prisma",
    'scanner_software_versions_pd': None,
    'magnetic_field_strength': "3.0",
    'mri_repetition_time_pd': 0.8,
    'mri_echo_time_pd': "0.8",
    'flip_angle': "7.0",
    'acquisition_matrix': "[68, 68, 40]",
    'mri_field_of_view_pd': "213 x 208 x 213.0 mm",
    'patient_position': "Laying down face up",
    'transformation_performed': "No",
    'image_num_dimensions': 4,
    'image_extent1': 68,
    'image_extent2': 68,
    'image_extent3': 40,
    'image_extent4': None,
    'extent4_type': 'Time',
    'image_unit1': 'a.u.',
    'software_preproc': 'BIDSkit 3.0.2',
    'study': 'Biological Substrates of Maladaptive Stress Response in Early Childhood',
    'experiment_description': None,
    'visnum': None
    }

structural_image03_json  = {  
    'subjectkey' : None,
    'src_subject_id': None,
    'interview_date': None,
    'interview_age': None,
    'sex': None,
    'comments_misc': None,
    'image_file': None,
    'image_description': 'MPRAGE structural',
    'experiment_id': None,
    'scan_type': "MR structural",
    'scan_object': "Live",
    'image_file_format': "NIFTI",
    'image_modality': "MRI",
    'scanner_manufacturer_pd': "Siemens",
    'scanner_type_pd': "Magnetom Prisma",
    'scanner_software_versions_pd': None,
    'magnetic_field_strength': "3.0",
    'mri_repetition_time_pd': 0.8,
    'mri_echo_time_pd': "0.8",
    'flip_angle': "7.0",
    'acquisition_matrix': "[  3 240 208 256   1   1   1   1]",
    'mri_field_of_view_pd': "199.7 x 208 x 213.0 mm",
    'patient_position': "Laying down face up",
    'transformation_performed': "No",
    'image_num_dimensions': 4,
    'image_extent1': 240,
    'image_extent2': 208,
    'image_extent3': 256,
    'image_extent4': None,
    'extent4_type': 'Time',
    'image_unit1': 'signal intensity',
    'software_preproc': 'BIDSkit 3.0.2',
    'study': 'Biological Substrates of Maladaptive Stress Response in Early Childhood',
    'experiment_description': None,
    'visnum': None
    }

dti_image03_json  = {  
    'subjectkey' : None,
    'src_subject_id': None,
    'interview_date': None,
    'interview_age': None,
    'sex': None,
    'comments_misc': None,
    'image_file': None,
    'image_description': 'DWI',
    'experiment_id': None,
    'scan_type': "MR diffusion",
    'scan_object': "Live",
    'image_file_format': "NIFTI",
    'image_modality': "MRI",
    'scanner_manufacturer_pd': "Siemens",
    'scanner_type_pd': "Magnetom Prisma",
    'scanner_software_versions_pd': None,
    'magnetic_field_strength': "3.0",
    'mri_repetition_time_pd': 0.8,
    'mri_echo_time_pd': "0.8",
    'flip_angle': "7.0",
    'acquisition_matrix': "[  4 140 140  92  99   1   1   1]",
    'mri_field_of_view_pd': "210 x 210 x 138 x 319.7 mm",
    'patient_position': "Laying down face up",
    'transformation_performed': "No",
    'image_num_dimensions': 4,
    'image_extent1': 140,
    'image_extent2': 140,
    'image_extent3': 92,
    'image_extent4': 99,
    'extent4_type': '',
    'image_unit1': 'signal intensity',
    'software_preproc': 'BIDSkit 3.0.2',
    'study': 'Biological Substrates of Maladaptive Stress Response in Early Childhood',
    'experiment_description': None,
    'bvek_bval_files': None,
    'bvecfile': None,
    'bvalfile': None,
    'visnum': None
    }

# Create an image03 for all data in upload

# For each subject

    # Grab subject level needed info

    # For each session

        # Grab session level needed info

        # Find movie version

        # Find experiment ID

        # For each scan

        # For functional image

        # Specify the experiment ID

        # Grab number of volumes to set 'image_extent4'

        #


image03_template  = {  
    'subjectkey' : None,
    'src_subject_id': None,
    'interview_date': None,
    'interview_age': None,
    'sex': None,
    'comments_misc': None,
    'image_file': None,
    'image_thumbnail_file': None,
    'image_description': None,
    'experiment_id': None,
    'scan_type': None,
    'scan_object': None,
    'image_file_format': None,
    'image_modality': None,
    'scanner_manufacturer_pd': None,
    'scanner_type_pd': None,
    'scanner_software_versions_pd': None,
    'magnetic_field_strength': None,
    'mri_repetition_time_pd': None,
    'mri_echo_time_pd': None,
    'flip_angle': None,
    'acquisition_matrix': None,
    'mri_field_of_view_pd': None,
    'patient_position': None,
    'photomet_interpret': None,
    'receive_coil': None,
    'transmit_coil': None,
    'transformation_performed': None,
    'transformation_type': None,
    'image_history': None,
    'image_num_dimensions': None,
    'image_extent1': None,
    'image_extent2': None,
    'image_extent3': None,
    'image_extent4': None,
    'extent4_type': None,
    'image_extent5': None,
    'extent5_type': None,
    'image_unit1': None,
    'image_resolution1': None,
    'image_slice_thickness': None,
    'image_orientation': None,
    'qc_outcome': None,
    'qc_description': None,
    'qc_fail_quest_reason': None,
    'decay_correction': None,
    'frame_end_times': None,
    'frame_end_unit': None,
    'frame_start_times': None,
    'frame_start_unit': None,
    'pet_isotope': None,
    'pet_tracer': None,
    'time_diff_inject_to_image': None,
    'time_diff_units': None,
    'pulse_seq': None,
    'slice_acquisition': None,
    'software_preproc': None,
    'study': None,
    'week': None,
    'experiment_description': None,
    'visit': None,
    'slice_timing': None,
    'bvek_bval_files': None,
    'bvecfile': None,
    'bvalfile': None,
    'visnum': None,
    'accession_number': None
    }