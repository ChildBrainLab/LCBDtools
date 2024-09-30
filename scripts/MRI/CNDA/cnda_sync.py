import xnat, os, shutil, sys, glob, zipfile, subprocess, json, shutil, gzip
from glob import glob
from zipfile import ZipFile


class CNDA:

    def __init__(self):
        username, password = self.read_credentials()
        url = 'https://cnda.wustl.edu'
        allocation = '/storage1/fs1/perlmansusan/Active/'

        self.lcbd_projects = {
            'NP1166' : {
                'directory':f'{allocation}moochie/study_data/CARE/CNDA_downloads/NP1166/',
                'bids-directory':f'{allocation}moochie/analysis/CARE/ME_MRI_data/',
                'photo-directory':f'{allocation}moochie/study_data/CARE/brain_photos/',
                'dcm2bids-config':f'{allocation}moochie/github/LCBDtools/scripts/MRI/dcm2bids/config.json',
                'accetable-qualities':['usable'], # usable, questionable, unusable
                'scans': [
                    'T1_MPRAGE_Cor',
                    'T1MPRAGECor',
                    'T1 MPRAGE Cor',
                    'dir98_AP_SBRef',
                    'dir98_AP',
                    'dir98_PA_SBRef',
                    'dir98_PA',
                    'movie_fmap_1',
                    'movie_fmap_2',
                    'movie_versionA_PA_SBRef',
                    'movie_versionA_PA',
                    'movie_versionB_PA_SBRef',
                    'movie_versionB_PA',
                    'movie_versionC_PA_SBRef',
                    'movie_versionC_PA'
                ],
                'excluded':[
                    'dir98_AP_'
                ],
                'post-processing': [self.debids] # Functions to run after syncing data for project
            }
        }

        self.session = xnat.connect(url, user = username, password = password, extension_types = False)

        self.sync()

    def read_credentials(self, creds = '/storage1/fs1/perlmansusan/Active/moochie/github/LCBDtools/scripts/MRI/CNDA/.xnat_auth'):
        contents = open(creds).read().split('\n')
        return contents[0], contents[1]

    def sync(self):
        for active_project in self.lcbd_projects.keys():
            self.active_project = active_project
            project_folder = self.lcbd_projects[active_project]['directory']
            dcm2bids_config = self.lcbd_projects[active_project]['dcm2bids-config']
            accetable_qualities = self.lcbd_projects[active_project]['accetable-qualities']
            excluded = self.lcbd_projects[active_project]['excluded']

            project = self.session.projects[active_project]
            print(f'Syncing {active_project}...')
            
            for subject in project.subjects.values():
                split = subject.label.split('_')
                if len(split) > 1:
                    self.subject_id = split[1]
                else:
                    self.subject_id = split[0]

                # Check if they need to be added to the project folder
                if os.path.exists(f'{project_folder}sub-{self.subject_id}/') == False:
                    os.makedirs(f'{project_folder}sub-{self.subject_id}/')
                
                experiments = []
                experiment_dates = []
                for experiment in project.subjects[subject.id].experiments.values():
                    if experiment_dates.count(experiment.date) > 0: # If resubmission of experiment
                        experiments.pop() # Remove the duplicate experiment
                    experiments.append(experiment) # Add experiment to experiments list
                    experiment_dates.append(experiment.date)
                        
                if len(experiments) < 1:
                    continue
                
                zipper = list(zip([experiment.date for experiment in experiments], experiments))
                zipper = sorted(zipper)
                experiment_dates, experiments = zip(*zipper)
                
                for exp_ind, experiment in enumerate(experiments):
                    self.exp_ind = exp_ind
                    self.experiment = experiment

                    print(f"Checking sub-{self.subject_id}/ses-{self.exp_ind}")
                    if os.path.exists(f"{project_folder}sub-{self.subject_id}/ses-{self.exp_ind}/"):
                        continue

                    scan_files = glob(f'{project_folder}sub-{self.subject_id}/ses-{self.exp_ind}/*')
                        
                    if len(scan_files) > 0: # If already downloaded
                        continue

                    print('\n\n\n')
                    print(f'New sessions available - Downloading {self.subject_id}/{self.exp_ind}/ ...')
                    
                    # Create the directory to prevent other cnda_sync's from download
                    os.makedirs(f'{project_folder}sub-{self.subject_id}/ses-{self.exp_ind}/')

                    # Download scan
                    experiment.download(f'{project_folder}sub-{self.subject_id}/scan.zip')
                    self.unzip(f'{project_folder}sub-{self.subject_id}/scan.zip', f'{project_folder}sub-{self.subject_id}/')

                    scan_folders = glob(f'{project_folder}sub-{self.subject_id}/*/scans/')
                    if len(scan_folders) > 1:
                        print(f"Multiple scan folders found for {self.subject_id}, skipping...")
                        continue
                    scan_folder = scan_folders[0]
                    print(f'Moving too {project_folder}sub-{self.subject_id}/ses-{self.exp_ind}/')

                    # Move directory to session directory
                    os.rmdir(f'{project_folder}sub-{self.subject_id}/ses-{self.exp_ind}/') # Remove shell session directory
                    shutil.move(scan_folder, f'{project_folder}sub-{self.subject_id}/ses-{self.exp_ind}/')
                    shutil.rmtree(scan_folder.split('scans/')[0])

                    # Remove all of the irrelavent scans
                    scans = glob(f'{project_folder}sub-{self.subject_id}/ses-{self.exp_ind}/*/')
                    for scan_folder in scans:
                        scan_type = scan_folder.split('/')[-2]

                        interesting = False

                        
                        for scan_of_interest in self.lcbd_projects[active_project]['scans']:
                            
                            if scan_of_interest in scan_type:
                                interesting = True
                                
                                #process = subprocess.Popen(f'dcm2niix {scan_folder}/', shell=True, stdout=subprocess.PIPE)
                                #process.wait()
                                break
                            
                        if interesting == True: # Check if the scan is usable
                            for scan_ind, scan in enumerate(experiment.scans):
                                scan_name =  str(scan_ind) + '_'.join(experiment.scans[scan].series_description.split(' '))
                                if scan_name == scan_type:
                                    print(f'Scan found! - {scan_name} - {experiment.scans[scan]}')
                                    if experiment.scans[scan].quality not in accetable_qualities:
                                        print(f"Unusuable scan {scan_name} for {self.subject_id}/V{self.exp_ind}")
                                        interesting = False
                                
                        for excluding in excluded:
                            if excluding in scan_type:
                                interesting = False

                        if interesting == False:
                            shutil.rmtree(scan_folder)

                    # Copy directory over to bids sourcedata directory for bidsifying
                    bids_folder = self.lcbd_projects[active_project]['bids-directory']
                    if os.path.exists(f"{bids_folder}sourcedata/{self.subject_id}/{self.exp_ind}/") == True:
                        print('Subject data exists in bids directory, rebuilding folder...')
                        shutil.rmtree(f"{bids_folder}sourcedata/{self.subject_id}/{self.exp_ind}/")

                    shutil.copytree(f"{project_folder}sub-{self.subject_id}/ses-{self.exp_ind}/", f'{bids_folder}sourcedata/{self.subject_id}/{self.exp_ind}/')

                    # Run BIDSkit on scans
                    dcm2bids_command = f'dcm2bids -d {bids_folder}sourcedata/{self.subject_id}/{self.exp_ind}/ -p sub-{self.subject_id} -s {self.exp_ind} -c {dcm2bids_config} -o {bids_folder}'
                    process = subprocess.Popen(dcm2bids_command, shell=True, stdout=subprocess.PIPE)
                    process.wait()

                    shutil.rmtree(f'{bids_folder}tmp_dcm2bids/sub-{self.subject_id}_ses-{self.exp_ind}/')

                    # Copy T1 scan to brain photos
                    photo_directory = self.lcbd_projects[active_project]['photo-directory']
                    T1_file = glob(f'{bids_folder}sub-{self.subject_id}/ses-{self.exp_ind}/**/*T1w*.nii.gz')
                    if len(T1_file) > 0: # If T1 file found
                        T1_file = T1_file.pop()
                        subject_photo_directory = f'{photo_directory}{self.subject_id}/V{self.exp_ind}/'
                        if os.path.exists(subject_photo_directory) == False:
                            os.makedirs(subject_photo_directory) # Create the photo directory
                        shutil.copy(T1_file, subject_photo_directory) # Copy the T1 file to the new directory

                        T1_file = glob(f"{subject_photo_directory}*T1*")[0]
                        self.ungunzip(T1_file)

                        print(f"Subject {self.subject_id} V{self.exp_ind} T1 available for brain photos")
                    else:
                        print(f"Subject {self.subject_id} V{self.exp_ind} T1 file not found")
                        continue

                    # Run post processing
                    for process in self.lcbd_projects[active_project]['post-processing']:
                        process()
            shutil.rmtree(f'{bids_folder}tmp_dcm2bids/')


    def unzip(self, filename, output_path):
        with ZipFile(filename) as zip_ref:
            zip_ref.extractall(output_path)
        os.remove(filename)

    
    def debids(self):
        # Adjust sidecards to remove the BIDS-URI syntax
        # In fmriprep 23.2.3 (latest) this syntax is causing
        # problems reading in field maps and applying
        # distortion corrections
        bids_dir = self.lcbd_projects[self.active_project]['bids-directory']

        # Update all fieldmap jsons IntendedFor fields
        fieldmaps_jsons = glob(f'{bids_dir}sub-{self.subject_id}/ses-{self.exp_ind}/**/*_epi.json')
        for fieldmap in fieldmaps_jsons:
            json_directory = fieldmap.split('/')
            json_directory.pop()
            json_directory = '/'.join(json_directory)

            fieldmap_json = json.load(open(fieldmap)) # Load the json

            intended_for = fieldmap_json['IntendedFor'] # Grab the intended for section

            if isinstance(intended_for, list) == False: # Format as list if not already formatted as such
                intended_for = [intended_for]

            # Iterate through each intended for entry
            for intension_ind, intension in enumerate(intended_for):
                for splits in ['bids::', f'sub-{self.subject_id}/']:
                    intension = intension.split(splits)
                    if len(intension) > 1: # If subject was in the intended for entry
                        intension = intension[1] # remove
                    else:
                        intension = intension[0] # Keep the string as is
                intended_for[intension_ind] = intension
            
            print(intended_for)
            fieldmap_json['IntendedFor'] = intended_for

            with open(fieldmap, 'w', encoding="utf-8") as json_file:
                json.dump(fieldmap_json, json_file, ensure_ascii=False, indent=4)

        return

    def ungunzip(self, filename):
        
        new_filename = filename.split('.gz')[0]
        with gzip.open(filename, 'rb') as f_in:
            with open(new_filename, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

if __name__ == '__main__':
    sync = CNDA() # Initialize a CNDA sync