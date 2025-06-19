import os, csv
import pandas as pd

# Create dataframes for iterating through brief
groupings = {
    'inhibit': [3, 8, 13, 18, 23, 28, 33, 38, 43, 48, 52, 54, 56, 58, 60, 62],
    'shift': [5, 10, 15, 20, 25, 30, 35, 40, 45, 50],
    'emotional control': [1, 6, 11, 16, 21, 26, 31, 36, 41, 46],
    'working memory': [2, 7, 12, 17, 22, 27, 32, 37, 42, 47, 51, 53, 55, 57, 59, 61, 63],
    'plan/organize': [4, 9, 14, 19, 24, 29]
}

group_sums = {
    'inhibit': 0,
    'shift': 0,
    'emotional control': 0,
    'working memory': 0,
    'plan/organize': 0
}

metrics = {
    'Inhibitory Self-Control Index' : ['inhibit', 'emotional control'],
    'Flexibility Index' : ['shift', 'emotional control'],
    'Emergent Metacognition Index' : ['working memory', 'plan/organize'],
    'Global Executive Composite ': ['inhibit', 'shift', 'emotional control', 'working memory', 'plan/organize']
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
            if pd.notna(row[f"brief_p_{question}"]) and str(row[f"brief_p_{question}"]).strip() != '':
                # Add score into raw score group

                group_sum[scoring_group] += float(row[f"brief_p_{question}"])

    # Calculate raw score groups
    raw_scores = {group : 0 for group in metrics.keys()}
    for metric, groups in metrics.items():
        
        for group in groups: #Iterate through groups 
            raw_scores[metric] += group_sum[group]
        

    scores = [score for score in raw_scores.values()]
    if sum(scores) > 0:
        data.append([str(row['demo_recordid']), row['visit_date']] + scores)


with open('/storage1/fs1/perlmansusan/Active/moochie/github/LCBDtools/scripts/Questionnaires/brief_p_scores.csv', 'w', newline='') as scored_sheet:
    writer = csv.writer(scored_sheet)
    
    # Write header
    header = ['Family ID', 'Visit Date'] + list(raw_scores.keys())
    writer.writerow(header)
    
    # Write data (list of lists)
    writer.writerows(data)
