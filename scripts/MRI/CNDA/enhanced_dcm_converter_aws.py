import os, time, datetime, subprocess, sys
from datetime import datetime
from glob import glob


subject = sys.argv[1]
if subject[:3] != 'sub':
	subject = sys.arg[2]

path = './CNDA_downloads/NP1166/'

update_date = datetime.strptime('03/08/2023', '%m/%d/%Y')

def bash(command):
	process = subprocess.Popen(command.split(), stdout =subprocess.PIPE)
	return process.communicate()

os.chdir(path)
directory = os.listdir('.')

if subject:
	directory = [subject]

for subject_folder in directory:
	creation_date = datetime.fromtimestamp(os.path.getctime(subject_folder))
	if creation_date > update_date:
		for root, directories, files in os.walk(subject_folder):
			for file in files:
				if file[-4:] == '.dcm':
					output, error = bash('dcm2niix {:s}'.format(root))
					print(output)
					if error:
						print('{:s} failed to convert! {:s}'.format(file, error))
					else:
						print(output)
						break
#/usr/bin/python3.7 /data/perlman/moochie/github/LCBDtools/scripts/MRI/CNDA/enhanced_dcm_converter.py $sub
