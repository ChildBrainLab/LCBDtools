# usage: python get_luminances.py <input.mp4> <output.txt> 

import os
import numpy as np
import cv2
import sys
from tqdm import tqdm
sys.path.append('../../')
from src.TimeSeries import TimeSeries

videopath = sys.argv[1]
outpath = sys.argv[2]

def framewise_luminance(frame):

    # Karim and Perlman, 2017
    # Jackson and Sirois, 2009;
    # Poynton, 2003
    luminance = (0.213 * np.average(frame[:,:,0])) # red
    luminance += (0.715 * np.average(frame[:,:,1])) # green
    luminance += (0.072 * np.average(frame[:,:,2])) # blue

    return luminance

larray = []
vidcap = cv2.VideoCapture(videopath)

success, image = vidcap.read()
total = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
fps = int(vidcap.get(cv2.CAP_PROP_FPS))

print("Reading frames:")
pbar = tqdm(total=total)

count = 0
while success:
    larray.append(framewise_luminance(image))
    success, image = vidcap.read()
    count += 1
    pbar.update(1)

vidcap.release()
cv2.destroyAllWindows()
pbar.close()

# load as TimeSeries object
larray = np.array(larray)
ts = TimeSeries(
    larray,
    time=np.linspace(0, total/fps, num=total),
    sampleRate=fps)
ts.lag_correct()
ts.resample(sample_rate=0.8)
ts.lag_correct()
ts.savgol_filter(w=5)
ts.standardize()

"""
import matplotlib.pyplot as plt
fig = plt.figure()
plt.plot(ts.signal)
plt.show(block=True)

plt.clf()
"""

f = open(outpath, 'w')

for i, val in enumerate(ts.signal):
    if i > 0:
        f.write('\n')
    f.write(str(val))

f.close()
