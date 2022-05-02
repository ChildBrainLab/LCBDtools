import sys
sys.path.append('../../../')
from preprocessing.src import Plots

import os, shutil
import numpy as np
import math, scipy
import pandas as pd
from tqdm import tqdm
from datetime import datetime

class Flank:
    """
    Object which stores details of a single trial of Flanker task. I.e.,
    stimulus type, response and response time, prompt duration, block,
    etc., all stored in a dict attribute named 'meta'.

    :param signal: Time-series data of shape (timepoints,)
    :type signal: numpy.array
    """

    def __init__(self, meta=None):
        if meta is None:
            self.meta = {}
        else:
            self.meta = meta

    def score(self):
        if self.meta['resp'] == self.meta['corr_answer']:
            return True
        else:
            return False

class TaskReader:
    """
    Object used to read data from an LCBD PsychoPy Flanker session. Specifically,
    this object was built for the output from Version 3 of P-CAT Flanker task.
    It should be adapated as needed to suit further task developments.

    :param path: relative path to data file from the working directory
    :type path: str
    """
    def __init__(self, path):
        self.path = path

        # return tuple of filename and file extension
        fname, fext = os.path.splitext(path)

        if fext == ".csv":
            WS = pd.read_csv(self,path, sep=",", low_memory=False)
        elif fext == ".tsv":
            WS = pd.read_csv(self.path, sep="\t", low_memory=False)
        elif fext == ".xlsx":
            WS = pd.read_excel(self.path)

        try:
            # read all required / expected metadata
            self.participant = str(int(WS['participant'][0]))
            self.session = int(WS['session'][0])
            self.date = datetime(str(WS['date'][0]))

            self.sampleRate = float(WS['frameRate'][0])

        except (UnboundLocalError, KeyError) as e:
            print("Error: an incorrect key was not found during"
            " the loading of some files and they will be skipped.")
            print("Loading: ", self.path)

        # generate a Flank object for each column associated with a rating
        self.flankerSeries = [
            Flank(

            )
        ]



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
