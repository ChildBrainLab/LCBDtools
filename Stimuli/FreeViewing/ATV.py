import sys
sys.path.append('..')
from src import Plots
from src.TimeSeries import TimeSeries

import os, shutil
import numpy as np
import math, scipy
from scipy import signal
import pandas as pd
from tqdm import tqdm


# "/home/usr/schneiderc/study_data/ATV/task_behavioral_data/ATV_task/8001/8001_ATV_ratings_2020_Jan_29_1405"
class TrialReader:
    """
    Object used to read data from a single trial (i.e., one continuous run
    of PsychoPy experiment, where one or more runs are completed),
    and from it generate the more flexible src.TimeSeries object, with info
    from the session written to the src.TimeSeries.meta dictionary

    :param path: relative path to data file from the working directory
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
            # read all required / expected metadata
            self.participant = str(int(WS['participant'][0]))
            # self.episode = str(WS['episode_file'][0])
            # self.episodeNumber = int(WS['episode'][0])
            # self.dimension = str(WS['rating_name'][0])
            self.episodeCode = str(WS['episodeCode'][0])
            # read date and time
            # self.sessionTime = datetime.strptime(WS['date'], '%Y_%b_%d_%I%M%p')

        except (UnboundLocalError, KeyError) as e:
            print("Error: an incorrect key was not found during"
            " the loading of some files and they will be skipped.")
            print("Loading: ", self.path)

        self.frameRates = np.array(WS['frameRate'])
        self.sampleRate = self.frameRates[0]

        # generate a TimeSeries object for each column associated with a rating
        self.ratingsSeries = [
            TimeSeries(
                np.array(WS[col]),
                time=np.array(WS["rating_time"+col.strip("rating_amplitude")]),
                sampleRate=self.sampleRate,
                meta={
                    'participant': self.participant,
                    'episode': ord(
                        self.episodeCode[int(
                            col.strip("rating_amplitude"))-1])%32-1,
                    # 'episode': self.episodeCode.find(
                    #     self.episodeCode[int(col.strip("rating_amplitude"))-1]),
                    'viewingOrder': self.episodeCode})\
            for col in WS.columns if 'rating_amplitude' in col]