
import sys, os, shutil, subprocess, random
from glob import glob

class ftp:
	"""
	- HIPAA Compliant File Transfer Protocol -
	This class is used as a parent file transfer protocol (ftp) class for transfering
	and restructuring files folders for a given study. To create a new FTP for a
	given study, you will need to create a new atlas defining source and destination of each file/folder
	"""
	def __init__(self, debug = True, copy = True): # Initializing a generic file transfer protocol
		self.debug = debug
		self.copy = copy
		self.lower_case = False

		self.work_dir = os.getcwd()
		self.old_dir = None
		self.new_dir = None

		self.new_atlas = lambda subject : None
		self.add_subjects = lambda subjects, more_subjects : [new_subject for new_subject in new_subjects if new_subject not in subjects]
		print('Generic FTP protocal initialized. Working directory, new directory and atlas need to be defined before running FTP.')

	def transfer(self, source, destination, atlas):
		if self.copy == False:
			response = input("Instance is set to delete files/folders after copying to new directory, would you still like to continue? (y/n)")
			if 'n' in response.lower().strip():
				return

		subject = atlas.subject

		filename = source.split('/').pop() # Grab filename

		if self.lower_case: # Lower case filename if requested
			lowercase_filename = self.rename(filename, subject) # Lowercase filename
			new_filename = lowercase_filename
		else:
			new_filename = filename

		for keyword, replacement in atlas.replacements.items():# Check for a replacement keyword
			if keyword in new_filename: # If keyword found
				new_filename = replacement.join(new_filename.split(keyword)) #


		if os.path.exists(destination + new_filename): # Check if file already transfered
			if os.path.exists(source) and self.copy == False: # Check if source exists and remove requested
				if os.path.isdir(source):
					shutil.rmtree(source)
				else:
					os.remove(source)
			return

		if self.debug:
			print(f'Transfering {source} --> {destination + new_filename}') # If debugging report the file to be transfered
		else:
			if os.path.exists(destination) == False: # Create parent folders if needed
				os.makedirs(destination)
			if os.path.isdir(source) == True:
				shutil.copytree(source, destination + new_filename)
				if self.copy == False:
					shutil.rmtree(source)
			else:
				shutil.copy(source, destination + filename)# Transfer file
				if filename != new_filename:
					os.rename(destination + filename, destination + new_filename)# Rename
				if self.copy == False:
					os.remove(source)

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
			if source[-1:] is '/': # If the item is a folder
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

class pcat_restructure_ftp(ftp):
	"""
	P-CAT Child FTP Protocol - Utilized to transfer files over to the new restructured directory
	"""
	def __init__(self, debug = False, copy = True):
		self.debug = debug
		self.copy = copy
		self.lower_case = False

		#self.work_dir = '../../../../study_data/P-CAT/R56/' # Working directory
		self.work_dir = '../../../../study_data/P-CAT/R56/restructured_data/PSU_data/' # Working directory
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
		self.new_dir = '../../../../../analysis/P-CAT/NIRS_Data_Clean_WU_PSU/'
		self.new_atlas = lambda subject : pcat_analysis_atlas(subject)

		subjects = []
		new_subjects = os.listdir('task_data/dbdos') # Grab all subjects in task_data
		subjects = self.add_subjects(subjects, new_subjects)
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
			f'task_data/dbdos/{subject[:4]}/':f'{subject[:4]}/{subject[:4]}_DB-DOS/{subject}_fNIRS_DB-DOS/'
		}
		self.replacements = {}

class care_ftp(ftp):
	def __init__(self, debug = False, copy = True):
		self.debug = debug
		self.copy = copy
		self.lower_case = False

		self.work_dir = '../../../../'
		self.old_dir = 'study_data/'
		self.new_dir = 'analysis/'

		self.new_atlas = lambda subject : care_nirs_atlas(subject)
		self.add_subjects = lambda subjects, more_subjects : [new_subject for new_subject in new_subjects if new_subject not in subjects]

		os.chdir(self.work_dir)

		print('CARE FTP protocal initialized. Looking for new fNIRS dat')

		if hot_init:
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
		self.replacements = {} # Initialize an empty replacement to keep the filename the same
