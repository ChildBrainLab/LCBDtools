import os, csv
import pandas as pd

# Create dataframes for iterating through brief
groupings = {
    'inhibit': [1, 10, 16, 24, 30, 39, 48, 62],
    'self monitoring': [4, 13, 20, 26],
    'shift': [2, 11, 17, 31, 40, 49, 58, 60],
    'emotional control': [6, 14, 22, 27, 34, 43, 51, 56],
    'initiate': [9, 38, 50, 55, 61],
    'working memory': [3, 12, 19, 25, 28, 32, 41, 46],
    'plan/organize': [7, 15, 23, 35, 44, 52, 57, 59],
    'task monitor': [5, 21, 29, 33, 42],
    'organization of materials': [3, 37, 45, 47, 53, 63]
}

group_sums = {
    'inhibit': 0,
    'self monitoring': 0,
    'shift': 0,
    'emotional control': 0,
    'initiate': 0,
    'working memory': 0,
    'plan/organize': 0,
    'task monitor': 0,
    'organization of materials': 0
}

metrics = {
    'BRI' : ['inhibit', 'self monitoring'],
    'ERI' : ['shift', 'emotional control'],
    'CRI' : ['initiate', 'working memory', 'plan/organize', 'task monitor', 'organization of materials'],
    'GEC': ['inhibit', 'self monitoring', 'shift', 'emotional control', 'initiate', 'working memory', 'plan/organize', 'task monitor', 'organization of materials']
}

data = []

# Create a dataframe with the BRIEF questionnaire
breif_df = pd.read_csv('/storage1/fs1/perlmansusan/Active/moochie/study_data/P-CAT/R01/data/WUSTL_data/questionnaire_data/2025.06.09/redcap_2025.06.09.csv')

# Iterate through each entry
for ind, row in breif_df.iterrows():
    c_p = None
    group_sum = group_sums.copy()

    # Iterate through each group
    for scoring_group, questions in groupings.items():
        
        for question in questions: # Iterate through all questions in group

            # check is parent data is present
            if pd.notna(row[f"brief_2_{question}"]) and str(row[f"brief_2_{question}"]).strip() != '':
                # Add score into raw score group

                group_sum[scoring_group] += float(row[f"brief_2_{question}"])

    # Calculate raw score groups
    raw_scores = {group : 0 for group in metrics.keys()}
    for metric, groups in metrics.items():
        
        for group in groups: #Iterate through groups 
            raw_scores[metric] += group_sum[group]
        

    scores = [score for score in raw_scores.values()]
    if sum(scores) > 0:
        data.append([str(row['demo_recordid']), row['visit_date']] + scores)


with open('/storage1/fs1/perlmansusan/Active/moochie/github/LCBDtools/scripts/Questionnaires/brief_2_scores.csv', 'w', newline='') as scored_sheet:
    writer = csv.writer(scored_sheet)
    
    # Write header
    header = ['Family ID', 'Visit Date'] + list(raw_scores.keys())
    writer.writerow(header)
    
    # Write data (list of lists)
    writer.writerows(data)
