import pandas as pd
import os
import numpy as np
import subprocess
from glob import glob
import msoffcrypto
import io


USER = os.getlogin()
f = open(f"./CNDA_downloads/.lcbd_creds", 'r')
pw = f.readline().strip()
f.close()

CNDAqueue = "./CNDA_downloads/CNDA_download_queue.txt"

if os.path.isfile(CNDAqueue):
    os.remove(CNDAqueue)


try:
    f = open("./CNDA_downloads/CNDA_downloaded.txt", 'r')
    downloaded_sessions = [str(line).strip() for line in f.readlines()]
    f.close()

except:
    downloaded_sessions = []


sheets = ["V0", "V1", "V2"]

dt_subs = {}

f = open(CNDAqueue, 'w')

decrypted_workbook = io.BytesIO()

for sheet in sheets:
    
    with open(
        "./CNDA_downloads/CARE_dataTracker.xlsx",  # /data/perlman/moochie/study_data/CARE/study_info/Logs/CARE_dataTracker.xlsx  
        'rb') as file:
        office_file = msoffcrypto.OfficeFile(file)
        office_file.load_key(password=pw)
        office_file.decrypt(decrypted_workbook)
    file.close()

    df = pd.read_excel(
        decrypted_workbook,
        sheet_name=sheet,
        engine='openpyxl')

    df['CNDA Label'].replace('', np.nan, inplace=True)

    df.dropna(subset=['CNDA Label'], inplace=True)

    dt_subs[sheet] = df['CNDA Label']

    for label in dt_subs[sheet]:
        labels = str(label).split(',')

        for CNDAlabel in labels:
            if CNDAlabel not in downloaded_sessions:
                
                f.write(CNDAlabel.strip())
                f.write('\t')
                f.write(str(sheet))
                f.write('\n')

f.close()
