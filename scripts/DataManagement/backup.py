import shutil, os
from datetime import date
from datetime import datetime
from pathlib import Path


print("Backing up data on moochie!")

today = str(date.today())
destination = 'E:/backup/'
sourcebase = "Z:/Active/"

# Generate backup sources 
with open(f'{destination}backup_items.txt', 'r') as file:
    sources = [f'{sourcebase}{line.split('\n')[0]}' for line in file.readlines()]

# Count current backup count and remove excess
max_count = 2
folders = [f for f in os.listdir(destination) if os.path.isdir(os.path.join(destination, f))]
sorted_folders = sorted(folders, key=lambda f: datetime.strptime(f, "%Y-%m-%d"))
while len(sorted_folders) >= max_count:
    excess_folder = sorted_folders.pop(0)
    print(f'Number of backups exceeded, deleting old folder {excess_folder}...')
    shutil.rmtree(f"{destination}{excess_folder}")

# Create the new backup folder
destination += today + '/'
Path(destination).mkdir(parents = True, exist_ok = True)

for source in sources:
    basename = source.split(sourcebase)[-1]
    
    print(f"Copying over {basename} to {destination}...")

    Path(destination + '/'.join(basename.split('/')[:-1])).mkdir(parents = True, exist_ok = True)
    shutil.copytree(source, destination + basename, dirs_exist_ok = True)

print("Backup complete...")
