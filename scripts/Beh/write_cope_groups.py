# usage: python write_cope_scores.py <score_df_file> <subject_list.txt> <output_file>

import os
import numpy as np
import pandas as pd
import sys

dffile = sys.argv[1]
subfile = sys.argv[2]
of = sys.argv[3]

# load in Emily Hone's df file probably
df = pd.read_csv(dffile)

# get list of subjects, as formatted by Emily Hone's df file
f = open(subfile, 'r')

subs = []

for line in f.readlines():
    sub = [word for word in line.split('/') if "sub-" in word][0]
    sub = sub.strip('sub-')
    subs.append(sub)

f.close()

fmtsubs = [sub[:4]+'-'+sub[-1] for sub in subs]

scores = []
# get score for each subject
for sub in fmtsubs:
    enroll_group = df[df['record_id']==sub]['enroll_group'].iloc[0]
    rdas = df[df['record_id']==sub]['total'].iloc[0]
    if (enroll_group == 2) or (rdas < 48):
        scores.append(2)
    else:
        scores.append(1)

# write output file
f = open(of, 'w')

for i, score in enumerate(scores):
    if i > 0:
        f.write('\n')
    f.write(str(score))
f.close()
