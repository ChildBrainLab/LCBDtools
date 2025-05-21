import subprocess
from glob import glob

nirs_script = "Z:/Active/moochie/github/HomerOfflineConverter/HomerOfflineConverter.m"

nirs_dir = 'Z:/Active/moochie/study_data/CARE/NIRS_data/'

probes = glob(f"{nirs_dir}/*/*/*/*.mat")
for probe in probes:
	split = probe.split('\\')
	subject = split[1]
	session = split[2]
	directory = '/'.join(split[:-1])

	nirs_file = glob(f"{directory}/*.nirs")
	if len(nirs_file) > 0:
		print(f"{subject} session {session} already converted...")
		continue

	print(f"Running {subject} session {session} (working directory {directory})...")
	subprocess.run(f"matlab -r {nirs_script} {directory}", capture_output=True)
