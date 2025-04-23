# usage: python get_loudness.py <path/to/audio.wav> <outfile.txt>

import numpy as np
import soundfile as sf
import pyloudnorm as pyln
import sys
sys.path.append('../../')
from src.TimeSeries import TimeSeries
import math

audiofile = sys.argv[1]
outfile = sys.argv[2]

data, rate = sf.read(audiofile)

print("data:", data)
print("data shape:", data.shape)
print("rate:", rate)

meter = pyln.Meter(rate, block_size=0.8)

ts = []
ts.append(0)
for window in np.array_split(data, math.floor(len(data)/(0.8*rate))):
    loudness = meter.integrated_loudness(window)
    ts.append(loudness)

ts = TimeSeries(
    ts,
    time=np.linspace(0, len(ts) / 1.25, num=len(ts)),
    sampleRate=1.25)

ts.fix_inf()
ts.lag_correct()
ts.resample(sample_rate=0.8)
ts.lag_correct()
ts.savgol_filter(w=5)
ts.standardize()

f = open(outfile, 'w')

for i, val in enumerate(ts.signal):
    if i > 0:
        f.write('\n')
    f.write(str(val))

f.close()
