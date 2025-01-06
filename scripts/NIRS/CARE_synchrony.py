#general dependencies (importing premade packages/libraries)
import mne, random, os, json, sys, io, requests, shutil, hrc
import numpy as np
import pandas as pd
import pycwt as wavelet
import matplotlib.pyplot as plt
from datetime import datetime
from typing import Union
from os.path import join
from glob import glob
from itertools import compress
from tqdm import tqdm
from pycwt.helpers import find
from copy import copy
from collections import OrderedDict
from mpl_toolkits.mplot3d import Axes3D
from platform import python_version
python_version()

convolver = hrc.convolver()

sys.path.append('/storage1/fs1/perlmansusan/Active/moochie/github/')
from LCBDtools.src import argParser
from LCBDtools.src import Plots

# parameters
nirs_dir = "/storage1/fs1/perlmansusan/Active/moochie/analysis/CARE/NIRS_data_clean_2/"
psypy_dir = "/storage1/fs1/perlmansusan/Active/moochie/study_data/CARE/task_data/DB_DOS/"
ex_subs = ['52491c']
participant_num_len = 5
sample_rate = 7.81250
n_blocks = 3

nirs_session_dirs = [os.path.split(d)[0] for d in glob(
    nirs_dir+"**/*_probeInfo.mat",
    recursive=True) \
    if d.strip(nirs_dir).strip("/")[:participant_num_len] not in ex_subs and \
        "V" in (os.path.basename(os.path.dirname(os.path.dirname(d))))]

def timeconvert_psychopy_to_nirstar(
    sample_rate,
    NSstim1_t,
    PSstim1_t,
    PSevent_t):
    
    NSevent_t = NSstim1_t + (PSevent_t - PSstim1_t) * sample_rate
    return NSevent_t


for ses in tqdm(nirs_session_dirs):
    # should always work, even with multiple-runs. 
    # TODO remember that these exist, where 2 runs are collected
    # for the same dyad of parent/child, for unknown reason. 
    # potentially check for truncated run while parsing this data in other
    # mne processing software
    
#     if ("50170_V0_fNIRS" in ses) or ("50171_V0_fNIRS" in ses):
#         pass
#     else:
#         continue
    
    # only do this if there's only 1 .evt file in study folder
    og_evt = glob(ses+"/*.evt")
    if len(og_evt) != 1:
        print("Error: found", len(og_evt), "evt files for the given sub / visit.")
        print("Skipping:", ses)
        continue
    else:
        og_evt = og_evt[0]
    
    # open original evt
    print(og_evt)
    f = open(og_evt, 'r')
    line1 = f.readline()
    print(line1)
    f.close()
    
    # first time marker is NIRS stim start 1
    NSstim1_t = line1.split('\t')[0]
    
    if NSstim1_t == '':
        print('Empty event file, skipping...')
        continue
    
#     print(ses)
    child_sub = ses.strip(nirs_dir).strip("/")[:participant_num_len]
#     print(child_sub)
    visit_ID = ses.strip(nirs_dir).strip("/")[participant_num_len+1:participant_num_len+3]
#     print(visit_ID)
    # looks like it's working!
    
    task_file = glob(join(psypy_dir, child_sub, visit_ID)+ "/*.csv")
    
    # only continue if we have exactly 1 task file found
    if len(task_file) != 1:
        print("Error: found", len(task_file), "task files for the given sub / visit.")
        continue
    else:
        task_file = task_file[0]
      
    # df of psychopy csv output
    df = pd.read_csv(task_file)
    
    stims = []
    
    # iterate through any column that has "countdown" and ".started"
    block_i = 0
    for col in df.columns:
        
        # if we're dealing with a legitimate block column
        if ("intro_txt" in col) and (".stopped" in col):

            # then also generate the name of the corresponding stop column
            block_name_str = col.strip("intro_txt").strip(".stopped")
            
            stopcol = "timeup_txt"+block_name_str+".started"
            
            # store any non-NaN vals in the start and stop column (times)
            starts = (df[~df[col].isnull()][col].astype(float) + 5).tolist()
            stops = (df[~df[stopcol].isnull()][stopcol].astype(float)).tolist()
            
            if len(starts) != len(stops):
                print("Unequal number of starts and stops. ses:", ses, "block_i", block_i)
                continue
            
            # if there are no starts already entered / outlines has length 1,
            # then we know that the first start in our starts is the same as line1 trigger. 
            # meaning that is the reference point to which the time course of the psychopy
            # file and the NIRS file will be aligned, again using the sample rate
            # or, easily, if block_i == 1.
            
            # append to stims with tuples of (time, evt_stim_col)
            for i in range(len(starts)):
                stims.append((starts[i], block_i))
                stims.append((stops[i], 7))
            
            # if we're in the first block, we know psychopy stim 1 now
            if block_i == 0:
                PSstim1_t = starts[0]
                stims.pop(0)
            
            # convert using first NIRS stim and first Psychopy stim to align
            converted_stims = []
            
            for (time, val) in stims:
                converted_stims.append((
                    timeconvert_psychopy_to_nirstar(
                        float(sample_rate),
                        float(NSstim1_t),
                        float(PSstim1_t),
                        float(time)),
                    val))
            
            block_i += 1
        
        # if we're not dealing with a legitimate column, we can just keep iterating
        else:
            continue

    output_lines = [line1]
    
    for (stim_time, stim_col) in converted_stims:
        # make bit format stims
        evts = [0]*8
        evts[stim_col]=1
        
        # and write these as lines in correct format for .evt
        line = str(round(stim_time))
        for evt_col in evts:
            line += "\t"
            line += str(evt_col)
        line += "\n"
            
        output_lines.append(line)
    
    # move OG evt to _old.evt
    shutil.move(
        og_evt,
        og_evt.replace(".evt", "_old.evt"))
    
    # write the lines as the new, properly named .evt
    f = open(join(ses, og_evt), 'w')
    
    for line in output_lines:
        f.write(line)
    
    f.close()

# Some configuration variables
study_dir = "/storage1/fs1/perlmansusan/Active/moochie/analysis/CARE/NIRS_data_clean_2/"
participant_num_len = 5 # default length of participant numbers
ex_subs = [] # any subjects to not include in the dataset
debug = True

# set block durations (original data has start and stop data points, those stop data points are eventually removed to replace with durations instead, they are easier to work with)
durations = {
    'Block 1': 120,
    'Block 2': 105,
    'Block 3': 120}

    # set the channels for each ROI
ROIs = {
    'Left Dorsolateral Prefrontal': ['S3_D2 hbo', 'S4_D2 hbo'],
    'Right Dorsolateral Prefrontal': ['S5_D3 hbo', 'S6_D3 hbo'],
    'Left Ventrolateral Prefrontal': ['S1_D1 hbo', 'S2_D1 hbo', 'S2_D2 hbo'],
    'Right Ventrolateral Prefrontal': ['S7_D3 hbo', 'S7_D4 hbo', 'S8_D4 hbo']}

# make a list of all matching session paths (in this case for V0, assuming there should be more sessions?)
session_dirs = [d for d in glob(study_dir+"/*/V0/*") \
    if os.path.basename(os.path.split(os.path.split(d)[1])[1]) not in ex_subs]

subjects = list(set([os.path.basename(d)[:participant_num_len] for d in session_dirs]))

print(f"Subject Directory Count - {len(session_dirs)}")

# make a list where all of the scans will get loaded into (for children and for parent)
scans = []

# loop over all the session directories (dyads / DB-DOS folders)
for dyad_dir in list(set([os.path.split(ses)[0] for ses in session_dirs])):
    try:
        
        # get subject and visit from this path
        sub = os.path.basename(os.path.dirname(dyad_dir))
        visit = os.path.basename(dyad_dir)
        
        if debug:
            print(f'{sub} - {visit}')
        
        # determining whether sub is Child or Parent can be done by reading the config file in the .nirx directory        
        config_files = glob(os.path.join(dyad_dir, "*fNIRS", "*config*"))

        # open the file and read the line with Subject= in it
        for config in config_files:
            with open(config, 'r') as f:
                line = f.readline()
                while "Subject=" not in line:
                    line = f.readline()
                line = line.strip()
                line = line.replace("Subject=", "")
                
                # if the line is 1 it's the child
                if line == "1":
                    sub1 = os.path.dirname(config) # child
                elif line == "2":
                    sub2 = os.path.dirname(config) # parent
                    
        # make sure it has 'modern' .evt files
        evts = glob(sub1 + "/*.evt")
        if len(evts) != 2:
            print("There should be 2 evt files. Skipping:", os.path.basename(sub1))
            continue

#         #**load each in via hypyp loader (fixing config file so that even if child and parent numbers were flipped, they will now each be labelled as c or p in object)**
        fnirs_participant_1 = mne.io.read_raw_nirx(sub1, preload=False, verbose="warning") # child
        fnirs_participant_1.info['subject_info']['his_id'] = f"{sub[:participant_num_len]}c"
        
        fnirs_participant_2 = mne.io.read_raw_nirx(sub2, preload=False, verbose="warning") # parent
        fnirs_participant_2.info['subject_info']['his_id'] = f"{sub[:participant_num_len]}p"
        
        scans.append((fnirs_participant_1, fnirs_participant_2))
    
    #when there aren't 2 evt files    
    except:
        print("skipping session:", dyad_dir)
        continue

#raw NIRS data for child and parent now loaded into "scans" object

print(f"Number of scans before processing- {len(scans)}")

# if we can't load in the annotations right, we'll remove them from our list of scans
bads = []

for i, dscan in enumerate(scans):
    
#    try:
    for scan in dscan:
        print(scan.annotations)
        # rename the binary annotations with actual names
        for key, desc in {'1.0': 'Block 1', '2.0': 'Block 2', '4.0': 'Block 3'}.items():
            try:
                scan.annotations.rename({key :desc})
            except:
                print("Annotation not found")

        # remove any stop annotations
        scan.annotations.delete(scan.annotations.description == '128.0')
        print("Successfully deleted")

        # set the durations based off the durations dictionary
        for key, desc in durations.items():
            try:
                scan.annotations.set_durations(key, desc, verbose=True)
            except:
                print("Annotation not found")
        
        print("Successfully reset annotation duration")
    
#    except:
#        print(f"Failed {scan}\n{scan.annotations}")
#        bads.append(i)

print(f"Length of Bads - {len(bads)}")
        
for i in sorted(bads, reverse=True):
    del scans[i]

# function to do Continuous Wavelet Transform on a single signal
#Sig1: raw MNE converted signal or Epoch; plot = set whether you want to plot the wavelet (True or False); chs: produce a wavelet for a specific channel
def mne_wavelet_transform(sig1: [mne.io.Raw, mne.Epochs], plot: bool = True,
                      chs: Union[str] = None):
    """
    Perform a continuous wavelet transform based off data in mne Raw object
    """
    
    #Fourier Transform "transforms" data from time to frequency domain (certain number of oscillations per second)
    #The the final wavelet transform is an intermediate between time and frequency domain, it just needs to be transformed to frquency first
    # set time ##t0 = start time and dt = distance in time from t0. N is length
    t0 = sig1.times[0]
    dt = sig1.times[1] - t0
    N = len(sig1.times)
    #t = np.arange(0, N) * dt + t0
    t = sig1.times
    
    # define wavelet analysis parameters ## Clayton Add reference for parameters? (By default uses a Morlet convolution function to align detected signal with
    # with this base function) 
    #Video on Morlet wavelets
    mother = wavelet.Morlet(6)
    s0 = 2 * dt # starting scale, in this case 2 * 0.128 s = 0.256 s
    dj = 1 / 12 # twelve sub-octaves per octaves
    J = 10 / dj # ten powers of 2 with dj sub-octaves
    
    if chs is None:
        chs = sig1.info['ch_names']
        
    #reshaping of signal
    for ch in chs:
        dat = np.squeeze(sig1.get_data(picks=[ch])) * 1e5
        
        # detrend and normalize the input data by its standard deviation (to remove drift effects)
        p = np.polyfit(t - t0, dat, 1)
        dat_notrend = dat - np.polyval(p, t - t0)
        std = dat_notrend.std() # standard deviation
        var = std ** 2 # variance
        dat_norm = dat_notrend / std # normalized dataset
        
        alpha, _, _ = wavelet.ar1(dat) # lag-1 autocorrelation for red noise
        
        #This is the actual function where dat_norm, dt etc. are entered to produce the wavelet tranformed matrix, weighted scales for each matrix, list of frequencies
        # coming from each matrix, the cone of influence (gives a prospective range in which signal should closely convolve with Morlet),
        #fast fourier transform? (fft)
        wave, scales, freqs, coi, fft, fftfreqs = wavelet.cwt(
            dat_norm, dt, dj, s0, J, mother)
        iwave = wavelet.icwt(wave, scales, dt, dj, mother) * std
    
        # plotting the fourier tranform
        power = (np.abs(wave)) ** 2
        fft_power = np.abs(fft) ** 2
        period = 1 / freqs
        power /= scales[:, None] # optional according to Liu et al. (2007)
        
        # power significance test (the degree of convergence of the signal and the Morlet function? Also compare frequencies in one epoch vs the other?)
        signif, fft_theor = wavelet.significance(
            1.0, dt, scales, 0, alpha,
            significance_level=0.95, 
            wavelet=mother)
        sig95 = np.ones([1, N]) * signif[:, None]
        sig95 = power / sig95
        
        # calculate global wavelet spectrum and determine its significance level
        glbl_power = power.mean(axis=1)
        dof = N - scales # correction for padding at edges
        glbl_signif, tmp = wavelet.significance(var, dt, scales, 1, alpha,
                                                significance_level=0.95, dof=dof,
                                                wavelet=mother)
        
        # calculate scale average and its significance level
        sel = find((period >= 10) & (period < 50))
        Cdelta = mother.cdelta
        scale_avg = (scales * np.ones((N, 1))).transpose()
        scale_avg = power / scale_avg # As in Torrence and Compo (1998) equation 24
        scale_avg = var * dj * dt / Cdelta * scale_avg[sel, :].sum(axis=0)
        scale_avg_signif, tmp = wavelet.significance(var, dt, scales, 2, alpha,
                                                    significance_level=0.95,
                                                    dof=[scales[sel[0]],
                                                        scales[sel[-1]]],
                                                    wavelet=mother)
        
        if plot is True:
            
            title = f"{sig1.info['subject_info']['his_id']} Channel {ch} Continuous Wavelet Transform"
            label = ""
            units = 'Absorbance Units (AU)'
            
            # prepare the figure
            plt.close('all')
            plt.ioff()
            figprops = dict(figsize=(11, 8), dpi=72)
            fig = plt.figure(**figprops)
            
            # first sub-plot, the original time series
            ax = plt.axes([0.1, 0.75, 0.65, 0.2])
            ax.plot(t, dat, 'k', linewidth=1.5)
            ax.set_title('a) {}'.format(title))
            ax.set_ylabel(r'{} [{}]'.format(label, units))
            
            # second sub-plot, the normalized wavelet power spectrum and significance
            # level contour lines and cone of influence hatched area. Note that period
            # scale is logarithmic
            bx = plt.axes([0.1, 0.37, 0.65, 0.28], sharex=ax)
            levels = [0.0625, 0.125, 0.25, 0.5, 1, 2, 4, 8, 16]
            conmap = bx.contourf(t, np.log2(period), np.log2(power), np.log2(levels), 
                        extend='both', cmap=plt.cm.jet)
#             plt.colorbar(conmap)
            extent = [t.min(), t.max(), 0, max(period)]
            bx.contour(t, np.log2(period), sig95, [-99, 1], colors='k', linewidths=2,
                                  extent=extent)
            bx.fill(np.concatenate([t, t[-1:] + dt, t[-1:] + dt,
                                   t[:1] - dt, t[:1] - dt]),
                    np.concatenate([np.log2(coi), [1e-9], np.log2(period[-1:]),
                                    np.log2(period[-1:]), [1e-9]]),
                    'k', alpha=0.3, hatch='x')
            bx.set_title('b) {} Wavelet Power Spectrum ({})'.format(label, mother.name))
            bx.set_ylabel('Frequency (Hz)')
            
            Yticks = 2 ** np.arange(np.ceil(np.log2(period.min())),
                                    np.ceil(np.log2(period.max())))
            
            bx.set_yticks(np.log2(Yticks))
            bx.set_yticklabels(1/Yticks)
            
            # third sub-plot, the global wavelet and Fourier power spectra and theoretical
            # noise spectra. Note that period scale is logarithmic
            cx = plt.axes([0.77, 0.37, 0.2, 0.28], sharey=bx)
            cx.plot(glbl_signif, np.log2(period), 'k--')
            cx.plot(var * fft_theor, np.log2(period), '--', color='#cccccc')
            cx.plot(var * fft_power, np.log2(1./fftfreqs), '-', color='#cccccc',
                    linewidth=1.)
            cx.plot(var * glbl_power, np.log2(period), 'k-', linewidth=1.5)
            cx.set_title('c) Global Wavelet Spectrum')
            cx.set_xlabel(r'Power [({})^2]'.format(units))
            cx.set_xlim([0, glbl_power.max() + var])
            cx.set_ylim(np.log2([period.min(), period.max()]))
            cx.set_yticks(np.log2(Yticks))
            cx.set_yticklabels(1/Yticks)
            plt.setp(cx.get_yticklabels(), visible=False)
            
            # Fourth sub-plot, the scale averaged wavelet spectrum.
            dx = plt.axes([0.1, 0.07, 0.65, 0.2], sharex=ax)
            dx.axhline(scale_avg_signif, color='k', linestyle='--', linewidth=1.)
            dx.plot(t, scale_avg, 'k-', linewidth=1.5)
            dx.set_title('d) {}--{} second scale-averaged power'.format(2, 8))
            dx.set_xlabel('Time (seconds)')
            dx.set_ylabel(r'Average variance [{}]'.format(units))
            ax.set_xlim([t.min(), t.max()])

            plt.show()
    
    return wave, scales, freqs, coi, fft, fftfreqs


# function to do wavelet coherence transform on 2 signals
def mne_wavelet_coherence_transform(sig1: [mne.io.Raw, mne.Epochs],
        sig2: [mne.io.Raw, mne.Epochs],
        plot: bool = True, fig_fname: str = None,
        chs: Union[str] = None):
    
    t0 = sig1.times[0]
    dt = sig1.times[1] - t0
    N = len(sig1.times)
#     t = np.arange(0, N) * dt + t0
    t = sig1.times
    
    # define wavelet analysis parameters
    mother = wavelet.Morlet(6)
    s0 = 2 * dt # starting scale, in this case 2 * 0.128 s = 0.256 s
    dj = 1 / 12 # twelve sub-octaves per octaves
    J = 10 / dj # ten powers of 2 with dj sub-octaves
    
    if chs is None:
        chs = sig1.info['ch_names']
        
    for ch in chs:
        dat1 = np.squeeze(sig1.get_data(picks=[ch]))
        dat2 = np.squeeze(sig2.get_data(picks=[ch]))
        
        if np.isnan(dat1).any():
            print("Dat 1 contains NaN values")
            raise ValueError
            
        if np.isnan(dat2).any():
            print("Dat 2 contains NaN values")
            raise ValueError
        
        # detrend and normalize the input data by its standard deviation
        p1 = np.polyfit(t - t0, dat1, 1)
        dat_notrend1 = dat1 - np.polyval(p1, t - t0)
        std1 = dat_notrend1.std() # standard deviation
        var1 = std1 ** 2 # variance
        dat_norm1 = dat_notrend1 / std1 # normalized dataset
        
        # detrend and normalize the input data by its standard deviation
        p2 = np.polyfit(t - t0, dat2, 1)
        dat_notrend2 = dat2 - np.polyval(p2, t - t0)
        std2 = dat_notrend2.std() # standard deviation
        var2 = std2 ** 2 # variance
        dat_norm2 = dat_notrend2 / std2 # normalized dataset
        
        WCT, aWCT, coi, freqs, sig95 = wavelet.wct(
            dat_norm1, dat_norm2,
            dt, dj=dj, s0=s0, J=J, sig=False,
            significance_level=0.95, wavelet='morlet',
            normalize=True)
        
        period = 1 / freqs
        
        if plot is True:
            
            title = f"{sig1.info['subject_info']['his_id']} / {sig2.info['subject_info']['his_id']} Channel {ch} Wavelet Coherence Transform"
            label = f"{sig1.info['subject_info']['his_id']} {sig2.info['subject_info']['his_id']} {ch}"
            units = 'Absorbance Units (AU)'
            
            # prepare the figure
            plt.close('all')
            plt.ioff()
            figprops = dict(figsize=(11, 8), dpi=72)
            fig = plt.figure(**figprops)
            
            # first sub-plot, the normalized wavelet power spectrum and significance
            # level contour lines and cone of influence hatched area. Note that period
            # scale is logarithmic
            ax = plt.axes([0.1, 0.37, 0.65, 0.28])
#             levels = [0.0625, 0.125, 0.25, 0.5, 1, 2, 4, 8, 16]
            levels = list(np.arange(0.1, 1, step=0.1))
            conmap = ax.contourf(t, np.log2(period), WCT, levels, 
                        extend='both', cmap=plt.cm.jet)
            plt.colorbar(conmap)
            extent = [t.min(), t.max(), 0, max(period)]
#             ax.contour(t, np.log2(period), sig95, [-99, 1], colors='k', linewidths=2,
#                                   extent=extent)
            ax.fill(np.concatenate([t, t[-1:] + dt, t[-1:] + dt,
                                   t[:1] - dt, t[:1] - dt]),
                    np.concatenate([np.log2(coi), [1e-9], np.log2(period[-1:]),
                                    np.log2(period[-1:]), [1e-9]]),
                    'k', alpha=0.3, hatch='x')
            ax.set_title('b) {} Wavelet Coherence Spectrum ({})'.format(label, mother.name))
            ax.set_ylabel('Frequency (Hz)')
            
            Yticks = 2 ** np.arange(np.ceil(np.log2(period.min())),
                                    np.ceil(np.log2(period.max())))
            
            ax.set_yticks(np.log2(Yticks))
            ax.set_yticklabels(1/Yticks)
            ax.set_xlim([t.min(), t.max()])
            ax.set_ylim(np.log2([period.min(), period.max()]))
            
            if fig_fname is None:
                plt.show()
            else:
                plt.savefig(fig_fname)
            
    return WCT, aWCT, coi, freqs, sig95 


#Here the signals collected from the various channels are converted to relaative hemoglobin concentration instead of a frequency waveform,
#which is what we were working with above before preprocessing

# make a list where the preprocessed scans will go
print(f"Length of scans - {len(scans)}")
pps = []

# for each dyad scan in scans
for dscan in scans:

    ppdscan = [] # make a list for the preprocessed dyad's scans
    
    # individually preprocess each subject in dyad
    for scan in dscan:
        
        # convert to optical density
        raw_od = mne.preprocessing.nirs.optical_density(scan)

        # scalp coupling index
        sci = mne.preprocessing.nirs.scalp_coupling_index(raw_od)
        raw_od.info['bads'] = list(compress(raw_od.ch_names, sci < 0.5))
        
        # linear detrend, par example
#         raw.data[:] = scipy.signal.detrend(raw.get_data(), axis=-1, fit='linear')

        if len(raw_od.info['bads']) > 0:
            print("Bad channels in subject", raw_od.info['subject_info']['his_id'], ":", raw_od.info['bads'])
        
        # temporal derivative distribution repair (motion attempt)
        tddr_od = mne.preprocessing.nirs.tddr(raw_od)
#         print("tddr")
#         tddr_od.plot(
#             n_channels=len(tddr_od.ch_names),
#             scalings=0.1,
#             duration=100,
#             show_scrollbars=False)
        
        # savgol filter (linear polynomial smoothing)
#         sav_od = raw_od.savgol_filter(0.5)
#         print("savgol filtering")
#         sav_od.plot(
#             n_channels=len(sav_od.ch_names),
#             scalings=0.1,
#             duration=100,
#             show_scrollbars=False)

        bp_od = tddr_od.filter(0.01, 0.5)
#         print("bandpass")
#         bp_od.plot(
#             n_channels=len(bp_od.ch_names),
#             duration=100,
#             scalings=0.1,
#             show_scrollbars=False)
    
        # haemoglobin conversion using Beer Lambert Law (this will change channel names from frequency to hemo or deoxy hemo labelling)
        haemo = mne.preprocessing.nirs.beer_lambert_law(bp_od, ppf=0.1)
#         print("haemo")
#         haemo.plot(
#             n_channels=len(haemo.ch_names),
#             duration=100,
#             scalings=0.0001,
#             show_scrollbars=False)

#         print("PSD")
#         haemo_lp.plot_psd(average=True)
        
        # Convolve the scan
        convolved_nirx = convolver.convolve_hrf(haemo)
        

    ppdscan.append(haemo)
        
    pps.append(ppdscan)


print(f"Length of PPS - {len(pps)}")
#Creating a dictionary variable to store bad channels for later
bad_channels_dict = {}

for dscan in pps:
    for scan in dscan:
        bad_channels_dict[scan.info['subject_info']['his_id']] = scan.info['bads']
        


# make a dictionary where all of the epoch'd data will go
epoch_df = {}
dropped = []
usable = []
# loop over the dyads in the preprocessed list
for dscan in pps:
    
    # February 9th 2023
    # Clayton update to prune subjects who have
    # >= 10 channels dropped from the SCI function during preprocessing
    max_bad = max([len(scan.info['bads']) for scan in dscan])
    # whichever number is higher ^, num. of channels dropped in
    # either parent or child
    
    if max_bad >= 10:
        for scan in dscan:
            sub_num = scan.info['subject_info']['his_id']
            print(f"Subject {sub_num} was dropped from further analysis.")
            dropped.append(scan.info['subject_info']['his_id'])
        continue # skip this dyad
        # if max_bad is greater than or equal to 10
    
    # for each scan in the dyad
    for scan in dscan:
        sub_num = scan.info['subject_info']['his_id']
        # set their location in the epoch df to a dictionary
        epoch_df[scan.info['subject_info']['his_id']] = {}
    
#        for i, ROI in enumerate(ROIs.keys()):

        # loop over ROIs (channels here)
        for i, ROI in enumerate([ch for ch in scan.info['ch_names'] if "hbo" in ch]):
            
            epoch_df[scan.info['subject_info']['his_id']][ROI] = []
        
            # get their events and set block durations
            events, event_dict = mne.events_from_annotations(dscan[0], verbose=False)
            reject_criteria = dict(hbo=200e-6)
            tmin, puzzletmax, playtmax = -5, 105, 120

            if len(list(event_dict.keys())) < 3:
                if sub_num not in usable:
                    usable.append(sub_num)
                continue
            
            # use the mne.Epochs function / object to generate epochs
            preplay_epochs = mne.Epochs(
                scan, # the scan object
                events, # its events
#                 picks=ROIs[ROI],
                picks=[ROI], # the channels
                event_id={list(event_dict.keys())[0]: list(event_dict.values())[0]}, # the first event key
                tmin=tmin, # epoch relative start time
                tmax=playtmax, # epoch relative end time
                baseline= (None, 0), # baseline window to subtract
#                 reject=reject_criteria,
                reject_by_annotation=True,
                detrend=1, # linear detrend
                verbose=False, 
                preload=False, # don't actually load it yet (saves memory)
                event_repeated='merge')
            
            epoch_df[scan.info['subject_info']['his_id']][ROI].append(preplay_epochs)
            
            puzzle_epochs = mne.Epochs(
                scan,
                events,
#                 picks=ROIs[ROI],
                picks=[ROI],
                event_id={list(event_dict.keys())[1]: list(event_dict.values())[1]},
                tmin=tmin,
                tmax=puzzletmax,
                baseline= (None, 0),
#                 reject=reject_criteria,
                reject_by_annotation=True,
                detrend=1,
                verbose=False,
                preload=False,
                event_repeated='merge')
            
            epoch_df[scan.info['subject_info']['his_id']][ROI].append(puzzle_epochs)
            
            postplay_epochs = mne.Epochs(
                scan,
                events,
#                 picks=ROIs[ROI],
                picks=[ROI],
                event_id={list(event_dict.keys())[2]: list(event_dict.values())[2]},
                tmin=tmin,
                tmax=playtmax,
                baseline=(None, 0),
#                 reject=reject_criteria,
                reject_by_annotation=True,
                detrend=1,
                verbose=False,
                preload=False,
                event_repeated='merge')
            
            epoch_df[scan.info['subject_info']['his_id']][ROI].append(postplay_epochs)
            if sub_num not in usable:
                usable.append(sub_num)

#Will tell you how many dyads are retaining for further analyses (not sure if we need this for the current CARE script)
print([sub for sub in epoch_df.keys()])
print(f"Dropped - {dropped}")
print(f"Dyads Including in Synchrony Preprocessing - {len([sub for sub in epoch_df.keys() if "c" in sub])}")

print(f"\n\nUsable Subjects\n {'\n'.join(usable)}")

print(f'\nUsable Dyads\n{'\n'.join([subject for subject in usable if 'c' in subject])}')

# make a new dictionary where the synchrony values will be stored
sync_df = {}
block_types = ['Block 1', 'Block 2', 'Block 3']
perm_df = {}

# THIS TAKES A REALLY LONG TIME TO COMPUTE. AROUND 14 HOURS ON A DECENT NETWORK
# SKIP DOWN TO USE THE SAVED VERSIONS!

#real vs single false dyad test of a myriad of real and fake dyad pairs

print("Starting Synchrony ")
# for every parent subject
for parent in tqdm([sub for sub in sorted(epoch_df.keys()) if "p" in sub]):
    print(parent)

    sync_df[parent] = {}
    perm_df[parent] = []
    
    # pick two children, one real and one random
    children = []
    
#     children.append(parent.replace("p", "c")) # real child
    
    # random sample of N children
    # could be repeated, could be the real dyad 
    randoms = random.choices(
        [sub for sub in epoch_df.keys() if "c" in sub],
        k=999) # N of random 
    # randoms = list(randoms).insert(0, parent.replace("p", "c"))
    perm_df[parent] = list(randoms)
    
    # only going to do synchrony once per kid
    # we can count # of repeats from perm_df[parent]
    for child in list(set(randoms)):
        children.append(child)
    
    # old version that just does 1 random non-real child per parent
#     children.append(
#         random.choice([sub for sub in epoch_df.keys() if "c" in sub \
#             and parent.replace("p", "") not in sub])) # random pick
    
    # loop over these 2 selected children (1 real, N random)
    for child in children:
        
        # and make them a location in the sync dictionary under this parent
        sync_df[parent][child] = {}
        
        # for every block type (pre-play, puzzle, post-play)
        for block_num, block in enumerate(block_types):
            
            # make this parent/child combo a location for this block type, also a dictionary
            sync_df[parent][child][block] = {}
                
            # for each channel available with this subject (not dropped)
            for ch in epoch_df[parent].keys():
                
                # our sync value is going to go here
                # sync_df[parent][child][block][ch]
                # i.e. averaging over the 4 block iterations
                
                # so start keeping track of values to average now
                pc_wcts = []
                
                # load in their epoched data for this subject / channel / block
                print(epoch_df[parent][ch])
                print(block_num)
                if block_num < len(epoch_df[parent][ch]):
                    p_epoch = epoch_df[parent][ch][block_num].load_data()
                else:
                    print(f"Skipping {parent} {block_num} {ch}")
                if block_num < len(epoch_df[child][ch]):
                    c_epoch = epoch_df[child][ch][block_num].load_data()
                else:
                    print(f"Skipping {child} {block_num} {ch}")
                
                # for each iteration of this block (max 4)
                for block_it in np.arange(0, np.min([
                    len(p_epoch),
                    len(c_epoch)])):
                    
                    print(ch)
                    # try to do the WCT with these epochs
                    try:
                        WCT, aWCT, coi, freqs, sig95 = mne_wavelet_coherence_transform(
                            p_epoch[block_it],
                            c_epoch[block_it],
                            plot=True if "S5_D3 hbo" in ch else False, # save plots but only for some random channel because otherwise it's an insane amount
                            fig_fname=f"/storage1/fs1/perlmansusan/Active/moochie/analysis/CARE/sync_figs/{parent}_{child}_{ch.replace(' ', '_')}_{block_num}_{block_it}.png")

                        # make values outside COI = np.nan
                        nanWCT = WCT
                        for t in range(nanWCT.shape[1]):
                            nanWCT[np.where(freqs>coi[t]), t] = np.nan
                        # also set to nan outside frequencies of interest
                        
                        # TASK RELATED FREQUENCIES ARE ARBITRARILY DETERMINED here
                        WCT[(5>(1/freqs))|((1/freqs)>105), :] = np.nan
                        
                        # between periods of 5s and 105s (.0095 -.2 Hz; flip for sec) which is based on Ngyuen et al. 2021
                        

                        # average inside cone of influence
                        # and within values from freq range determined above
                        pc_wcts.append(np.nanmean(nanWCT))
#                     print(np.nanmean(nanWCT))
    
                    # if anything with the WCT fails, say so
                    except:
                        print(f"Fail @ parent {parent}, child {child}, block {block}, channel {ch}, block it {block_it}")
#                 print(np.average(pc_wcts))  
                sync_df[parent][child][block][ch] = np.average(pc_wcts)

# skip if you're going to load the already-saved ones. for real. don't overwrite this with an empty data file. 
# SAVE SYNCHRONY VALUES

channels = epoch_df[parent].keys()
cols = ["Parent", "Child", "Block"]
for ch in channels:
    cols.append(ch)
    
df = pd.DataFrame(columns=cols)    

for parent in sync_df.keys():
    
    for child in sync_df[parent].keys():
        
        for block in sync_df[parent][child].keys():
            
            dic = {
                'Parent': parent,
                'Child': child,
                'Block': block}
            
            for key, val in sync_df[parent][child][block].items():
                dic[key] = val
            
            dic = {k: [v] for k, v in dic.items()}
            df = pd.concat([df, pd.DataFrame(dic, columns=cols)], ignore_index=True)

        
df.to_csv("/storage1/fs1/perlmansusan/Active/moochie/analysis/CARE/Test_Analysis/wct_full_ses-0_permuted_values_pipeline_conv.csv")


json_object = json.dumps(perm_df, indent=4)
with open("/storage1/fs1/perlmansusan/Active/moochie/analysis/CARE/Test_Analysis/permuted_subjects_ses-0_pipeline_conv.json", 'w') as outfile:
    json.dump(perm_df, outfile)