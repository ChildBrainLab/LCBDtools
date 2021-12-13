import os, shutil
from os.path import join
import numpyas np
import math
from tqdm import tqdm

class TimeSeries:
    """
    Object which stores time-series data and offers various signal-related
    manipulations
    :param signal: Time-series data of shape (timepoints,)
    :type signal: numpy.array
    :param time: (Default: None) If None, defaults to np.arange(len(signal)),
        else array of shape (timepoints,)
    :type time: numpy.array
    :param sampleRate: (Default: 1024) frequency (in Hz) at which
        data was collected
    :type sampleRate: int
    """

    def __init__(self, signal, time=None, sampleRate=1024):
        self.signal = signal
        if time is None:
            self.time = np.arange(len(self.signal))
        else:
            self.time = time
        self.sampleRate = sampleRate
        self.meta = {}

    def fix_nan(self, val='interpol'):
        """
        Replaces any NaN encountered in signal with val
        :param val: (Default: interpol) If 'interpol', interpolates missing
            or NaN value. Else replaces with float or int.
        :type val: {'interpol', float, int}
        """
        signal = self.signal
        for loc in zip(*np.where(np.isnan(signal))):
            if (isinstance(val, float)) or (isinstance(val, int)):
                signal[loc] = val
            elif val == 'interpol':
                # account for potential of having NaN at a tail
                neighbors = []
                if loc[-1] > 0:
                    neighbors.append(signal[loc[-1]-1])
                if loc[-1] < len(signal):
                    neighbors.append(signal[loc[-1]+1])
                signal[loc] = np.mean(neighbors)
        self.signal = signal

    # TODO: peak by prominence / z-score
    def set_n_peaks(self, n=3, bin_ranges=None):
        """
        Counts number of peaks (timepoints with signal in certain amplitudinal
        range) found in self.signal within n possible bins.
        :param n: (Default: 3) number of amplitude bins
        :type n: int
        :param bin_ranges: (None) if none, arbitrarily defines bins based off
            range found in signal. If int / float, builds list of ranges based
            off this as max. If list, defines custom bin ranges.
        :type bin_ranges: length n list of tuples
        """
        if bin_ranges is None:
            max = math.ceil(np.max(self.signal))
        elif (isinstance(bin_ranges, int)) or (isinstance(bin_ranges, float)):
            max = bin_ranges

        max = max + (max % n) # make max equally divisible by n
        # make equally-sized ranges based off n and signal max
        self.bin_ranges = [( (i/n)*max, ((i+1)/n)*max ) for i in range(n)]

        # assert correct number of bin ranges
        message = "Number of bins supplied and n are not equal"
        if len(self.bin_ranges) != n:
            print(message)
            raise ValueError
        # TODO: give warning about overlapping bin ranges

        n_peaks = np.zeros(n)
        for timepoint in self.signal:
            for i, bin_range in enumerate(self.bin_ranges):
                if \
                (timepoint > bin_range[0]) and \
                (timepoint <= bin_range[1]):
                    n_peaks[i] += 1
        self.n_peaks = n_peaks

    def set_moving_average(self, x, w=5):
        """
        Builds moving average via convolution
        :param x: time-series data with shape (n_timepoints,)
        :type x: numpy.array
        :param w: (Default: 5) length of window over which averages are made
        :type w: int
        """
        self.mvg_avg = TimeSeries(
            np.convolve(
                x,
                np.ones(w),
                mode='full'))

    def set_PSD(self, x, window='boxcar'):
        """
        Estimate power spectral density using a periodogram
        :param window: (Default: boxcar) Desired window to use. If window is a
            string or tuple, it is passed to get_window to generate the window
            values, which are DFT-even by default. See get_window for a list of
            windows and required parameters. If window is array_like it will
            be used directly as the window and its length must be nperseg.
        :type window: str
        """
        from scipy.signal import periodogram

        self.freqs, self.PSD = periodogram(x, self.sampleRate)
