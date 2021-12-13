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
from FreeViewing import Viewings


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
fnames = [join(dataDir, fname) for fname in os.listdir(dataDir)\
    if os.path.basename(fname)[:args.participant_num_len] not in args.ex_subs]

dataset = []
for fpath in tqdm(fnames):
    try:
        # build Viewing object for each filepath in scan
        dataset.append(Viewings.Viewing(fpath))
    except:
        pass

# dataset = []
# with tqdm(total=total) as pbar:
#     for sub in subjectFiles:
#         for fpath in subjectFiles[sub]:
#             if os.path.basename(fpath)[:3] not in badSubs:
#                 try:
#                     dataset.append(Viewings.Viewing(fpath))
#                 except:
#                     pass
#             pbar.update(1)
print("Length of dataset:", len(dataset))
print("Dataset[0]:", dataset[0])

quit()
# mvg_avgs = []
# w = int(dataset[0].sampleRate) * args.TR

dataset = [view for view in dataset if view.episodeNumber == episode]

# also then sort by subject number
idx = np.argsort([view.participant for view in dataset])
dataset = [dataset[i] for i in idx]

for view in dataset:
    view.fix_nan()
    view.lag_correct()
    view.resample(sample_rate=0.5)
    # some subjects didn't understand the actual scale...
    # these are found in the study notes
    # ATV_data_tracker_20200312.xlsx
    # if they didn't and we need to reverse it:
    if view.participant in subjectsWhoDidntUnderstand:
        view.rating = ((view.rating-1)*-1)+1

# import matplotlib.pyplot as plt
# plt.hist([len(view.rating) for view in dataset], bins=20)
# plt.show()

# pdb.set_trace()

# get plain old raw subject rating
for view in dataset:
    Plots.plot_xy_line(
        view.time,
        view.rating,
        xlabel="Time (s)",
        ylabel="Subject " + str(view.participant) + " Raw Rating",
        fig_fname="raw_"+str(view.participant))
# Plots.plot_xy_line(
#     dataset[0].time,
#     dataset[0].rating,
#     xlabel="Time (" + dataset[0].time_unit + ")",
#     title="Subject " + str(dataset[0].participant) + " Raw Rating")

# # for plotting with 'same' padding i.e. time as x-axis instead of TR
# Plots.plot_xy_line(
#     dataset[0].time,
#     mvg_avgs[0],
#     xlabel="Time (" + dataset[0].time_unit + ")",
#     title="Subject " + str(dataset[0].participant) + \
#     ' Moving Average w =' + str(w))

Plots.plot_colormesh(
    np.array([view.rating/2 for view in dataset]),
    xlabel='Time (TRs)',
    ylabel='Subject',
    yticks=[view.participant for view in dataset])
