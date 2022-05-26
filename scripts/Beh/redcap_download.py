from redcap import Project
import os
import csv
import pandas
import sys

# usage: python3 redcap_download.py /path/to/save/output.csv

outfile = sys.argv[1]

api_url = 'https://redcap.wustl.edu/api/'
api_key = os.environ['REDCAP_API_TOKEN']

project = Project(api_url, api_key)

csv_data = project.export_records(format='csv')

data_frame = project.export_records(format='df')

pandas.DataFrame.to_csv(
    data_frame,
    outfile)
