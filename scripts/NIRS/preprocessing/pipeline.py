# General dependencies
import os, shutil, matplotlib, json, sys, mne, mne_nirs
from os.path import join
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from copy import deepcopy
from glob import glob
from itertools import compress

# Load custom modules from LCBDtools
import processor as proc
import annotator as ann
import LCBDtools.Stimuli
from LCBDtools.src import argParser
from LCBDtools.src import Plots


class pipeline:
	def __init__(self, args):
		os.listdir('config/')# Grab the configuration folder

		# Some configuration variables
		self.nirs_dir = args.data_folder
		self.task_dir = args.task_folder
		self.output_dir = args.output_dir
		self.task = args.task
		self.ex_subs = args.ex_subs # any subjects to not include in the dataset
		self.in_subs = args.in_subs # limit inclusion to these subjects
		self.covariates = args.covariates # read covariates from a csv file



	def orient(self, config):

		if self.covariates is not None:
		    self.covariates = pd.read_csv(self.covariates)

		if self.bad_channels is not None:
		    f = open(self.bad_channels, 'r')
		    self.bad_channels_dict = json.load(f)
		    f.close()

		# Remove excluded and include subjects as needed through in_subs and ex_subs


		# get all matching session dirs with subject in top level of glob
		self.nirs_dirs = glob(nirs_dir+"*/*/*/")
		self.session_dirs = [d[nirs_dir_len:] for d in self.session_dirs]

		# subjects are top level folders in the study_dir that have
		# session folders with this run
		self.subjects = [d.split('/')[0] for d in self.session_dirs]


	def run(self):
		self.processor = proc.processor()

		for i, ses in enumerate(self.session_dirs):
		    subject = self.subjects[i]
			self.processor.preprocess(ses, subject)

	def locate(self, dir, string):
		dir, files = os.listdir()
