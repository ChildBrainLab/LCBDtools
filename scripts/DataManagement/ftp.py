
import sys, os, shutil, subprocess, random
from glob import glob

class ftp:
	"""
	- HIPAA Compliant File Transfer Protocol -
	This class is used as a parent file transfer protocol (ftp) class for transfering
	and restructuring files folders for a given study. To create a new FTP for a
	given study, you will need to create a new atlas defining source and destination of each file/folder
	"""
	def __init__(self, debug = True, copy = True, undo = False): # Initializing a generic file transfer protocol
		self.debug = debug
		self.copy = copy
		self.undo = undo
		self.lower_case = False

		if self.copy == False:
			response = input('Copy apart of this file transfer protocol is set to False so the script will delete old files after transfer, would you like to continue? (y/n)\n')
			if 'n' in response.lower():
				return

		self.work_dir = os.getcwd()
		self.old_dir = None
		self.new_dir = None

		self.new_atlas = lambda subject : None
		self.add_subjects = lambda subjects, more_subjects : [new_subject for new_subject in new_subjects if new_subject not in subjects]
		print('Generic FTP protocal initialized. Working directory, new directory and atlas need to be defined before running FTP.')

	def transfer(self, source, destination, atlas):

		subject = atlas.subject

		filename = source.split('/').pop() # Grab filename

		if os.path.isfile(source) == True:
			if self.lower_case: # Lower case filename if requested
				lowercase_filename = self.rename(filename, subject) # Lowercase filename
				new_filename = lowercase_filename
			else:
				new_filename = filename

			split = new_filename.split('.')
			if len(split) > 1:
				filetype = split.pop()
			else:
				filetype = '' 
			new_filename = split[0]

			for keyword, replacement in atlas.replacements.items():# Check for a replacement keyword
				if keyword in new_filename: # If keyword found
					new_filename = replacement.join(new_filename.split(keyword)) #
			new_filename = new_filename + '.' + filetype
		else:
			new_filename = filename

		if self.debug:
			print(f'Transfering {source} --> {destination + new_filename}') # If debugging report the file to be transfered
		else:
			try:
				if os.path.exists(destination) == False: # Create parent folders if needed
					os.makedirs(destination)
				if os.path.isdir(source) == True:
					shutil.copytree(source, destination + new_filename)
					if self.copy == False:
						shutil.rmtree(source)
				else:
					shutil.copy(source, destination + new_filename)# Transfer file
				#if filename != new_filename:
				#	os.rename(destination + filename, destination + new_filename)# Rename
					if self.copy == False:
						os.remove(source)
			except:
				print(f'Transfer failed: {source}') 
	   
	def bash(self, command):
		process = subprocess.Popen(command.split(), stdout =subprocess.PIPE)
		return process.communicate()

	def ssh(self):
		return

	def rename(self, filename, subject, atlas = None): # Function to lower case filename except for subject ID
		return subject.join([split.lower() for split in filename.split(subject)])

	def iterate_subjects(self, subjects):
		for subject in subjects:
			subject_atlas = self.new_atlas(subject) # Create an atlas of all potential files
			self.iterate_atlas(subject_atlas)

	def iterate_atlas(self, atlas):
		for source, destination in atlas.map.items(): # For each item in the atlas map
			source = self.old_dir + source # Prefix on the working directory
			destination = self.new_dir + destination # Prefix on the new directory
			if source[-1:] == '/': # If the item is a folder
				if os.path.exists(source) == True: # Check if folder exists
					for filename in os.listdir(source):# For each file:
						self.transfer(source + filename, destination, atlas) # Call file transfer
				else:
					print(f"Folder {source} doesn't exits")
			else: # If the item is a file
				if os.path.exists(source): # If file to be transfered exists
					self.transfer(source, destination, atlas) # Call file transfer
				else:
					print(f"File {source} doesn't exist")

class aws(ftp):
	def __init__(self):
		self.s3 = boto3.client('s3')
		self.ec2 = boto3.client('ec2')

		self.lower_case = False

		with open('care_subjects.txt', 'r') as file:
			self.subjects = file.read().split(',')[:-1]

	def main(self):
		random_subjects = self.subjects[:20]

		results = self.upload(random_subjects)
		self.transfer(self.s3, "CNDA_downloads/", "data/perlman/moochie/study_data/CARE/CNDA_downloads/", "moochie")


	def upload(self, subjects = None):
		if subjects == None:
			subjects = self.subjects
		for subject in subjects:
			os.mkdir(f"CNDA_downloads/{subject}/")
			self.bash(str(f'scp -r schaedigd@dynosparky.neuroimage.wustl.edu:moochie/study_data/CARE/CNDA_downloads/NP1166/{subject}/ses-0/ CNDA_downloads/{subject}/'))
		return True

	def transfer(self, client, source, destination, bucket):
		dir = os.listdir(source)
		for path in dir:
			if os.path.isdir(source + path) == True:
				self.transfer(client, source + path + '/', destination + path + '/', bucket)
			else:
				if '.git' not in path:
					client.upload_file(source + path, bucket, destination + path)

class pcat_ftp(ftp):
	"""
	P-CAT Child FTP Protocol - Utilized to transfer files over to the new restructured directory
	"""
	def __init__(self, debug = False, copy = True, undo = False):
		self.debug = debug
		self.copy = copy
		self.undo = undo
		self.lower_case = False

		self.work_dir = '../../../../study_data/P-CAT/R56/PCAT_MS1/data/psychopy/' # Working directory
		#self.work_dir = '../../../../study_data/P-CAT/R56/restructured_data/PSU_data/' # Working directory
		#self.work_dir = '../../../../analysis/P-CAT/NIRS_Data_Clean_WU_PSU/'
		self.old_dir = ''
		self.new_dir = 'restructured_data/'

		self.excluded_subjects = ['1147']

		self.new_atlas = lambda subject : pcat_atlas(subject)
		self.add_subjects = lambda subjects, new_subjects : [new_subject for new_subject in new_subjects if new_subject not in subjects and new_subject not in self.excluded_subjects]

		os.chdir(self.work_dir)

	def orient(self): # Used to find all subjects with potential data
		subjects = []

		doi = ['video_data', 'task_data', 'NIRS_data', 'audio_data', 'eyetracker_data'] # Directories of interest
		for directory in doi:
			new_subjects = os.listdir(directory) # Grab all subjects in task_data
			subjects = self.add_subjects(subjects, new_subjects)

		self.iterate_subjects(subjects)

	def orient_analysis(self):
		self.old_dir = ''
		self.new_dir = '../../../../../../analysis/P-CAT/NIRS_Data_Clean_WU_PSU/'
		self.new_atlas = lambda subject : pcat_analysis_atlas(subject)

		subjects = ['1258','1187','1194','1177','1193','1180','1184','1263','1179','1173','1104','1190','1109','1103','1174','1189','1256','1112','1266','1176','1195','1186','1265','1182','1188','1175','1102','1243','1172','1178','1185']
		self.iterate_subjects(subjects)

	def iterate_subjects(self, subjects):
		for subject in subjects:	# For each subject
			for age in ['-C', '-P']: # For parent and child
				subject_atlas = self.new_atlas(subject + age) # Create an atlas of all potential files
				self.iterate_atlas(subject_atlas)

class pcat_restructuring_atlas:
	"""
	Subject Atlas defines file origins and destinations among files to be transfered
	for the P-CAT data restructuring. Could be adjusted to work for other transfers if needed
	"""
	def __init__(self, subject):
		self.subject = subject
		self.map = { # List of all files/folders to transfer
			f'audio_data/{subject[:4]}/':f'audio_data/interview/{subject[:4]}/',
			f'NIRS_data/{subject[:4]}/{subject[:4]}_DB-DOS/{subject}_fNIRS_DB-DOS/':f'fnirs_data/dbdos/{subject[:4]}/{subject}/',
			f'NIRS_data/{subject[:4]}/{subject[:4]}_Flanker/':f'fnirs_data/flanker/{subject[:4]}/',
			f'task_data/{subject[:4]}/{subject[:4]}_DB-DOS/':f'task_data/dbdos/{subject[:4]}/',
			f'task_data/{subject[:4]}/{subject[:4]}_Flanker/':f'task_data/flanker/{subject[:4]}/',
			f'task_data/{subject[:4]}/{subject[:4]}_Jumble/':f'task_data/jumble/{subject[:4]}/',
			f'task_data/{subject[:4]}/{subject[:4]}_Posner/':f'task_data/posner/{subject[:4]}/',
			f'video_data/{subject[:4]}/{subject[:4]}_DB-DOS.mp4':f'video_data/dbdos/{subject[:4]}/',
			f'video_data/{subject[:4]}/{subject[:4]}_Flanker.mp4':f'video_data/flanker/{subject[:4]}/',
			f'video_data/{subject[:4]}/{subject[:4]}_Flanker_practice.mp4':f'video_data/flanker/{subject[:4]}/',
			f'video_data/{subject[:4]}/{subject[:4]}_Interview.mp4':f'video_data/interview/{subject[:4]}/',
			f'video_data/{subject[:4]}/{subject[:4]}_DB-DOS.MP4':f'video_data/dbdos/{subject[:4]}/',
			f'video_data/{subject[:4]}/{subject[:4]}_Flanker.MP4':f'video_data/flanker/{subject[:4]}/',
			f'video_data/{subject[:4]}/{subject[:4]}_Flanker_practice.MP4':f'video_data/flanker/{subject[:4]}/',
			f'video_data/{subject[:4]}/{subject[:4]}_Interview.MP4':f'video_data/interview/{subject[:4]}/',
			f'video_data/{subject[:4]}/{subject[:4]}_TSST/':f'video_data/tsst/{subject[:4]}/',
			f'eyetracker_data/{subject[:4]}/{subject}_TSST/':f'eyetracker_data/tsst/{subject[:4]}/{subject}/',
			f'eyetracker_data/{subject[:4]}/{subject}_Jumble/':f'eyetracker_data/jumble/{subject[:4]}/',
			f'KBIT_data/{subject[:4]}_KBIT.pdf':f'kbit_data/',
			f'questionnaire_data/':f'questionnaire_data/'
		}
		self.replacements = {
			'db-dos':'dbdos'
		}

class pcat_analysis_atlas:
	def __init__(self, subject):
		self.subject = subject
		self.map = { # List of all files/folders to transfer
			#f'{subject[:4]}/{subject}/':f'{subject[:4]}/{subject[:4]}_DB-DOS/{subject}_fNIRS_DB-DOS/',
			#f'task_data/dbdos/{subject[:4]}/':f'{subject[:4]}/{subject[:4]}_DB-DOS/{subject}_fNIRS_DB-DOS/'
			#f'{subject[:4]}/{subject[:4]}_DB-DOS/{subject}_fNIRS_DB-DOS/':f'{subject[:4]}/{subject[:4]}_DB-DOS/{subject}_fNIRS_DB-DOS/'
			f'{subject[:4]}/':f'{subject[:4]}/{subject[:4]}_DB-DOS/{subject}_fNIRS_DB-DOS/'
		}
		self.replacements = {'nirs': 'NIRS',
							'DB-DOS': 'db-dos',
							'dbdos' : 'db-dos'}

class care_ftp(ftp):
	def __init__(self, debug = False, copy = True):
		self.debug = debug
		self.copy = copy
		self.lower_case = False

		self.work_dir = '../../../../'
		self.old_dir = 'study_data/'
		self.new_dir = 'analysis/'

		self.new_atlas = lambda subject : care_nirs_atlas(subject)
		self.add_subjects = lambda subjects, more_subjects : [new_subject for new_subject in more_subjects if new_subject not in subjects]

		os.chdir(self.work_dir)

		print('CARE FTP protocal initialized. Looking for new fNIRS dat')

		self.orient()

	def orient(self):
		subjects = [subject for subject in os.listdir('study_data/CARE/NIRS_data/') if subject != 'P002']
		self.iterate_subjects(subjects)
		return

class care_nirs_atlas:
	"""
	Subject Atlas for the CARE study to transfer NIRS data to the
	preprocessing area
	"""
	def __init__(self, subject):
		self.subject = subject
		self.map = {
			f'CARE/NIRS_data/{self.subject}/':f'CARE/NIRS_data_clean_2/{self.subject}/'
		}
		self.replacements = {'.V':'V'} # Initialize an empty replacement to keep the filename the same

class vanshb_partition_ftp(ftp):
	def __init__(self, debug = False, copy = True):
		self.debug = debug
		self.copy = copy
		self.lower_case = False

		self.work_dir = './'
		self.old_dir = '/storage1/fs1/perlmansusan/Active/moochie/analysis/CARE/MRI_data/derivatives/fmriprep/'
		self.new_dir = '/storage1/fs1/perlmansusan/Active/vanshb_partition/fmri_data/derivatives/fmriprep/'

		self.new_atlas = lambda subject : vanshb_partition_atlas(subject)
		self.add_subjects = lambda subjects, new_subjects : [new_subject for new_subject in new_subjects if new_subject not in subjects]

		os.chdir(self.work_dir)

		print('Vansh partition FTP protocal initialized. Looking for new fMRI dat')

		self.orient()

	def orient(self):
		# Grab subject data for Vansh's analysis
		subjects = [subject for subject in os.listdir(self.old_dir) if subject[:4] == 'sub-' and subject[-5:] != '.html']
		print(f"Subjects: {subjects}")

		self.iterate_subjects(subjects)
		return

class vanshb_partition_atlas:
	def __init__(self, subject):
		self.subject = subject
		self.map = { # List of all files/folders to transfer
			f'{subject}/ses-0/func/{subject}_ses-0_task-movieA_space-MNIPediatricAsym_cohort-2_res-2_desc-preproc_bold_6mm_smoothed.nii':f'{subject}/ses-0/func/{subject}_ses-0_task-movieA_space-MNIPediatricAsym_cohort-2_res-2_desc-preproc_bold_6mm_smoothed.nii',
			f'{subject}/ses-0/func/{subject}_ses-0_task-movieB_space-MNIPediatricAsym_cohort-2_res-2_desc-preproc_bold_6mm_smoothed.nii':f'{subject}/ses-0/func/{subject}_ses-0_task-movieB_space-MNIPediatricAsym_cohort-2_res-2_desc-preproc_bold_6mm_smoothed.nii',
			f'{subject}/ses-0/func/{subject}_ses-0_task-movieC_space-MNIPediatricAsym_cohort-2_res-2_desc-preproc_bold_6mm_smoothed.nii':f'{subject}/ses-0/func/{subject}_ses-0_task-movieC_space-MNIPediatricAsym_cohort-2_res-2_desc-preproc_bold_6mm_smoothed.nii',
			f'{subject}/ses-0/func/{subject}_ses-0_task-movieA_run-02_space-MNIPediatricAsym_cohort-2_res-2_desc-preproc_bold_6mm_smoothed.nii':f'{subject}/ses-0/func/{subject}_ses-0_task-movieA_space-MNIPediatricAsym_cohort-2_res-2_desc-preproc_bold_6mm_smoothed.nii',
			f'{subject}/ses-0/func/{subject}_ses-0_task-movieB_run-02_space-MNIPediatricAsym_cohort-2_res-2_desc-preproc_bold_6mm_smoothed.nii':f'{subject}/ses-0/func/{subject}_ses-0_task-movieB_space-MNIPediatricAsym_cohort-2_res-2_desc-preproc_bold_6mm_smoothed.nii',
			f'{subject}/ses-0/func/{subject}_ses-0_task-movieC_run-02_space-MNIPediatricAsym_cohort-2_res-2_desc-preproc_bold_6mm_smoothed.nii':f'{subject}/ses-0/func/{subject}_ses-0_task-movieC_space-MNIPediatricAsym_cohort-2_res-2_desc-preproc_bold_6mm_smoothed.nii',
			f'{subject}/ses-0/func/{subject}_ses-0_task-movieA_space-MNI152NLin2009cAsym_res-2_desc-preproc_bold_6mm_smoothed.nii':f'{subject}/ses-0/func/{subject}_ses-0_task-movieA_space-MNI152NLin2009cAsym_res-2_desc-preproc_bold_6mm_smoothed.nii',
			f'{subject}/ses-0/func/{subject}_ses-0_task-movieB_space-MNI152NLin2009cAsym_res-2_desc-preproc_bold_6mm_smoothed.nii':f'{subject}/ses-0/func/{subject}_ses-0_task-movieB_space-MNI152NLin2009cAsym_res-2_desc-preproc_bold_6mm_smoothed.nii',
			f'{subject}/ses-0/func/{subject}_ses-0_task-movieCspace-MNI152NLin2009cAsym_res-2_desc-preproc_bold_6mm_smoothed.nii':f'{subject}/ses-0/func/{subject}_ses-0_task-movieC_space-MNI152NLin2009cAsym_res-2_desc-preproc_bold_6mm_smoothed.nii',
			f'{subject}/ses-0/func/{subject}_ses-0_task-movieA_run-02_space-MNI152NLin2009cAsym_res-2_desc-preproc_bold_6mm_smoothed.nii':f'{subject}/ses-0/func/{subject}_ses-0_task-movieA_space-MNI152NLin2009cAsym_res-2_desc-preproc_bold_6mm_smoothed.nii',
			f'{subject}/ses-0/func/{subject}_ses-0_task-movieB_run-02_space-MNI152NLin2009cAsym_res-2_desc-preproc_bold_6mm_smoothed.nii':f'{subject}/ses-0/func/{subject}_ses-0_task-movieB_space-MNI152NLin2009cAsym_res-2_desc-preproc_bold_6mm_smoothed.nii',
			f'{subject}/ses-0/func/{subject}_ses-0_task-movieC_run-02_space-MNI152NLin2009cAsym_res-2_desc-preproc_bold_6mm_smoothed.nii':f'{subject}/ses-0/func/{subject}_ses-0_task-movieC_space-MNI152NLin2009cAsym_res-2_desc-preproc_bold_6mm_smoothed.nii',
			f'{subject}/ses-0/func/AHKJ_rating_avg_movieA.txt':f'{subject}/ses-0/func/AHKJ_rating_avg_movieA.txt',
			f'{subject}/ses-0/func/AHKJ_rating_avg_movieB.txt':f'{subject}/ses-0/func/AHKJ_rating_avg_movieB.txt',
			f'{subject}/ses-0/func/AHKJ_rating_avg_movieC.txt':f'{subject}/ses-0/func/AHKJ_rating_avg_movieC.txt',
			f'{subject}/ses-0/func/AHKJ_loudness_movieA.txt':f'{subject}/ses-0/func/AHKJ_loudness_movieA.txt',
			f'{subject}/ses-0/func/AHKJ_loudness_movieB.txt':f'{subject}/ses-0/func/AHKJ_loudness_movieB.txt',
			f'{subject}/ses-0/func/AHKJ_loudness_movieC.txt':f'{subject}/ses-0/func/AHKJ_loudness_movieC.txt',
			f'{subject}/ses-0/func/AHKJ_luminance_movieA.txt':f'{subject}/ses-0/func/AHKJ_luminance_movieA.txt',
			f'{subject}/ses-0/func/AHKJ_luminance_movieB.txt':f'{subject}/ses-0/func/AHKJ_luminance_movieB.txt',
			f'{subject}/ses-0/func/AHKJ_luminance_movieC.txt':f'{subject}/ses-0/func/AHKJ_luminance_movieC.txt',
			f'{subject}/ses-0/func/{subject}_ses-0_task-movieA_desc-confounds_rot_x.txt':f'{subject}/ses-0/func/{subject}_ses-0_task-movieA_desc-confounds_rot_x.txt',
			f'{subject}/ses-0/func/{subject}_ses-0_task-movieA_desc-confounds_rot_y.txt':f'{subject}/ses-0/func/{subject}_ses-0_task-movieA_desc-confounds_rot_y.txt',
			f'{subject}/ses-0/func/{subject}_ses-0_task-movieA_desc-confounds_rot_z.txt':f'{subject}/ses-0/func/{subject}_ses-0_task-movieA_desc-confounds_rot_z.txt',
			f'{subject}/ses-0/func/{subject}_ses-0_task-movieA_desc-confounds_trans_x.txt':f'{subject}/ses-0/func/{subject}_ses-0_task-movieA_desc-confounds_trans_x.txt',
			f'{subject}/ses-0/func/{subject}_ses-0_task-movieA_desc-confounds_trans_y.txt':f'{subject}/ses-0/func/{subject}_ses-0_task-movieA_desc-confounds_trans_y.txt',
			f'{subject}/ses-0/func/{subject}_ses-0_task-movieA_desc-confounds_trans_z.txt':f'{subject}/ses-0/func/{subject}_ses-0_task-movieA_desc-confounds_trans_z.txt',
			f'{subject}/ses-0/func/{subject}_ses-0_task-movieB_desc-confounds_rot_x.txt':f'{subject}/ses-0/func/{subject}_ses-0_task-movieB_desc-confounds_rot_x.txt',
			f'{subject}/ses-0/func/{subject}_ses-0_task-movieB_desc-confounds_rot_y.txt':f'{subject}/ses-0/func/{subject}_ses-0_task-movieB_desc-confounds_rot_y.txt',
			f'{subject}/ses-0/func/{subject}_ses-0_task-movieB_desc-confounds_rot_z.txt':f'{subject}/ses-0/func/{subject}_ses-0_task-movieB_desc-confounds_rot_z.txt',
			f'{subject}/ses-0/func/{subject}_ses-0_task-movieB_desc-confounds_trans_x.txt':f'{subject}/ses-0/func/{subject}_ses-0_task-movieB_desc-confounds_trans_x.txt',
			f'{subject}/ses-0/func/{subject}_ses-0_task-movieB_desc-confounds_trans_y.txt':f'{subject}/ses-0/func/{subject}_ses-0_task-movieB_desc-confounds_trans_y.txt',
			f'{subject}/ses-0/func/{subject}_ses-0_task-movieB_desc-confounds_trans_z.txt':f'{subject}/ses-0/func/{subject}_ses-0_task-movieB_desc-confounds_trans_z.txt',
			f'{subject}/ses-0/func/{subject}_ses-0_task-movieC_desc-confounds_rot_x.txt':f'{subject}/ses-0/func/{subject}_ses-0_task-movieC_desc-confounds_rot_x.txt',
			f'{subject}/ses-0/func/{subject}_ses-0_task-movieC_desc-confounds_rot_y.txt':f'{subject}/ses-0/func/{subject}_ses-0_task-movieC_desc-confounds_rot_y.txt',
			f'{subject}/ses-0/func/{subject}_ses-0_task-movieC_desc-confounds_rot_z.txt':f'{subject}/ses-0/func/{subject}_ses-0_task-movieC_desc-confounds_rot_z.txt',
			f'{subject}/ses-0/func/{subject}_ses-0_task-movieC_desc-confounds_trans_x.txt':f'{subject}/ses-0/func/{subject}_ses-0_task-movieC_desc-confounds_trans_x.txt',
			f'{subject}/ses-0/func/{subject}_ses-0_task-movieC_desc-confounds_trans_y.txt':f'{subject}/ses-0/func/{subject}_ses-0_task-movieC_desc-confounds_trans_y.txt',
			f'{subject}/ses-0/func/{subject}_ses-0_task-movieC_desc-confounds_trans_z.txt':f'{subject}/ses-0/func/{subject}_ses-0_task-movieC_desc-confounds_trans_z.txt',
			f'{subject}/ses-0/func/{subject}_ses-0_task-movieA_run-02_desc-confounds_rot_x.txt':f'{subject}/ses-0/func/{subject}_ses-0_task-movieA_desc-confounds_rot_x.txt',
			f'{subject}/ses-0/func/{subject}_ses-0_task-movieA_run-02_desc-confounds_rot_y.txt':f'{subject}/ses-0/func/{subject}_ses-0_task-movieA_desc-confounds_rot_y.txt',
			f'{subject}/ses-0/func/{subject}_ses-0_task-movieA_run-02_desc-confounds_rot_z.txt':f'{subject}/ses-0/func/{subject}_ses-0_task-movieA_desc-confounds_rot_z.txt',
			f'{subject}/ses-0/func/{subject}_ses-0_task-movieA_run-02_desc-confounds_trans_x.txt':f'{subject}/ses-0/func/{subject}_ses-0_task-movieA_desc-confounds_trans_x.txt',
			f'{subject}/ses-0/func/{subject}_ses-0_task-movieA_run-02_desc-confounds_trans_y.txt':f'{subject}/ses-0/func/{subject}_ses-0_task-movieA_desc-confounds_trans_y.txt',
			f'{subject}/ses-0/func/{subject}_ses-0_task-movieA_run-02_desc-confounds_trans_z.txt':f'{subject}/ses-0/func/{subject}_ses-0_task-movieA_desc-confounds_trans_z.txt',
			f'{subject}/ses-0/func/{subject}_ses-0_task-movieB_run-02_desc-confounds_rot_x.txt':f'{subject}/ses-0/func/{subject}_ses-0_task-movieB_desc-confounds_rot_x.txt',
			f'{subject}/ses-0/func/{subject}_ses-0_task-movieB_run-02_desc-confounds_rot_y.txt':f'{subject}/ses-0/func/{subject}_ses-0_task-movieB_desc-confounds_rot_y.txt',
			f'{subject}/ses-0/func/{subject}_ses-0_task-movieB_run-02_desc-confounds_rot_z.txt':f'{subject}/ses-0/func/{subject}_ses-0_task-movieB_desc-confounds_rot_z.txt',
			f'{subject}/ses-0/func/{subject}_ses-0_task-movieB_run-02_desc-confounds_trans_x.txt':f'{subject}/ses-0/func/{subject}_ses-0_task-movieB_desc-confounds_trans_x.txt',
			f'{subject}/ses-0/func/{subject}_ses-0_task-movieB_run-02_desc-confounds_trans_y.txt':f'{subject}/ses-0/func/{subject}_ses-0_task-movieB_desc-confounds_trans_y.txt',
			f'{subject}/ses-0/func/{subject}_ses-0_task-movieB_run-02_desc-confounds_trans_z.txt':f'{subject}/ses-0/func/{subject}_ses-0_task-movieB_desc-confounds_trans_z.txt',
			f'{subject}/ses-0/func/{subject}_ses-0_task-movieC_run-02_desc-confounds_rot_x.txt':f'{subject}/ses-0/func/{subject}_ses-0_task-movieC_desc-confounds_rot_x.txt',
			f'{subject}/ses-0/func/{subject}_ses-0_task-movieC_run-02_desc-confounds_rot_y.txt':f'{subject}/ses-0/func/{subject}_ses-0_task-movieC_desc-confounds_rot_y.txt',
			f'{subject}/ses-0/func/{subject}_ses-0_task-movieC_run-02_desc-confounds_rot_z.txt':f'{subject}/ses-0/func/{subject}_ses-0_task-movieC_desc-confounds_rot_z.txt',
			f'{subject}/ses-0/func/{subject}_ses-0_task-movieC_run-02_desc-confounds_trans_x.txt':f'{subject}/ses-0/func/{subject}_ses-0_task-movieC_desc-confounds_trans_x.txt',
			f'{subject}/ses-0/func/{subject}_ses-0_task-movieC_run-02_desc-confounds_trans_y.txt':f'{subject}/ses-0/func/{subject}_ses-0_task-movieC_desc-confounds_trans_y.txt',
			f'{subject}/ses-0/func/{subject}_ses-0_task-movieC_run-02_desc-confounds_trans_z.txt':f'{subject}/ses-0/func/{subject}_ses-0_task-movieC_desc-confounds_trans_z.txt',
		}
		self.replacements = {}


if __name__ == "__main__":
	protocol = vanshb_partition_ftp()

