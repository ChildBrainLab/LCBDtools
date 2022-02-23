import os, shutil
import glob
from os.path import join

study_path = "/data/perlman/moochie/study_data/CARE/"

data_folders = [
    # "audio_data",
    # "brain_photos",
    # "KBIT_data",
    # "MRI_data",
    # "MRI_data_preproc_122821",
    # "narrative_data",
    # "NIRS_data",
    # "NIRS_data_preproc",
    # "picture_data",
    # "task_data/AHKJ",
    #"task_data/DB_DOS"
    "video_data"
]

def update_subj_number(old_num):
    try:
        if int(str(old_num)[:4]) >= 5000 and int(str(old_num)[:4]) < 6000:
            pass
        split_num = str(old_num).split('-')

        if len(split_num) == 1:
            new_num = str(old_num) + "0"
        elif len(split_num) == 2:
            new_num = str(split_num[0]) + str(split_num[1])
        else:
            print("Failure. Old number:", old_num, "is incompatible.")
            raise Exception
    except:
        print("See error.")
        return None

    return new_num

def get_matches(num_range='[5000-5999]'):
    matches = glob.glob('**/*'+num_range+'**', recursive=True)
    matches_sort = sorted(matches, key=len)
    matches_sort.reverse()
    
    matches = matches_sort
    matches = [match for match in matches if "DICOM" not in match]
    matches = [match for match in matches if "pilot" not in match]

    return matches

def main():
    os.chdir(study_path)

    for data_type in data_folders:
        os.chdir(data_type)

        matches = get_matches()
        # print(matches)

        for match in matches:
            fname = os.path.basename(match)

            if fname[0] == '5': 
                if len(fname) > 4:
                    if fname[4].isnumeric():
                        continue
                    if fname[4] == '-':
                        old_num = fname[:6]
                    else:
                        old_num = fname[:4]
                else:
                    old_num = fname[:4]
            elif fname[:4] == 'sub-':
                if fname[8] == '-':
                    old_num = fname[4:10]
                else:
                    old_num = fname[4:8]
            else:
                continue

            
            new_num = update_subj_number(old_num)
            if new_num is None:
                print("Skipping:", fname)
                continue
            
            new_fname = fname.replace(old_num, new_num)

            shutil.move(match, join(os.path.dirname(match), new_fname))

            #print("Move ", match, "to", join(os.path.dirname(match), new_fname))

        # go back to OG folder
        os.chdir(study_path)


if __name__=='__main__':
    main()


