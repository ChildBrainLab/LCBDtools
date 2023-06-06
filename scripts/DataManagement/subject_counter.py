
import os, sys


class counter:
    def __init__(self, path = None):
        if path != None:
            self.data_path = path
        else:
            self.data_path = '../../../../analysis/CARE/CNDA_downloads'

    def count(self):
        self.subject_count = {}
        subjects = os.listdir(self.data_path)
        for subject in subjects:
            if os.path.isdir(self.data_path + subject) == False:
                continue    
            sessions = os.listdir(self.data_path + subject)
            for session in sessions:
                if session not in self.subject_count.keys():
                    self.subject_count[session] = []
                self.subject_count[session].append(subject)
                        
    def count_dyads(self):
        self.dyad_count = {}
        for session in self.subject_count.keys():
            found = []
            for subject in self.subject_count[session]:
                if subject[:5] not in found:
                    found.append(subject[:5])
            self.dyad_count[session] = found       

