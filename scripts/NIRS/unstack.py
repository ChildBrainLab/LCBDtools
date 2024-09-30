import csv

studys = ['CARE', 'P-CAT']

filenames = ['wct_full_permuted_values_new_V2.csv', 'wct_full_permuted_values.csv', 'wct_full_permuted_values_new.csv', 'wct_full_permuted_values_new_1.csv']


def unstack_file(filename, folder, study, unstack = True, DOI = True, ROI = True):
	ROI = True
	ROIs = {
		'Left DLPFC':['S3_D2 hbo', 'S4_D2 hbo'],
		'Right DLPFC':['S5_D3 hbo', 'S6_D3 hbo'],
		'Left VLPFC':['S1_D1 hbo', 'S2_D1 hbo', 'S2_D2 hbo'],
		'Right VLPFC':['S7_D3 hbo', 'S7_D4 hbo', 'S8_D4 hbo'],
		'VLPFC': ['S1_D1 hbo', 'S2_D1 hbo', 'S2_D2 hbo', 'S7_D3 hbo', 'S7_D4 hbo', 'S8_D4 hbo'],
		'DLPFC': ['S3_D2 hbo', 'S4_D2 hbo', 'S5_D3 hbo', 'S6_D3 hbo'],
		'Left Hemisphere': ['S3_D2 hbo', 'S4_D2 hbo', 'S1_D1 hbo', 'S2_D1 hbo', 'S2_D2 hbo'],
		'Right Hemisphere': ['S5_D3 hbo', 'S6_D3 hbo', 'S7_D3 hbo', 'S7_D4 hbo', 'S8_D4 hbo'],
		'Whole Brain': ['S3_D2 hbo', 'S4_D2 hbo', 'S1_D1 hbo', 'S2_D1 hbo', 'S2_D2 hbo', 'S5_D3 hbo', 'S6_D3 hbo', 'S7_D3 hbo', 'S7_D4 hbo', 'S8_D4 hbo']
		}

	channel_start = 3
	try:
		with open(folder + filename, 'r') as csv_file:
			csv_contents = csv.reader(csv_file)
			data = [row for row in csv_contents]
	except:
		print(f'{folder}{filename} not found or failed to read')
		return
		
	# LCBD NIRS typical header = ['', 'Parent', 'Child', 'Block', 'S1_D1 hbo', 'S2_D1 hbo', 'S2_D2 hbo', 'S3_D2 hbo', 'S4_D2 hbo', 'S5_D3 hbo', 'S6_D3 hbo', 'S7_D3 hbo', 'S7_D4 hbo', 'S8_D4 hbo']
	header = data.pop(0)

	current_subject = None
	total_blocks = 0

	for region, channels in ROIs.items():
		channels_ind = [[ind for ind, channel in enumerate(header[channel_start:]) if channel == COI][0] + channel_start for COI in channels]
		ROIs[region] = channels_ind
	header[channel_start:] = ROIs.keys()


	stacked_data = {}
	for datum in data:
		if header[0] in [0, '0']:	# Reformat if row numbers included in sheet
			datum.insert(0, 0)

		dyad = False
		parent = datum[1]
		child = datum[2]

		if parent[:-1] == child[:-1]: # Check if real dyad
			dyad = True
		if dyad == DOI: # Check if dyad status matches what we want to save
			if f"{parent}-{child}" not in stacked_data.keys():# Check if new subject
				stacked_data[f"{parent}-{child}"] = {} # Append new list if new
			block = int(datum[3][-1])
			if block > total_blocks:
				total_blocks = block
			
			if ROI == False:
				stacked_data[f"{parent}-{child}"][block] = datum[channel_start:] # Save block data
			else:
				if block not in stacked_data[f"{parent}-{child}"].keys():
					stacked_data[f"{parent}-{child}"][block] = []
					
				for region, channels_ind in ROIs.items():
					average = 0
					for channel_ind in channels_ind:
						average += float(datum[channel_ind])
					stacked_data[f"{parent}-{child}"][block] += [average/len(channels_ind)]
			
				
	# Iterate through dyads of interest and 
	new_data = []
	dyad_count = 0
	for dyad, blocks in stacked_data.items():
		dyad_count += 1
		dyad_split = dyad.split('-')
		new_datum = [dyad_count, dyad_split[0], dyad_split[1]]
		for block, channels in sorted(blocks.items()):		
			if unstack == True:		
				new_datum += channels
			else:
				new_data.append(new_datum + [block] + channels)
		if unstack == True:	
			new_data.append(new_datum)
		
	# Create header for data
	new_header = ['', 'Parent', 'Child']

	if unstack == True:
		for block in range(1, total_blocks + 1):
			for channel_name in header[channel_start:]:
			    new_header.append(f'Block_{block}-{channel_name}')
	else:
		new_header += ['Block']	
		new_header += header[channel_start:]

	if unstack == True:
		stack_status = 'unstacked'
	else:
		stack_status = 'stacked'

	new_filename = f'{folder}{stack_status}_{str(DOI).lower()}_dyads_{filename}'
	with open(new_filename, 'w') as csvfile:
		csvwriter = csv.writer(csvfile)
		csvwriter.writerow(new_header)
		for datum in new_data:
			csvwriter.writerow(datum)
	print(f"{new_filename} successfully created...")

for study in studys:
	folder = f'/data/perlman/moochie/analysis/{study}/Test_Analysis/'
	for filename in filenames:
		for unstack in [False, True]:
			for DOI in [False, True]: # Dyads of interest (i.e,. false dyads or true dyads)
				unstack_file(filename, folder, study, unstack, DOI)	

	
