import glob, tensorflow, mne

from glob import glob

from matplotlib import pyplot as plt

from scipy.ndimage import gaussian_filter







class convolver:



    def __init__(self):

        self.bids_directory = '../../../../../analysis/P-CAT/flanker_nirs/'

        self.ouput_directory = ''



        self.ex_subs = []



        self.ROIs = {

            'Left Frontal': ['S3_D2 hbo', 'S4_D2 hbo'],

            'Right Frontal': ['S5_D3 hbo',  'S6_D3 hbo'],

            'Left Temporal': ['S1_D1 hbo', 'S2_D1 hbo', 'S2_D2 hbo'],

            'Right Temporal': ['S7_D3 hbo', 'S7_D4 hbo', 'S8_D4 hbo']

        }



    def load(self):

        # make a list where all of the scans will get loaded into

        self.task_scans = []



        # Load in master file with scan order info

        subject_dirs = glob(f'{self.bids_directory}*/')



        for dir_ind, directory in enumerate(subject_dirs):

            for excluded in self.ex_subs:

                if excluded in directory:

                    print(f"Deleting {directory}")

                    del subject_dirs[dir_ind]



        for subject_dir in subject_dirs:

            mat_files = glob(subject_dir + '*_probeInfo.mat') + glob(subject_dir + '*_probeinfo.mat')

            if len(mat_files) == 0:

                print(f"Missing probe info for {subject_dir}...\n skipping\s")

                continue

            

            print(subject_dir)

            

            fnirs_participant = mne.io.read_raw_nirx(subject_dir)

            self.task_scans.append(fnirs_participant)





    def preprocess(self):

        #Here the signals collected from the various channels are converted to relaative hemoglobin concentration instead of a frequency waveform,

        #which is what we were working with above before preprocessing



        # make a list where the preprocessed scans will go

        self.preprocessed_scans = []

        # for each dyad scan in scans

        for scan in self.task_scans:

            print(scan)

            try:

                # convert to optical density

                raw_od = mne.preprocessing.nirs.optical_density(scan)



                # scalp coupling index

                sci = mne.preprocessing.nirs.scalp_coupling_index(raw_od)

                raw_od.info['bads'] = list(compress(raw_od.ch_names, sci < 0.5))



                if len(raw_od.info['bads']) > 0:

                    print("Bad channels in subject", raw_od.info['subject_info']['his_id'], ":", raw_od.info['bads'])



                # temporal derivative distribution repair (motion attempt)

                tddr_od = mne.preprocessing.nirs.tddr(raw_od)





                bp_od = tddr_od.filter(0.01, 0.5)



                # haemoglobin conversion using Beer Lambert Law (this will change channel names from frequency to hemo or deoxy hemo labelling)

                haemo = mne.preprocessing.nirs.beer_lambert_law(bp_od, ppf=0.1)



                self.preprocessed_scans.append(haemo)

            except:

                print(f"Scan failed to preprocess...\n{scan}")



    def build_hrf():

        filter = [0, 0.8, 0.2, -0.25, -0.20, -0.125, -0.05, -0.01, -0.001]



        def expand(filter):

            new_filter = []

            for ind, data in enumerate(filter):

                new_filter.append(data)

                if ind + 1 < len(filter):

                    new_filter.append((data + filter[ind + 1])/2)

            return new_filter



        def smooth(filter, a = 2):

            return gaussian_filter(filter, sigma=a)



        plt.plot(filter)

        plt.show()



        filter = expand(filter)

        filter = expand(filter)

        filter = expand(filter)

        filter = smooth(filter)



        plt.plot(filter)

        plt.title('Synthetic HRF Convolution Filter')

        plt.show()










