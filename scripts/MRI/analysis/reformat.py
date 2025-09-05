import os, csv

# Load the data
regression_output_file = "/storage1/fs1/perlmansusan/Active/moochie/analysis/CARE/ROI_deviation/subject-ROI_multiple_regression.csv"
content = []
with open(regression_output_file, 'r') as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        content.append(row)
header = content.pop(0)

# Create a dataframe for storing data
reformatted = {}

# Iterate through each line
last_subject = ''
for line in content:
    # Grab line data
    subject = line[0]
    movie = line[1]
    ROI = line[2]
    segment = line[3]
    conflict = line[4]
    valence = line[5]
    volatility = line[6]
    beta = line[7]
    intercept = line[8]

    # Check if subject changed
    if subject != last_subject:
        last_subject = subject
        reformatted[subject] = {}

    # Check if we've seen this ROI for the subject
    if ROI not in reformatted[subject].keys():
        reformatted[subject][ROI] = {}

    # Add information to dataframe
    reformatted[subject][ROI][segment] = [movie, conflict, valence, volatility, beta, intercept]


# Iterate through dataframe and add into new file
new_header = []
new_contents = []
for subject in reformatted.keys():

    for ROI in reformatted[subject].keys():
        header = ['Subject', 'ROI', 'Movie']
        row_content = [subject, ROI, None]

        for segment in reformatted[subject][ROI].keys():
            # Check if segment was a full
            num_split = segment.split('-')
            if int(num_split[1]) - int(num_split[0]) != 100:
                break

            # Update movie
            row_content[2] = reformatted[subject][ROI][segment][0]

            # Add content
            header += ['Segment', 'Valence', 'Volatility', 'Beta', 'Intercept']
            row_content += [segment, valence, volatility, beta, intercept]
    
        if row_content:
            new_contents.append(row_content)

        if len(header) > len(new_header):
            new_header = header

new_contents = [header] + new_contents

with open("/storage1/fs1/perlmansusan/Active/moochie/analysis/CARE/ROI_deviation/subject-ROI_multiple_regression_reformatted.csv", mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerows(new_contents)  # write all rows at once