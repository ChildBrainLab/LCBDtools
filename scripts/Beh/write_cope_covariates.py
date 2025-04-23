# usage: python write_cope_covariates.py <df_path> <subj_list.txt> <output path> <columns of interest>

"""
# example: python write_cope_covariates.py /mydf.csv /copes.txt /covs.txt q1,q2,q3

This will write out the models in a tab-delimited file readable by
FSL FEAT, and you can paste into the design matrix to make .mat and .con files

There will be an extra column of 1s, and a 
"""

import os
import numpy as np
import pandas as pd
import sys

dffile = sys.argv[1]
subfile = sys.argv[2]
of = sys.argv[3]
cois = sys.argv[4]

cois = cois.split(',')

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
    vals = []
    for coi in cois:
        val = df[df['record_id']==sub][coi].iloc[0].astype(float)
        vals.append(float(val))
    scores.append(vals)

# demean columns
scores = np.array(scores)
# get col means
col_means = np.mean(scores, axis=0)
# copy and transpose
demeaned = scores.copy().transpose()
# iterate over rows and demean
for i in range(demeaned.shape[0]):
    demeaned[i] = demeaned[i] - col_means[i]
# show means are 0?
print("Make sure means are ~0.")
print(demeaned.mean(axis=1))
# transpose back
scores = demeaned.transpose()

# write output file
f = open(of, 'w')

for i, row in enumerate(scores):
    if i > 0:
        f.write('\n')
    f.write(str(1))
    for val in row:
        f.write('\t')
        f.write(str(val))
f.close()
