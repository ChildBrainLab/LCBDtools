import mne
import numpy as np
from glob import glob
from matplotlib import pyplot as plt
from scipy.ndimage import gaussian_filter
from scipy import signal



class convolver:

    def __init__(self, freq = None):

        self.bids_dir = '/storage1/fs1/perlmansusan/Active/moochie/analysis/P-CAT/flanker_nirs/'
        self.ouput_directory = ''

        self.ex_subs = []
        

    def load(self, bids_dir = None):
        if bids_dir != None:
            self.bids_dir = bids_dir

        # make a list where all of the scans will get loaded into
        self.task_scans = []

        # Load in master file with scan order info
        subject_dirs = glob(f'{self.bids_dir}*/')[:3]
        print(subject_dirs)

        for dir_ind, directory in enumerate(subject_dirs):
            for excluded in self.ex_subs:
                if excluded in directory:
                    print(f"Deleting {directory}")
                    del subject_dirs[dir_ind]

        for subject_dir in subject_dirs:
            mat_files = glob(subject_dir + '*_probeInfo.mat') + glob(subject_dir + '*_probeinfo.mat')
            if len(mat_files) == 0:
                print(f"Missing probe info for {subject_dir}...\n")
                continue
            
            print(subject_dir)
            
            fnirs_participant = mne.io.read_raw_nirx(subject_dir)
            self.task_scans.append(fnirs_participant)

        scan = self.task_scans[0]
        scan.load_data()
        freq = scan.info['sfreq']
        self.filter = HRF(freq).filter


    def convolve_hrf(self, raw_nirx):
        raw_nirx.load_data()
        raw_sfreq = raw_nirx.info['sfreq']
        raw_signal = raw_nirx.get_data('all')
        convolution = lambda nirx_raw : signal.fftconvolve(nirx_raw, self.filter, mode = 'same')

        convolved_nirx = raw_nirx.apply_function(convolution)
        convolved_signal = convolved_nirx.get_data('all')

        self.compare(raw_signal[0,:300], 'Raw Signal', convolved_signal[0, :300], 'Convolved Signal')
    
    def compare(self, first_signal, first_title, second_signal, second_title):
        x = [number for number in range(first_signal.shape[0])]

        figure, axis = plt.subplots(2, 1)

        axis[0].plot(x, first_signal)
        axis[0].set_title(first_title)

        axis[1].plot(x, second_signal)
        axis[1].set_title(second_title)

        plt.show()
    
    def test(self):
        self.load()
        self.convolve_hrf(self.task_scans[0])

class HRF():

    def __init__(self, freq, verbose = False):
        self.filter = [-0.1, 0.8, 0.7, -0.25, -0.20, -0.125, -0.05, -0.01, -0.001]

        self.freq = freq

        def expand(filter):
            new_filter = []
            for ind, data in enumerate(filter):
                new_filter.append(data)
                if ind + 1 < len(filter):
                    new_filter.append((data + filter[ind + 1])/2)
            return new_filter

        def smooth(filter, a = 2):
            return gaussian_filter(self.filter, sigma=a)

        plt.plot(self.filter)
        plt.title('HRF Averages')
        plt.show()

        # Calculate number of samples per hemodynamic response function
        # Number of seconds  per HRF (12 seconds/HRF) times samples per second
        hrf_samples = round(12 * self.freq, 2)

        while len(self.filter) < hrf_samples:
            # How can we slow this down to not double?
            self.filter = expand(self.filter) 
            print("Expanding filter")

        plt.plot(self.filter)
        plt.title('Synthetic HRF Convolution Filter')
        plt.show()

        self.filter = np.array(self.filter)
        self.scalar = np.array([0.5])
        self.filter = np.convolve(self.filter, self.scalar, mode = 'same')

        plt.plot(self.filter)
        plt.title('Synthetic HRF Convolution Filter - Scaled')
        plt.show()




        
"""
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
                print(f"Scan failed to preprocess...\n{scan}")"""



if __name__ == '__main__':
    conv = convolver()
    conv.test()