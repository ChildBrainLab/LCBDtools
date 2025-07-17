import os, csv
from glob import glob
import numpy as np

# Grab all rating files
atv_files = glob('/storage1/fs1/perlmansusan/Active/moochie/study_data/ATV_LCBD/session_materials/ATV_task/data/*.csv')

# Data frame
movie_ratings = {
    'A': [],
    'B': [],
    'C': []
}

# Iterate through each file
for atv_file in atv_files:
    ratings = {
    'A': [],
    'B': [],
    'C': []
    }

    # Figure out movie order
    splits = atv_file.split('/')[-1].split('_')

    order = splits[1]
    if order == 'ATV': # Skip test cases
        continue

    # Read content
    with open(atv_file, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        content = [row for row in csvreader]

    for row in content[1:]: # Iterate through file and add ratings
        if len(row) > 34 and row[33] != '': # Check for first movie
            if row[33] not in ['None', 'space']:
                ratings[order[0]].append(float(row[33]))
        
        if len(row) > 60 and row[59] != '': # Check for first movie
            if row[59] not in ['None', 'space']:
                ratings[order[1]].append(float(row[59]))

        if len(row) > 86 and row[85] != '': # Check for first movie
            if row[85] not in ['None', 'space']:
                ratings[order[2]].append(float(row[85]))

    # Append movie ratings found to data frame
    for movie in movie_ratings.keys():
        if ratings[movie]:
            movie_ratings[movie].append(ratings[movie])

# Iterate through each movie
movie_len = {
    'A': 1604,
    'B': 1704,
    'C': 1653
}
for movie in movie_ratings.keys():
    
    # Find max length
    max_len = 0
    for subject_rating in movie_ratings[movie]:
        if len(subject_rating) > max_len:
            max_len = len(subject_rating)

    # Format ratings
    for subject_ind, subject_rating in enumerate(movie_ratings[movie]):
        print(subject_rating)
        if isinstance(subject_rating, list) and len(subject_rating) < max_len:
            movie_ratings[movie][subject_ind] += [np.nan for ind in range(max_len - len(subject_rating))]

    # Calculate standard deviation
    ratings = np.array(movie_ratings[movie])
    print(f"Ratings shape: {ratings.shape}")
    stack = np.vstack(ratings)
    print(f"Movie {movie} stack shape: {stack.shape}")
    volatility = np.nanstd(stack, axis = 0)
    print(f"Volatility shape: {volatility.shape}")
    
    # Resize to TR frequency
    volatility_old = np.linspace(0, 1, len(volatility[3:]))     # Original normalized positions (0 to 1)
    volatility_new = np.linspace(0, 1, movie_len[movie])

    volatility_interp = np.interp(volatility_new, volatility_old, volatility[3:]) 

    print(f"New shape: {volatility_interp.shape}")

    with open(f"AHKJ_movie{movie}_volatility.txt", "w") as file:
        for number in volatility_interp:
            file.write(str(number) + '\n')