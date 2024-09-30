import shutil
from datetime import date
from pathlib import Path


print("Backing up data!")

today = str(date.today())

destination = 'E:/backup/'

sourcebase = "Z:/Active/"
sources = [f'{sourcebase}moochie/study_data/CARE/NIRS_data/',
           f'{sourcebase}moochie/study_data/CARE/task_data/']


# Count current backup count and remove excess

# Create the new backup folder
destination += today + '/'
Path(destination).mkdir(parents = True, exist_ok = True)

for source in sources:
    basename = source.split(sourcebase)[-1]
    
    print(f"Copying over {basename} to {destination}...")

    Path(destination + '/'.join(basename.split('/')[:-1])).mkdir(parents = True, exist_ok = True)
    shutil.copytree(source, destination + basename, dirs_exist_ok = True)

print("Backup complete...")
