# General dependencies
import os, shutil
from os.path import join
from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np
# import pandas as pd
# import seaborn as sns
# from copy import deepcopy
from glob import glob
from itertools import compress

import mne
import mne_nirs

# LCBD dependencies
# add relative path to our toolbox
# TODO: want path appends to be done in
# venv, so can import modules correctly
# and not using relative paths that may change
# in future releases
import sys
sys.path.append('../../../')
from LCBDtools.src import argParser
from LCBDtools.src import Plots

def create_boxcar(raw, event_id=None, stim_dur=1):
    """
    Generate boxcar representation of the experimental paradigm.

    Parameters
    ----------
    raw : instance of Raw
        Haemoglobin data.
    event_id : as specified in MNE
        Information about events.
    stim_dur : Number
        The length of your stimulus.

    Returns
    -------
    s : array
        Returns an array for each annotation label.
    """
    from scipy import signal

    events, ids = mne.events_from_annotations(
        raw,
        event_id=event_id,
        verbose=False)

    s = np.zeros((len(raw.times), len(ids)))
    for idx, id in enumerate(ids):
        bc = signal.boxcar(round(raw.info['sfreq'] * stim_dur[id]))

        id_idx = [e[2] == idx + 1 for e in events]
        id_evt = events[id_idx]
        event_samples = [e[0] for e in id_evt]
        s[event_samples, idx] = 1.
        s[:, idx] = np.convolve(s[:, idx], bc)[:len(raw.times)]
    return s

# args = argParser.main([
#     # "data_folder",
#     # "run",
#     "participant_num_len",
#     "ex_subs",
#     # "in_subs",
# ])

# Some configuration variables
nirs_dir = "/data/perlman/moochie/analysis/P-CAT/NIRS_data_clean"
PSUnirs_dir = "/data/perlman/moochie/analysis/P-CAT/PSU_NIRS_data_clean"
participant_num_len = 4 # default length of participant numbers
# ex_subs = args.ex_subs # any subjects to not include in the dataset
# in_subs = args.in_subs # limit inclusion to these subjects

# from data tracker June 11th 2022, list of subjects with v3 Flanker completed
in_subs = [
    "1115",
    "1116",
#     "1110", didn't do flanker, less 80% practice
    "1114",
#     "1119", # refused to flank
    "1121",
    "1122",
    "1126",
    "1125",
    "1127",
#     "1128", sibling participated
    "1129",
    "1134",
    "1130",
#     "1131", <20% on practice
#     "1137", lower extreme on KBIT
#     "1124", # took off cap midway through, they did the first couple blocks
    "1133",
#     "1138", <20% on practice
    "1144",
    "1143",
#     "1141", <20% on practice
    "1145",
    "1149",
    "1154",
    "1155",
#     "1142", <20% on practice
    "1148",
    "1156",
    # june 24 updates
    "1159",
    # "1160", failed practice
]

# PSU stuff
PSU_insubs = [
    "1202",
#     "1203", # issue... no flanker data collected
    "1204",
#     "1205", # failed practice
    "1207",
    "1209",
    "1211",
    "1213",
#     "1214", # failed practice
#     "1216", # failed practice
    "1219",
    "1220",
#     "1221", # failed practice
#     "1222", # failed practice
    "1223",
#     "1234", # failed practice
#     "1229", # failed practice
#     "1231", # failed practice
    "1238",
    "1226",
]

for sub in PSU_insubs:
    in_subs.append(sub)

all_subs = [
    "1102",
    "1109",
    "1103",
    "1104",
    "1112",
    "1115",
    "1116",
    "1110",
    "1117",
    "1118",
    "1114",
    "1119",
    "1121",
    "1122",
    "1126",
    "1113",
    "1125",
    "1127",
    "1128",
    "1129",
    "1134",
    "1130",
    "1131",
    "1137",
    "1124",
    "1133",
    "1138",
    "1144",
    "1143",
    "1151",
    "1145",
    "1141",
    "1147",
    "1149",
    "1154",
    "1155",
    "1152",
    "1139",
    "1142",
    "1148",
    "1156",
    "1159",
    "1160"]

# PSU stuff
PSU_subs = [
    "1200",
    "1201",
    "1202",
    "1203",
    "1204",
    "1205",
    "1206",
    "1207",
    "1208",
    "1209",
    "1210",
    "1211",
    "1212",
    "1213",
    "1214",
    "1216",
    "1218",
    "1219",
    "1220",
    "1221",
    "1222",
    "1223",
    "1225",
    "1226",
    "1227",
    "1228",
    "1229",
    "1231",
    "1232",
    "1234",
    "1235",
    "1236",
    "1237",
    "1238",
    "1239"]

for sub in PSU_subs:
    all_subs.append(sub)

ages = [
    6.42026009582478,
    5.1006160164271,
    6.38193018480493,
    4.68993839835729,
    7.97809719370294,
    6.55989048596851,
    7.43326488706366,
    4.8952772073922,
    6.78439425051335,
    5.09787816563997,
    4.58316221765914,
    4.51471594798084,
    7.87953456536619,
    5.37987679671458,
    7.97535934291581,
    4.03285420944559,
    7.71252566735113,
    7.81656399726215,
    0,
    7.45516769336071,
    5.86173853524983,
    6.6009582477755,
    4.3750855578371,
    4.07939767282683,
    6.13826146475017,
    4.35318275154004,
    5.13894592744695,
    5.7056810403833,
    7.42778918548939,
    4.51745379876797,
    6.40930869267625,
    4.03011635865845,
    6.01779603011636,
    7.67693360711841,
    6.94318959616701,
    4.35592060232717,
    0,
    0,
    4.03832991101985,
    5.93018480492813,
    5.36344969199179,
    4.25462012303290,
    0]

# PSU stuff
PSU_ages = [
    5.88364134154689,
    0.0,
    5.71663244353183,
    5.84804928131417,
    5.91375770020534,
    6.37645448323066,
    0.0,
    6.08624229979466,
    0.0,
    5.30047912388775,
    0.0,
    4.18617385352498,
    0.0,
    4.85694729637235,
    4.42710472279261,
    0.0,
    0.0,
    6.92676249144422,
    6.34086242299795,
    4.99657768651609,
    4.50376454483231,
    5.68377823408624,
    0.0,
    0.0,
    0.0,
    0.0,
    4.20807665982204,
    4.99383983572895,
    0.0,
    4.34496919917865,
    0.0,
    0.0,
    0.0,
    6.48596851471595,
    0.0]

for age in PSU_ages:
    ages.append(age)

session_dirs = [d for d in glob(nirs_dir+"/*/*Flanker") if \
    os.path.basename(d)[:participant_num_len] in in_subs]

PSUsession_dirs = [d for d in glob(PSUnirs_dir+"/*/*Flanker") if \
    os.path.basename(d)[:participant_num_len] in in_subs]

subjects = list(set([os.path.basename(d)[:participant_num_len] for d in session_dirs]))

# mne.viz.set_3d_backend('pyvista')
raw_intensities = []

for ses in session_dirs:

#     if os.path.basename(ses)[:participant_num_len] == "50600":
#         pass
#     else:
#         continue

#     evts = glob(ses + "/*.evt")
#     if len(evts) != 2:
#         print("There should be 2 evt files. Skipping:", os.path.basename(ses))
#         continue
    try:
        raw_intensities.append(mne.io.read_raw_nirx(ses).load_data())
    except:
        print("Failure to load:", ses, "skipping.")
#     raw_intensities[-1].resample(0.7) # downsample to 0.7 HZ to run faster

#     # replace raw_ints annotations with events from custom file.
#     # read events from file
#     events, event_dict = mne.read_events(join(ses, "new_eve.txt"))
#     annot_from_events = mne.annotations_from_events(
#         events=events,
#         event_desc=event_dict,
#         sfreq=raw_intensities[-1].info['sfreq'],
#         orig_time=raw_intensities[-1].info['meas_date'])

#     raw_intensities[-1].set_annotations(annot_from_events)

# PSU data
for ses in PSUsession_dirs:

    try:
        raw_intensities.append(mne.io.read_raw_nirx(ses).load_data())
    except:
        print("Failure to load:", ses, "skipping.")

for raw in raw_intensities:

    raw_od = mne.preprocessing.nirs.optical_density(raw)

    # sci = mne.preprocessing.nirs.scalp_coupling_index(raw_od)

    # raw_od.info['bads'] = list(compress(raw_od.ch_names, sci < 0.5))

    tddr_od = mne.preprocessing.nirs.tddr(raw_od)

    haemo = mne.preprocessing.nirs.beer_lambert_law(tddr_od, ppf=0.1)

    haemo.plot(
        duration=raw.times[-1],
        title=raw.info['subject_info']['his_id'][:participant_num_len],
        block=True,
        clipping=None)
