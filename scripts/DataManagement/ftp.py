
import sys
import os, shutil
from glob import glob

class ftp:
	"""
	This class is used as a parent file transfer protocol (ftp) class for restructuring files
	folders for a given study. To create a new FTP for a given study, you will need
	to create a new atlas defining source and destination of each file/folder
	"""
	def __init__(self, debug = True): # Initializing a generic file transfer protocol
		self.work_dir = os.getcwd()
		self.old_dir = None
		self.new_dir = None

		self.new_atlas = lambda subject : None
		self.add_subjects = lambda subjects, more_subjects : [new_subject for new_subject in new_subjects if new_subject not in subjects]
		print('Generic FTP protocal initialized. Working directory, new directory and atlas need to be defined before running FTP.')

	def iterate_subjects(self, subjects, debug):
		for subject in subjects:	# For each subject
			for age in ['-C', '-P']:
				subject_atlas = self.new_atlas(subject + age) # Create an atlas of all potential files
				self.iterate_atlas(subject_atlas, debug)

	def iterate_atlas(self, atlas, debug):
		for source, destination in atlas.map.items(): # For each item in the atlas map
			source = self.old_dir + source # Prefix on the working directory
			destination = self.new_dir + destination # Prefix on the new directory
			if source[-1:] is '/': # If the item is a folder
				if os.path.exists(source): # Check if folder exists
					for filename in os.listdir(source):# For each file:
						self.transfer(source + filename, destination, atlas.subject, debug) # Call file transfer
				elif debug:
					print(f"Folder {source} doesn't exits")
			else: # If the item is a file
				if os.path.exists(source): # If file to be transfered exists
					self.transfer(source, destination, atlas.subject, debug) # Call file transfer
				elif debug:
					print(f"File {source} doesn't exist")

	def transfer(self, source, destination, subject, debug):
		filename = source.split('/').pop() # Grab filename
		new_filename = self.rename(filename, subject) # Lowercase filename

		if os.path.exists(destination + new_filename): # Check if file already transfered
			return

		if debug:
			print(f'Transfering {source} --> {destination + new_filename}') # If debugging report the file to be transfered
		else:
			if os.path.exists(destination) is False: # Create parent folders if needed
				os.makedirs(destination)
			shutil.copy(source, destination + filename)# Transfer file
			os.rename(destination + filename, destination + new_filename)# Rename

	def rename(self, filename, subject): # Function to lower case filename except for subject ID
		return subject.join([split.lower() for split in filename.split(subject)])

class pcat_ftp(ftp):
	"""
	P-CAT Child FTP Protocol - Utilized to transfer files over to the new restructured directory
	"""
	def __init__(self, debug = True):
		self.work_dir = '../../../../study_data/P-CAT/R56/' # Working directory
		self.old_dir = ''
		self.new_dir = 'restructured_data/'

		self.excluded_subjects = ['1147']

		self.new_atlas = lambda subject : pcat_atlas(subject)
		self.add_subjects = lambda subjects, new_subjects : [new_subject for new_subject in new_subjects if new_subject not in subjects and new_subject not in self.excluded_subjects]

		os.chdir(self.work_dir)

		self.orient(debug)

	def orient(self, debug): # Used to find all subjects with potential data
		subjects = []

		doi = ['video_data', 'task_data', 'NIRS_data', 'audio_data', 'eyetracker_data'] # Directories of interest
		for directory in doi:
			new_subjects = os.listdir(directory) # Grab all subjects in task_data
			subjects = self.add_subjects(subjects, new_subjects)

		self.iterate_subjects(subjects, debug)

class pcat_atlas:
	"""
	Subject Atlas defines file origins and destinations among files to be transfered
	for the P-CAT data restructuring. Could be adjusted to work for other transfers if needed
	"""
	def __init__(self, subject):
		self.subject = subject
		self.map = { # List of all files/folders to transfer
			f'audio_data/{subject[:4]}/':f'audio_data/interview/{subject[:4]}/',
			f'NIRS_data/{subject[:4]}/{subject[:4]}_DB_DOS/{subject}_fNIRS_DB-DOS/':f'fnirs_data/dbdos/{subject[:4]}/{subject}/',
			f'NIRS_data/{subject[:4]}/{subject[:4]}_Flanker/':f'fnirs_data/flanker/{subject[:4]}/',
			f'task_data/{subject[:4]}/{subject[:4]}_DB_DOS/':f'task_data/dbdos/{subject[:4]}/',
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
			f'questionnaire_data/':f'questionnaire_data'
		}
