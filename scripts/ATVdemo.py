import argParser
import sys
sys.path.append('..')

import os, shutil
from os.path import join
from tqdm import tqdm
import pdb
import numpy as np

import pdb

# LCBD modules
from src import Plots
from FreeViewing.ATV import TrialReader


args = argParser.main([
    "data_folder",
    "TR",
    "run",
    "ex_subs",
    "participant_num_len"
])

# "/data/perlman/moochie/user_data/SchneiderClayton/\
# studyData/ATV_LCBD_copy_120821/data"
dataDir = args.dataFolder

episode = args.run

# list of all fnames in dataDir if the first n characters are not bad subjects
# they are full paths joined to data directory
fnames = [join(dataDir, fname) for fname in os.listdir(dataDir)\
    if os.path.basename(fname)[:args.participant_num_len] not in args.ex_subs]

dataset = []
for fpath in tqdm(fnames):
    try:
        # for each filepath in the list, run an ATV.TrialReader builder
        # add each src.TimeSeries object generated from the TrialReader to
        # the dataset list
        for ts in TrialReader(fpath):
            dataset.append(ts)
    except:
        pass

print("Number of viewings in dataset:", len(dataset))

# dataset = [ts for ts in dataset if ts.meta['episode'] == episode]
#
# # also then sort by subject number
# idx = np.argsort([view.participant for view in dataset])
# dataset = [dataset[i] for i in idx]

for ts in dataset:
    ts.fix_nan()
    ts.lag_correct()
    ts.resample(sample_rate=args.TR)
    # some subjects didn't understand the actual scale...
    # these are found in the study notes
    # ATV_data_tracker_20200312.xlsx
    # if they didn't and we need to reverse it:
    # if view.participant in subjectsWhoDidntUnderstand:
    #     view.rating = ((view.rating-1)*-1)+1

# plot to view lengths of dataset in samples
# import matplotlib.pyplot as plt
# plt.hist([len(view.rating) for view in dataset], bins=20)
# plt.show()

# get a plain old raw subject rating
# for view in dataset[:1]:
#     Plots.plot_xy_line(
#         view.time,
#         view.rating,
#         xlabel="Time (s)",
#         ylabel="Subject " + str(view.participant) + " Raw Rating",
#         fig_fname="raw_"+str(view.participant))

Plots.plot_xy_line(
    dataset[0].time,
    dataset[0].signal,
    xlabel="Time (" + dataset[0].time_unit + ")",
    title="Subject " + str(dataset[0].participant) + " Raw Rating")

# for plotting with 'same' padding i.e. time as x-axis instead of TR
Plots.plot_xy_line(
    dataset[0].time,
    mvg_avgs[0],
    xlabel="Time (" + dataset[0].time_unit + ")",
    title="Subject " + str(dataset[0].participant) + \
    ' Moving Average w =' + str(w))

Plots.plot_colormesh(
    np.array([view.signal/2 for view in dataset]),
    xlabel='Time (TRs)',
    ylabel='Subject',
    yticks=[view.participant for view in dataset])
