import mne, random, statistics
import numpy as np
from mne_nirs.preprocessing import peak_power, scalp_coupling_index_windowed
from mne_nirs.visualisation import plot_timechannel_quality_metric
from glob import glob
from matplotlib import pyplot as plt
from scipy import signal
from scipy.ndimage import gaussian_filter
from scipy.stats import skew, kurtosis
from itertools import compress



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

        for dir_ind, directory in enumerate(subject_dirs[:2]):
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
            fnirs_participant = preprocess(fnirs_participant)
            self.task_scans.append(fnirs_participant)

        scan = self.task_scans[0]
        scan.load_data()
        freq = scan.info['sfreq']
        self.filter = HRF(freq).filter


    def convolve_hrf(self, nirx_obj):
        nirx_obj.load_data()
        convolution = lambda nirx : signal.fftconvolve(nirx, self.filter, mode = 'same')
        return nirx_obj.apply_function(convolution)
    
    def plot(self, first_signal, first_title, second_signal, second_title):
        x = [number for number in range(first_signal.shape[0])]

        figure, axis = plt.subplots(2, 1)

        axis[0].plot(x, first_signal)
        axis[0].set_title(first_title)

        axis[1].plot(x, second_signal)
        axis[1].set_title(second_title)

        plt.savefig('signal_conversion.jpeg')

    def compare(self, raw_nirx, convolved_nirx):
        meters = [self.calc_heart_rate_presence, self.calc_skewness_and_kurtosis, self.calc_snr, self.calc_pp, self.calc_sci]
        for meter in meters:
            response = meter(raw_nirx, 'raw')
            response = meter(convolved_nirx, 'convolved')


    def calc_pp(self, scan, state):
        raw_nirx = scan.load_data()

        raw_od = mne.preprocessing.nirs.optical_density(raw_nirx)
        raw_od, scores, times = peak_power(raw_od, time_window=10)

        figure = plot_timechannel_quality_metric(raw_od, scores, times, threshold=0.1)
        plt.savefig(f'{state}_powerpeak.jpeg')
        return True

    def calc_sci(self, scan, state):
        raw_nirx = scan.load_data()

        raw_od = mne.preprocessing.nirs.optical_density(raw_nirx)
        raw_sci = mne.preprocessing.nirs.scalp_coupling_index(raw_od)

        figure, axis = plt.subplots(1, 1)

        axis[0].hist(raw_sci)
        axis[0].set_title(f'{state} Scalp Coupling Index')
        plt.savefig(f'{state}_powerpeak.jpeg')
        return True

    def calc_snr(self, scan, state):
        # Load your raw NIRX data (already loaded as `raw` in this example)
        raw = scan.load_data()

        # 1. Filter the raw data to obtain the signal and noise components
        # Define the signal band (e.g., hemodynamic response band)
        signal_band = (0.01, 0.2)
        # Define the noise band (outside of the hemodynamic response)
        noise_band = (0.2, 1.0)  # Adjust as needed

        # Extract the signal in the desired band
        raw_signal = raw.copy().filter(signal_band[0], signal_band[1], fir_design='firwin')

        # Extract the noise in the out-of-band frequency range
        raw_noise = raw.copy().filter(noise_band[0], noise_band[1], fir_design='firwin')

        # 2. Calculate the Power Spectral Density (PSD) for signal and noise using compute_psd()
        psd_signal = raw_signal.compute_psd(fmin=signal_band[0], fmax=signal_band[1])
        psd_noise = raw_noise.compute_psd(fmin=noise_band[0], fmax=noise_band[1])

        # 3. Extract the power for each component
        signal_power = psd_signal.get_data().mean(axis=-1)  # Average power across frequencies for signal
        noise_power = psd_noise.get_data().mean(axis=-1)    # Average power across frequencies for noise

        # 4. Calculate SNR
        snr = signal_power / noise_power
        snr = sum(snr)/len(snr)
        print(f"{state} signal-to-noise ratio - {snr}")
        return snr

    def calc_skewness_and_kurtosis(self, scan, state):
        # Load your raw NIRX data (assuming `raw` is already loaded)
        raw = scan.load_data()

        # 1. Extract the time series data for each channel
        data = raw.get_data()  # shape: (n_channels, n_times)

        # 2. Compute skewness and kurtosis for each channel
        skewness = skew(data, axis=1)  # Calculate skewness along the time dimension
        kurtosis_vals = kurtosis(data, axis=1)  # Calculate kurtosis along the time dimension

        # 3. Display the results for each channel
        for ch_name, skew_val, kurt_val in zip(raw.ch_names, skewness, kurtosis_vals):
            print(f"{state} - Channel {ch_name}: Skewness = {skew_val:.3f}, Kurtosis = {kurt_val:.3f}")

    def calc_heart_rate_presence(self, scan, state):
        # Load your raw NIRX data (assuming it's already loaded as `raw`)
        raw = scan.load_data()

        # 1. Bandpass filter the raw data to isolate the heart rate frequency range
        heart_rate_band = (0.5, 2.0)  # Typical heart rate frequency range
        raw_filtered = raw.copy().filter(heart_rate_band[0], heart_rate_band[1], fir_design='firwin')

        # 2. Compute the Power Spectral Density (PSD) using compute_psd()
        psd = raw_filtered.compute_psd(fmin=heart_rate_band[0], fmax=heart_rate_band[1])

        # 3. Calculate the mean power across frequencies for each channel
        mean_psd = psd.get_data().mean(axis=-1)  # Average over frequency bins for each channel

        # 4. Identify the channel with the maximum power in the heart rate band
        max_power_channel_index = np.argmax(mean_psd)
        max_power_channel_name = raw_filtered.ch_names[max_power_channel_index]
        max_power_value = mean_psd[max_power_channel_index]

        # Print results
        print(f"Channel with maximum heart rate power: {max_power_channel_name} with power: {max_power_value:.4f}")

        # 5. Plot the PSD to visually inspect heart rate presence
        plt.figure(figsize=(10, 5))
        # Plot the mean power against the corresponding frequencies
        plt.plot(psd.freqs, mean_psd, label='Mean PSD')
        plt.axvline(x=60/70, color='r', linestyle='--', label='Expected HR (approx 70 bpm)')
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Mean Power')
        plt.title('Power Spectral Density of Heart Rate Frequency Band')
        plt.legend()
        plt.grid()
        plt.savefig(f'{state}_heart_rate_presence.jpeg')

    def test(self):
        # Load available samples
        self.load()

        # Create a copy of the original scan
        copy_nirx = self.task_scans[2].copy()
        copy_nirx.load_data()

        # Convolve the scan
        convolved_nirx = self.convolve_hrf(self.task_scans[2])

        # Compare original to convolved scan
        print(f"Original: {copy_nirx}\nConvolved: {convolved_nirx}")
        self.compare(copy_nirx, convolved_nirx)



class HRF():

    def __init__(self, freq, verbose = False):
        self.filter = [-0.004, -0.02, -0.05, 0.6, 0.6, 0, -0.1, -0.105, -0.09, -0.04, -0.01, -0.005, -0.001, -0.0005, -0.00001, -0.00001, -0.0000001]


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
        hrf_samples = round(30 * self.freq, 2)

        print("Expanding filter")
        while len(self.filter) < hrf_samples:
            self.filter = expand(self.filter) 

        plt.plot(self.filter)
        plt.title('Synthetic HRF Convolution Filter')
        plt.savefig('synthetic_hrf_0.jpeg')

        print('Compressing HRF with mean filter...')
        window = 2
        while len(self.filter) > hrf_samples:
            self.filter = [statistics.mean(self.filter[ind:ind+window]) for ind in range(len(self.filter) - window)]
 
        plt.plot(self.filter)
        plt.title('Synthetic HRF Convolution Filter')
        plt.savefig('synthetic_hrf_1.jpeg')

        print('Smoothing filter...')
        self.filter = smooth(self.filter)
        self.filter = smooth(self.filter)

        plt.plot(self.filter)
        plt.title('Synthetic HRF Convolution Filter')
        plt.savefig('synthetic_hrf_2.jpeg')

        print('Scaling filter...')
        self.filter = np.array(self.filter)
        self.scalar = np.array([0.5])
        self.filter = np.convolve(self.filter, self.scalar, mode = 'same')

        plt.plot(self.filter)
        plt.title('Synthetic HRF Convolution Filter - Scaled')
        plt.savefig('scaled-synthetic_hrf.jpeg')

        

def preprocess(scan):

    #try:
    # convert to optical density
    scan.load_data() 

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

    # bandpass filter
    haemo_bp = haemo.copy().filter(
        0.05, 0.7, h_trans_bandwidth=0.2, l_trans_bandwidth=0.02)

    return haemo
    #except:
    #    print(f"Scan failed to preprocess...\n{scan}")


if __name__ == '__main__':
    conv = convolver()
    conv.test()