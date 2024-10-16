import mne, random
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
            return gaussian_filter(filter, sigma=a)

        plt.plot(self.filter)
        plt.title('HRF Averages')
        plt.show()

        # Calculate number of samples per hemodynamic response function
        # Number of seconds  per HRF (12 seconds/HRF) times samples per second
        hrf_samples = 64 #round(12 * self.freq, 2)

        print("Expanding filter")
        self.filter = self.interpolate(self.filter, hrf_samples) 
 
        self.filter = smooth(self.filter)

        plt.plot(self.filter)
        plt.title('Synthetic HRF Convolution Filter')
        plt.savefig('synthetic_hrf.jpeg')

        self.filter = np.array(self.filter)
        #self.scalar = np.array([0.5])
        #self.filter = np.convolve(self.filter, self.scalar, mode = 'same')

        plt.plot(self.filter)
        plt.title('Synthetic HRF Convolution Filter - Scaled')
        plt.savefig('scaled-synthetic_hrf.jpeg')

    def interpolate(self, filter, size):
        old_size = len(filter)
        indices = self.bin_index(filter)
        
        count = 0
        while len(filter) < size:
            # If we've fully interpolated, reset
            if indices == []:
                indices = self.bin_index(filter)
            print(indices)
            current_indice = indices[0]

            # Interpolate and add value
            if len(indices) > 1:
                for next_index in sorted(indices):
                    if next_index > current_indice:
                        break

                interpolation = (filter[current_indice] + filter[next_index])/2
            else:
                interpolation = filter[current_indice]

            filter.insert(current_indice, interpolation)

            del indices[0]

            indices = [index + 1 if index > current_indice else index for index in indices]

            count += 1# Increment count
        print(f"Filter size increased from {old_size} to {len(filter)}")
        return filter
            
    def bin_index(self, filter, indices = None, position = None, direction = -1):

        # Define empty list basecase
        if len(filter) == 0:
            return []

        if indices == None:
            indices = [index for index in range(len(filter))]
            position = int(len(filter)/2)
        discovered_indices = [position]

        # Define base cases for last position in filter recursion
        if len(filter) == 1:
            return discovered_indices
        
        # Figure out recursion logic using random number generator
        if direction == 'random':
            direction = random.uniform(0, 1)
            if direction <=0.5:
                direction = -1
            else:
                direction = 1
            
        # Calulcate metrics for next recusion
        half_size = int(len(filter)/2)
        quarter_size = int(len(filter)/4)

        first_position = position + (direction*quarter_size) # Find position in original filter
        if first_position == position:
            first_position += direction

        second_position = position - (direction*quarter_size)
        if second_position == position:
            second_position -= direction
        print(f"Position: {position} | first - {first_position} - second - {second_position}")
        
        if direction == 1:
            first_indices = self.bin_index(filter[half_size:], indices[half_size:], first_position)
            second_indices = self.bin_index(filter[:(half_size - direction)], indices[:(half_size - direction)], second_position)
        if direction == -1:    
            first_indices = self.bin_index(filter[:half_size], indices[:half_size], first_position)
            second_indices = self.bin_index(filter[(half_size - direction):], indices[(half_size - direction):], second_position)
        # zip the indice together
        for ind in range(min(len(first_indices), len(second_indices))):
            discovered_indices += [first_indices[0], second_indices[0]]
            del first_indices[0], second_indices[0]
        discovered_indices += first_indices
        discovered_indices += second_indices
        return discovered_indices

        
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