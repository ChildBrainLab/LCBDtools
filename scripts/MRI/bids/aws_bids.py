import os, shutil, boto3
from glob import glob
import sys

class scanner:

    def __init__(self, input_dir = None, output_dir = None):
        if input_dir == None:
            self.input_dir = os.getenv('input_dir')
        else:
            self.input_dir = input_dir
        if output_dir == None:
            self.output_dir = os.getenv('output_dir') # Folders of interest
        else:
            self.output_dir = output_dir

        self.s3 = boto3.resource('s3')


    def sync(self, ses = None):
        source_sessions = self.scan(self.input_dir, ses)
        bids_sessions = self.scan(self.output_dir, ses)

        print(source_sessions)
        print(bids_sessions)            
        unbids_convd = []
        for session in source_sessions:
            if session not in bids_sessions:
                unbids_convd.append(os.path.split(session)[0])

        unbids_convd = sorted(unbids_convd)
        print(unbids_convd)

        self.save(unbids_convd)

    def scan(self, folder, ses = None, save = False):
        # Look through an AWS bucket folder for subjects
        if folder[-1:] != '/':
            folder = folder + '/'
        
        if ses == None: # If ses not specify grab all sessions
            ses = ['ses-0', 'ses-1', 'ses-2']

        split = folder[5:].split('/')    

        bucket = self.s3.Bucket(split.pop(0))
        folder = '/'.join(split)
        sessions = set()
        for item in bucket.objects.filter(Prefix = folder + 'sub-'):
            split = item.key[len(folder):].split('/') # Extract
            if len(split) > 1:
                if split[1] not in ses:
                    continue
                subject = split[0] + '/' + split[1]
                if subject not in sessions:
                    sessions.add(subject.split('sub-')[1])
        return list(sessions)

    def save(self, unbids_convd):
        # open the participant list file
        print(f"Saving bids_list.txt: {', '.join(unbids_convd)}")

        f = open("bids_list.txt", 'w')

        for sub in unbids_convd:
            f.write(sub.replace("sub-", ""))
            f.write('\n')
        f.close()

        print(f"Saved bids_list.txt")

aws_scanner = scanner(sys.argv[1], sys.argv[2])
aws_scanner.sync(sys.argv[3])
