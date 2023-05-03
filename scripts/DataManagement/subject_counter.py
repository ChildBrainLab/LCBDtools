
import os, sys

data_path = '../../../../analysis/CARE/MRI_data_clean_2/'

class counter:
    def __init__(self, path):
        self.data_path = path
    
    def count(self):
        self.subject_count = {}
        subjects = os.listdir(self.data_path)
        for subject in subjects:
            if os.path.isdir() == False:
                continue    
            sessions = os.listdir()
            for session in sessions:
                if session not in self.subject_count.keys():
                    self.subject_count[session] = []
                self.subject_count[session].append(subject)
                        
    def count_dyads(self):

