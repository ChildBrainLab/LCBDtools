import mne, random, statistics
import numpy as np
from mne_nirs.preprocessing import peak_power, scalp_coupling_index_windowed
from mne_nirs.visualisation import plot_timechannel_quality_metric
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
        convolution = lambda nirx_raw : signal.fftconvolve(nirx_raw, self.filter, mode = 'same')
        return raw_nirx.apply_function(convolution)
    
    def plot(self, first_signal, first_title, second_signal, second_title):
        x = [number for number in range(first_signal.shape[0])]

        figure, axis = plt.subplots(2, 1)

        axis[0].plot(x, first_signal)
        axis[0].set_title(first_title)

        axis[1].plot(x, second_signal)
        axis[1].set_title(second_title)

        plt.savefig('signal_conversion.jpeg')

    def compare(self, raw_nirx, convolved_nirx):

        raw_od = mne.preprocessing.nirs.optical_density(raw_nirx)
        raw_sci = mne.preprocessing.nirs.scalp_coupling_index(raw_od)

        convolved_od = mne.preprocessing.nirs.optical_density(convolved_nirx)
        convolved_sci = mne.preprocessing.nirs.scalp_coupling_index(convolved_od)

        figure, axis = plt.subplots(2, 1)

        axis[0].hist(raw_sci)
        axis[0].set_title('Raw Scalp Coupling Index')

        axis[1].hist(convolved_sci)
        axis[1].set_title('Convolved Scalp Coupling Index')

        plt.savefig('convolution_sci.jpeg')

        raw_od, scores, times = peak_power(raw_od, time_window=10)
        figure = plot_timechannel_quality_metric(raw_od, scores, times, threshold=0.1)
        plt.savefig('raw_powerpeak.jpeg')

        convolved_od, scores, times = peak_power(convolved_od, time_window=10)
        figure = plot_timechannel_quality_metric(convolved_od, scores, times, threshold=0.1)
        plt.savefig('convolution_powerpeak.jpeg')

    def test(self):
        self.load()

        copy_nirx = self.task_scans[2].copy()
        copy_nirx.load_data()
        convolved_nirx = self.convolve_hrf(self.task_scans[2])
        self.compare(copy_nirx, convolved_nirx)



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
            return gaussian_filter(filter, sigma=a)

        plt.plot(self.filter)
        plt.title('HRF Averages')
        plt.show()

        # Calculate number of samples per hemodynamic response function
        # Number of seconds  per HRF (12 seconds/HRF) times samples per second
        hrf_samples = round(12 * self.freq, 2)

        print("Expanding filter")
        while len(self.filter) < hrf_samples:
            self.filter = expand(self.filter) 

        plt.plot(self.filter)
        plt.title('Synthetic HRF Convolution Filter')
        plt.savefig('synthetic_hrf_0.jpeg')

        window = 2
        while len(self.filter) > hrf_samples:
            self.filter = [statistics.mean(self.filter[ind:ind+window]) for ind in range(len(self.filter) - window)]
 
        plt.plot(self.filter)
        plt.title('Synthetic HRF Convolution Filter')
        plt.savefig('synthetic_hrf_1.jpeg')

        self.filter = smooth(self.filter)

        plt.plot(self.filter)
        plt.title('Synthetic HRF Convolution Filter')
        plt.savefig('synthetic_hrf_2.jpeg')

        self.filter = np.array(self.filter)
        self.scalar = np.array([0.5])
        self.filter = np.convolve(self.filter, self.scalar, mode = 'same')

        plt.plot(self.filter)
        plt.title('Synthetic HRF Convolution Filter - Scaled')
        plt.savefig('scaled-synthetic_hrf.jpeg')

        
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