import csv, os
import numpy as np
from scipy import stats

# Define runtime parameters
folder = "/storage1/fs1/perlmansusan/Active/moochie/analysis/CARE/Test_Analysis/"
filepath = "wct_full_ses-0_permuted_values_fix.csv"

# Define t-test variables
group1 = []
group2 = []

# Load folder contents
content = []
with open(f"{folder}{filepath}", "r") as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        content.append(row)
    header = content.pop(0)

# Split data into group 1 and group 2
for row in content:
    
    # Check that all channel synchrony calc
    nums = [False if datum == '' else True for datum in row]
    if sum(nums) != len(nums): # Skip if not
        continue

    # Calc synchrony
    sync = [float(datum) for datum in row[3:]]
    avg_sync = sum(sync) / len(sync)
    
    # Add average sync for subject block to group
    if row[0][:5] == row[1][:5]:
        group1.append(avg_sync)
    else:
        group2.append(avg_sync)


t_stat, p_value = stats.ttest_ind(group1, group2)
print("t =", t_stat, "p =", p_value)

