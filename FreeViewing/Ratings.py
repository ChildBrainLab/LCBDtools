import sys
sys.path.append('..')
from src import Plots

import os, shutil
import numpy as np
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
            WS = pd.read_csv(self.path, sep=",")
        elif fext == ".tsv":
            WS = pd.read_csv(self.path, sep='\t')
        elif fext == ".xlsx":
            WS = pd.read_excel(self.path)

        self.participant = str(WS['participant'][0])
        self.episode = str(WS['episode_file'][0])
        self.episodeNumber = int(WS['episode'][0])
        self.dimension = str(WS['rating_name'][0])

        self.frameRates = np.array(WS['frameRate'])
        self.sampleRate = self.frameRates[0]
        self.rating = np.array(WS['rating_amplitude'])
        self.time = np.array(WS['rating_time'])

    def QC(self):
        # if list(self.frameRates).count(self.frameRates[0]) \
        # != len(self.frameRates):
        #     print("Warning: frame rate is not continuous throughout!")
        #     raise ValueError
        print(np.where(self.frameRates != self.frameRates[0]))

    def fix_nan(self, val='interpol'):
        """
        Helper to fill occurances of NaNs in self.rating and self.time

        :param val: if not 'interpol', float or int which will replace NaNs
        :type val: str, float, int
        """
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

    def standardize(self):
        """
        Normalizes rating (i.e. subtract mean) and change variange to 1
        """
        self.rating = (self.rating - np.mean(self.rating)) / np.std(self.rating)
