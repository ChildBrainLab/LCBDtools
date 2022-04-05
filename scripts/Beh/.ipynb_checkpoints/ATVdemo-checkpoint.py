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
from src import Statistics


args = argParser.main([
    "data_folder",
    "TR",
    "run",
    "ex_subs",
    "participant_num_len"
])

# "/data/perlman/moochie/user_data/SchneiderClayton/\
# studyData/ATV_LCBD_copy_120821/data"
dataDir = args.data_folder

episode = args.run

# list of all fnames in dataDir if the first n characters are not bad subjects
# they are full paths joined to data directory
fnames = [join(dataDir, fname) for fname in os.listdir(dataDir)\
    if os.path.basename(fname)[:args.participant_num_len] not in args.ex_subs]

dataset = []

print("Loading ATV files as TimeSeries objects:")
print("==========")
for fpath in tqdm(fnames):
    try:
        # for each filepath in the list, run an ATV.TrialReader builder
        # add each src.TimeSeries object generated from the TrialReader to
        # the dataset list
        for ts in TrialReader(fpath).ratingsSeries:
            dataset.append(ts)
    except:
        print("Failure to read:", os.path.basename(fpath))
        pass

print("Number of viewings in dataset:", len(dataset))

# dataset = [ts for ts in dataset if ts.meta['episode'] == episode]
#
# # also then sort by subject number
# idx = np.argsort([view.participant for view in dataset])
# dataset = [dataset[i] for i in idx]

print("Preprocessing TimeSeries:")
print("==========")
for ts in tqdm(dataset):
    ts.fix_nan()
    ts.lag_correct()
    ts.resample(sample_rate=args.TR)

# truncate each batch of runs with the same episode to the length of the
# shortest trial in the batch
for episode in list(set([ts.meta['episode'] for ts in dataset])):
    ep_min = min([len(ts.signal) for ts in dataset\
        if ts.meta['episode']==episode])
    for ts in [ts for ts in dataset if ts.meta['episode']==episode]:
        ts.signal = ts.signal[:ep_min]
        ts.time = ts.time[:ep_min]

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
# for ts in dataset[:1]:
#     Plots.plot_xy_line(
#         ts.time,
#         ts.signal,
#         xlabel="Time (" + dataset[0].unit + ")",
#         ylabel="Subject " + str(ts.meta['participant']) + " Raw Rating",
#         fig_fname="raw_"+str(ts.meta['participant']))

# for i in range(len(dataset)):
#     Plots.plot_xy_line(
#         dataset[i].time,
#         dataset[i].signal,
#         xlabel="Time (" + dataset[i].unit + ")",
#         title="Subject " + str(dataset[i].meta['participant']) + " Raw Rating")

# for plotting with 'same' padding i.e. time as x-axis instead of TR
# Plots.plot_xy_line(
#     dataset[0].time,
#     mvg_avgs[0],
#     xlabel="Time (" + dataset[0].time_unit + ")",
#     title="Subject " + str(dataset[0].participant) + \
#     ' Moving Average w =' + str(w))

# make an average timecourse for each episode
# episodes = list(set([ts.meta['episode'] for ts in dataset]))
# averages = {}
#
# for episode in episodes:
#     averages[episode] = (
#         np.average(
#             [ts.signal for ts in dataset if ts.meta['episode']==episode],
#             axis=0),
#         next(filter(
#             lambda ts: ts.meta['episode']==episode), dataset, None).time)
#     print("shape of average:", average[episode].shape)
#     print("shape of episode:", dataset[0].signal.shape)
#
#     Plots.plot_xy_line(
#         averages[episode][0],
#         averages[episode][1],
#         xlabel="Time (" + dataset[0].unit + ")",
#         ylabel="Episode " + str(episode) + " Average Raw Rating")


# purge dataset of all except the queried run
purged_dataset = [ts for ts in dataset if ts.meta['episode']==args.run]

np.savetxt(
    "./episode"+str(args.run)+".csv",
    np.array([ts.signal for ts in purged_dataset]),
    delimiter=",")

# print("data shapes:")
# for ts in purged_dataset:
#     print(ts.signal.shape)

# make average of raw ratings
average = np.average(np.array([ts.signal for ts in purged_dataset]), axis=0)

# print("Dataset shape:", np.array([ts.signal for ts in purged_dataset]).shape)

# initialize empty array for icc values (one per timepoint)
iccs = np.array(purged_dataset[0].signal.shape)

# traverse through axis 1 / columns / timeoints
for i, col in enumerate(np.array([ts.signal for ts in purged_dataset]).T):
    # append icc for timepoint to iccs
    iccs[i] = Statistics.icc(
        np.array(col),
        icc_type='ICC(3,k)')

mean_icc = np.mean(iccs)
# icc = Statistics.icc(np.array([ts.signal for ts in purged_dataset]))

# plot average
Plots.plot_xy_line(
    purged_dataset[0].time,
    [average, iccs],
    # average,
    labels=['Mean rating', 'ICC(3, k)'],
    title="Mean Rating: Mean ICC(3, k) = {icc:.2f}".format(icc=mean_icc),
    xlabel="Time (" + purged_dataset[0].unit + ")",
    ylabel="Episode " + str(args.run) + " Average Raw Rating")

Plots.plot_colormesh(
    np.array([ts.signal/2 for ts in purged_dataset]),
    xlabel="Time (" + purged_dataset[0].unit + ")",
    ylabel='Subject',
    yticks=[ts.meta['participant'] for ts in purged_dataset])
