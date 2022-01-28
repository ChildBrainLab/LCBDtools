import os, shutil
from os.path import join
import numpy as np
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

    def __init__(self, signal, time=None, sampleRate=1024, meta={}, unit='s'):
        self.signal = signal
        if time is None:
            self.time = np.arange(len(self.signal))
        else:
            self.time = time
        self.sampleRate = sampleRate
        self.meta = meta
        self.unit = unit

    def fix_nan(self, val='interpol'):
        """
        Helper to fill occurances of NaNs in self.signal and self.time
        First trims tails, then retro-fills any remaining middle-wise

        :param val: (Default: 'interpol') if not 'interpol', float or int which
            will replace NaNs
        :type val: str, float, int
        """
        # HEAD
        i = 0
        while np.isnan(self.signal[i]):
            i += 1
        self.signal = self.signal[i:]
        self.time = self.time[i:]

        # TAIL
        i = len(self.signal)-1
        while np.isnan(self.signal[i]):
            i -= 1
        self.signal = self.signal[:i+1]
        self.time = self.time[:i+1]

        nans, x = np.isnan(self.signal), lambda z: z.nonzero()[0]
        self.signal[nans] = np.interp(x(nans), x(~nans), self.signal[~nans])

        nans, x = np.isnan(self.time), lambda z: z.nonzero()[0]
        self.time[nans] = np.interp(x(nans), x(~nans), self.time[~nans])

    def center(self, difference=1):
        """
        Substracts 'difference' from signal

        :param difference: amount substracted from signal
        :type difference: int, float
        """
        self.signal = self.signal - difference

    def scale(self, ylim=(-1, 1)):
        """
        Linearly scales max and min values of the signal to the respective lower
        and upper bounds of ylim

        :param ylim: lower and upper bound of scale
        :type ylim: tuple of type int or float
        """
        self.signal = np.interp(
            self.signal,
            (self.signal.min(), self.signal.max()),
            (ylim[0], ylim[1]))

    def standardize(self):
        """
        Normalizes rating (i.e. subtract mean) and scale variance to 1
        """
        self.rating = (self.rating - np.mean(self.rating)) / np.std(self.rating)


    def lag_correct(self):
        """
        During recording, skipped frames can add up to significant differences
        in the number of samples collected between subjects, even though the
        start / stop time are correct, and the sample rate generally holds true.

        This method regularizes time axis values along an ARTIFICIAL new
        axis, such that they are equally spaced apart.
        """
        self.time = np.linspace(0, self.time[-1], num=len(self.time))

    def resample(
        self,
        sample_rate=1,
        new_unit=None):
        """
        Resamples self.signal and self.time with numpy (tail padding)

        :param sample_rate: (default 1) new sample rate (in Hz) to which data
            are resampled
        :type sample_rate: float
        :param new_unit: (default None) if not None, reassigns self.unit
        :type new_unit: str
        """
        new_time = np.linspace(
            0,
            math.floor(self.time[-1]),
            num=math.floor(self.time[-1]*sample_rate))

        new_signal = np.interp(
            new_time,
            xp=self.time,
            fp=self.signal)

        self.time = new_time
        self.signal = new_signal
        self.sampleRate = sample_rate
        if new_unit is not None:
            self.unit = new_unit

    def get_moving_average(self, x, w=10, mode='same'):
        """
        Builds moving average via convolution

        :param x: data with shape (n_timepoints,) or (n_samples,)
        :type x: numpy.array
        :param w: (Default: 5) length of window over which averages are made
        :type w: int
        """
        return np.convolve(
            x,
            np.ones(w)/w,
            mode=mode)

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
