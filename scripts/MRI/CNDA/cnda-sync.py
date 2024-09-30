import xnat, os, shutil, boto3, sys, glob
from glob import glob


class CNDA:

    def __init__(self):
        username = 'dennys'
        password = '!Autumn?Max!?25'
        url = 'https://cnda.wustl.edu'

        self.active_projects = {
            'NP1166': 's3://moochie-archive/study_data/CARE/CNDA_downloads/NP1166/'
        }

        self.project_bids = {
            'NP1166': '/mnt/moochie/analysis/CARE/BIDS_data/'
        }

        self.session = xnat.connect(url, user = username, password = password, extension_types = False)

    def sync(self):
        archive_subjects = scanner.scan('s3://moochie-archive/study_data/CARE/CNDA_downloads/NP1166/')

        
        experiments = cnda.session.projects['NP1166'].subjects['CNDA7_S00188'].experiments.values()

        zipper = list(zip([experiment.date for experiment in experiments], experiments))
        zipper = sorted(zipper)
        experiment_dates, experiments = zip(*zipper)
        for exp_ind, experiment = 
        glob('/mnt/moochie/analysis/CARE/BIDS_data/sourcedata/51121/2/7*/**/*.nii*', recursive = True)



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
