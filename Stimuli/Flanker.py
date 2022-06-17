import sys

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

    def eval(self):
        """
        Evaluate whether the flank response was correct or incorrect

        :return: True if correct, False if incorrect
        """
        if self.meta['response'] == self.meta['corr_answer']:
            self.meta['correct'] = True
        else:
            self.meta['correct'] = False

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
            WS = pd.read_csv(self.path, sep=",", low_memory=False)
        elif fext == ".tsv":
            WS = pd.read_csv(self.path, sep="\t", low_memory=False)
        elif fext == ".xlsx":
            WS = pd.read_excel(self.path)

        try:
            # read all required / expected metadata
            self.participant = str(int(WS['participant'][0]))
            self.session = int(WS['session'][0])
            self.date = datetime.strptime(
                str(WS['date'][0]),
                '%Y_%b_%d_%H%M')

            self.sampleRate = float(WS['frameRate'][0])

        except (UnboundLocalError, KeyError) as e:
            print("Error: an incorrect key was not found during"
            " the loading of some files and they will be skipped.")
            print("Loading: ", self.path)

        # some general cleaning of the file / preparing for errors lol
        # TODO: if a key_resp{_block}.rt column doesn't exist for a given block,
        # let's add it in as a NaN series
        blocks = list(set([col.strip("_trial.thisRepN").strip("block") for \
            col in WS.columns if "trial.thisRepN" in col]))

        for block in blocks:
            if block == "1":
                if "key_resp.rt" not in WS.columns:
                    WS["key_resp.rt"] = " "
            else:
                if "key_resp_{}.rt".format(block) not in WS.columns:
                    WS["key_resp_{}.rt".format(block)] = " "

        # generate a Flank object for each column associated with a rating
        self.flankerSeries = []

        trial_n = 0
        for row_i, row in WS.iterrows():

            if "stimuli" not in str(row["stimuli_file"]):
                continue
            else:
                trial_n += 1

            self.flankerSeries.append(Flank(meta={
                "trial_n": trial_n,
                "block": int(row['stimuli_file'].split('_')[1].strip('block')),
                "corr_answer": str(row['corrAns']),
                "stim_file": str(row['stimuli_file']),
                "directional": True if row['stimuli_file'].split('_')[2] == \
                    "D" else False,
                "congruent": True if row['stimuli_file'].split('_')[3][0] == \
                    "C" else False,
                "stim_start_time": float(row['stimuli_{}.started'.format(
                    row['stimuli_file'].split('_')[1].strip(
                        'block'))]),
                "stim_stop_time": float(row['stimuli_{}.stopped'.format(
                    # special case because sometimes we have null ones of these
                    row['stimuli_file'].split('_')[1].strip(
                        'block'))]) if \
                        not pd.isnull(row['stimuli_{}.stopped'.format(
                            row['stimuli_file'].split('_')[1].strip('block'))])\
                            else float(row['stimuli_{}.started'.format(
                                row['stimuli_file'].split('_')[1].strip(
                                'block'))])+float(1.01),
                "response": str(row['key_resp_{}.keys'.format(
                    row['stimuli_file'].split('_')[1].strip(
                        'block'))]) if \
                    int(row['stimuli_file'].split('_')[1].strip(
                        'block')) > 1 else str(row['key_resp.keys']),
                "response_time": float(row['key_resp_{}.rt'.format(
                    row['stimuli_file'].split('_')[1].strip(
                        'block'))]) if \
                    int(row['stimuli_file'].split('_')[1].strip(
                        'block')) > 1 else float(row['key_resp.rt']),
                "fixation_start_time": float(row['fixation_{}.started'.format(
                    row['stimuli_file'].split('_')[1].strip(
                        'block'))]) if \
                    int(row['stimuli_file'].split('_')[1].strip(
                        'block')) > 1 else float(row['fixation.started']),
                "fixation_stop_time": float(row['fixation_{}.stopped'.format(
                    row['stimuli_file'].split('_')[1].strip(
                        'block'))]) if \
                    int(row['stimuli_file'].split('_')[1].strip(
                        'block')) > 1 else float(row['fixation.stopped'])}))
