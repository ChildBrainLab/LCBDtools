import sys
sys.path.append('..')
from src import Plots

import os, shutil
import numpy as np
import math, scipy
from scipy import signal
import pandas as pd
from tqdm import tqdm


# "/home/usr/schneiderc/study_data/ATV/task_behavioral_data/ATV_task/8001/8001_ATV_ratings_2020_Jan_29_1405"
class Viewing:
    """
    Object used to store data from a single trial (i.e., one viewing of one
    continuous video by one subject), with methods for operands within the trial

    :param path: relative path to data file in which time series is stored
    :type path: str
    """
    def __init__(self, path):
        self.path = path

        # return tuple of filename and file extension
        fname, fext = os.path.splitext(path)

        if fext == ".csv":
            WS = pd.read_csv(self.path, sep=',', low_memory=False)
        elif fext == ".tsv":
            WS = pd.read_csv(self.path, sep='\t', low_memory=False)
        elif fext == ".xlsx":
            WS = pd.read_excel(self.path)

        try:
            self.participant = str(int(WS['participant'][0]))
            # self.episode = str(WS['episode_file'][0])
            # self.episodeNumber = int(WS['episode'][0])
            # self.dimension = str(WS['rating_name'][0])
            self.episodeCode = os.path.basename(self.path)[4:7]
        except (UnboundLocalError, KeyError) as e:
            print("Error: an incorrect key was not found during"
            " the loading of some files and they will be skipped.")
            print("Loading: ", self.path)

        self.frameRates = np.array(WS['frameRate'])
        self.sampleRate = self.frameRates[0]
        # self.rating = np.array(WS['rating_amplitude'])
        self.rating = np.stack(
            [np.array(WS[col]) for col in WS.columns \
            if 'rating_amplitude' in col])
        # we know the order they viewed episodes in (self.episodeCode),
        # so it would be nice here to rearrange this object such that the order
        # of it is ABC
        # *****
        new_order = [[char for char in self.episodeCode].index(lett) for lett in list(sorted([char for char in self.episodeCode]))]
        # self.rating = self.rating[[char for char in self.episodeCode].index(lett) for lett in list(sorted([char for char in self.episodeCode]))]
        self.rating = self.rating[new_order]

        # self.time = np.array(WS['rating_time'])
        self.time = np.stack(
            [np.array(WS[col]) for col in WS.columns \
            if 'rating_time' in col])
        # the same re-ordering should occur here
        # ****
        # self.time = self.time[[char for char in self.episodeCode].index(lett) for lett in list(sorted([char for char in self.episodeCode]))]
        self.time = self.time[new_order]

        self.time_unit = 's'

    def QC(self):
        # if list(self.frameRates).count(self.frameRates[0]) \
        # != len(self.frameRates):
        #     print("Warning: frame rate is not continuous throughout!")
        #     raise ValueError
        print(np.where(self.frameRates != self.frameRates[0]))

    def fix_nan(self, val='interpol'):
        """
        Helper to fill occurances of NaNs in self.rating and self.time
        First trims tails, then retro-fills any remaining middle-wise

        :param val: if not 'interpol', float or int which will replace NaNs
        :type val: str, float, int
        """
        # HEAD
        i = 0
        while np.isnan(self.rating[i]):
            i += 1
        self.rating = self.rating[i:]
        self.time = self.time[i:]

        # TAIL
        i = len(self.rating)-1
        while np.isnan(self.rating[i]):
            i -= 1
        self.rating = self.rating[:i+1]
        self.time = self.time[:i+1]

        nans, x = np.isnan(self.rating), lambda z: z.nonzero()[0]
        self.rating[nans] = np.interp(x(nans), x(~nans), self.rating[~nans])

        nans, x = np.isnan(self.time), lambda z: z.nonzero()[0]
        self.time[nans] = np.interp(x(nans), x(~nans), self.time[~nans])

    def center(self):
        """
        Since ratings are taken on a scale of 0-2, transforms scale to be
        -1 to 1, i.e. center ylim around 0
        """
        self.rating = self.rating - 1

    def scale(self, ylim=(-1, 1)):
        """
        Linearly scales max and min values of the rating to the respective lower
        and upper bounds of ylim

        :param ylim: lower and upper bound of scale
        :type ylim: tuple of type int or float
        """
        self.rating = np.interp(
            self.rating,
            (self.rating.min(), self.rating.max()),
            (ylim[0], ylim[1]))

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
        sample_rate=1):
        """
        Resamples self.rating and self.time via numpy (tail padding)

        :param sample_rate: (default 1) new sample rate (in Hz) to which data
            are resampled
        :type sample_rate: float
        :param new_unit: (default None) if not None, reassigns self.time_unit
        """
        # self.rating, self.time = signal.resample(
        #     self.rating,
        #     num=math.floor(self.time[-1] * sample_rate),
        #     t=self.time)
        new_time = np.linspace(
            0,
            math.floor(self.time[-1]),
            num=math.floor(self.time[-1]*sample_rate))

        new_rating = np.interp(
            new_time,
            xp=self.time,
            fp=self.rating)

        self.time = new_time
        self.rating = new_rating

        # real_sample_rate = int(len(self.time) / self.time[-1])
        # R = real_sample_rate / sample_rate
        # pad_size = math.ceil(math.ceil(
        #     float(self.time.size)/R)*R - self.time.size)
        # # time_padded = np.append(self.time, np.zeros(pad_size)*np.NaN)
        # rating_padded = np.append(self.rating, np.zeros(pad_size)*np.NaN)
        # # self.time = scipy.nanmean(time_padded.reshape(-1, R), axis=1)
        # self.rating = scipy.nanmean(rating_padded.reshape(-1, R), axis=1)
        # # TODO: is this broken ?
        #
        # if new_unit is not None:
        #     self.time_unit = new_unit

        self.sampleRate = sample_rate

    def standardize(self):
        """
        Normalizes rating (i.e. subtract mean) and change variange to 1
        """
        self.rating = (self.rating - np.mean(self.rating)) / np.std(self.rating)

    def get_moving_average(self, x, w=10, mode='same'):
        """
        Builds moving average via convolution

        :param x: time-series data with shape (n_timepoints,)
        :type x: numpy.array
        :param w: (Default: 5) length of window over which averages are made
        :type w: int
        """
        return np.convolve(
            x,
            np.ones(w)/w,
            mode=mode)
