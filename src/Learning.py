import os
import numpy as np
import random
import math
from tqdm import tqdm
import sys

import matplotlib.pyplot as plt
from matplotlib.colors import Normalize

from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.model_selection import LeaveOneOut
from sklearn.model_selection import KFold
from sklearn.metrics import average_precision_score
from sklearn.metrics import precision_recall_curve
from sklearn.metrics import plot_precision_recall_curve
from sklearn.feature_selection import SelectKBest, f_classif

from src.Prep import Cope
from src.Prep import unmask


class Dataset:
    """
    Class object to which we can load our data before differentiating
    using various ML methods

    Parameters:
        - type (required positional): "cope"
        - mask (default): path to mask to be applied to MRI data
        - network_channels (default): list of channels to be included for fNIRS
    """

    def __init__(
        self,
        type,
        mask="/scratch/claytons/tlbx/templateflow/tpl-MNIPediatricAsym/" + \
            "cohort-2/",
        network_channels=None):

        self.data = []
        self.type = type
        self.mask = mask
        self.network_channels = network_channels
        self.trial_name = None
        self.freq_snip = None
        self.groups = []

    def LoadData(self, path):
        """
        Loads one data at a time, appending it to the Classifier.data attribute

        Parameters:
            - path (required positional): path of file (cope) to be loaded and
              stacked on the parent object's 'data' attribute
              note: objects will be loaded in as Cope objects

        """
        
        fname = os.path.basename(path)

        self.subject = [word.replace('sub-', '') for word in \
            path.split('/') if 'sub-' in word][0]

        self.session = [word.replace('ses-', '') for word in \
            path.split('/') if 'ses-' in word][0]

        if self.type == 'cope':
            self.data.append(
                Cope(

                )

        if (self.data[-1].data.shape != self.data[0].data.shape):
            
            print(
                "Warning:",
                self.type,
                "at \n",
                self.data[-1].subject,
                self.data[-1].startindex,
                "shaped inconsistently with dataset.")
            print("Removing it from dataset.")
            self.data.pop(-1)

            return None

        if self.data[-1].group not in self.groups:
            self.groups.append(self.data[-1].group)
        self.groups.sort()

        # make list of subjects in this dataset
        self.subjects = [item.subject for item in self.data]

    def MakeEstimator(
        self,
        k_fold=None,
        verbosity=True,
        labels=None,
        normalize=None):
        
        """
        Prepares data within Dataset object such that all Dataset.data
        are contained in either self.train_dataset or self.test_dataset,
        with the corresponding subjects listed in self.train_subjects and
        self.test_subjects. This is done either according to a k_fold cross-
        evaluation schema, if k_fold is provided, otherwise is split randomly
        by the float provided in tt_split.

        Parameters:
            - k_fold: (tuple ints, default None)
                cross-validation fold i and total folds k
                ex: (2, 5) fold 2 of 5
            - verbosity: (bool, default True) whether to print information
                such as the ratios of condition positive-to-negative subjects,
                total number of samples loaded into each set, etc.
            - labels: (list, default None) the real set of false and
                positive condition labels, if only loading in one class
                under the context
            - normalize: 'standard', 'minmax', or None
                method with which cope data will be normalized
                note: within itself, not relative to baseline or others

        """
        
        self.subjects.sort()

        loo = LeaveOneOut()
        loo.get_n_splits(self.subjects)

        X = np.array([item.data for item in self.data])
        y = np.array([item.meta[label] for item in self.data])

        i = 0
        for train_index, test_index in loo.split(self.subjects):
            print("TRAIN:", train_index, "TEST:", test_index)
            X_train, X_test = X[train_index], X[test_index]
            y_train, y_test = y[train_index], y[test_index]
            print(X_train, X_test, y_train, y_test)
            if i == k_fold:
                break
            i += 1

        self.X_train = X[train_index]
        self.X_test = X[test_index]
        self.Y_train = y[train_index]
        self.Y_test = y[test_index]

    def model_SVM(
        self,
        kernel='linear',
        degree=10,
        gamma='scale',
        coef0=0.0,
        C=1,
        iterations=1000,
        plot_PR=False,
        plot_Features=False,
        feat_select=True):
        """
        Support Vector Machine classifier using scikit-learn base

        Parameters:
            - kernel: {'linear', 'rbf', 'poly', 'sigmoid'}
            - degree: (int) default 3
            - gamma: (float) default 'scale'
            - coef0: (float) default 0.0
            - C: (float) default 1
            - iterations: (int) default 1000
            - plot_PR: (bool) default False
            - plot_Features: (bool) default False
            - feat_select: (bool) default False
            - num_feats: (int) default 10

        """

        from sklearn.svm import SVR
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler

        ### F-score ###

        from sklearn.feature_selection import f_classif
        
        mask = self.data[0].mask

        f_values, p_values = f_classic(self.X_train, self.Y_train)
        p_values = -np.log10(p_values)
        p_values[np.isnan(p_values)] = 0
        p_values[p_values > 10] = 10

        #p_unmasked = unmask(p_values, mask)
        #plot_haxby(p_unmasked, 'F-score')

        ### SVR ###

        svr = SVR(
            kernel=kernel,
            degree=degree,
            gamma=gamma,
            coef0=coef0,
            C=C)

        ### Dimensionality reduction ###

        from sklearn.feature_selection import SelectKBest, f_classif

        # define the dimension reduction to be used
        # here we use a classical univariate feature selection based on F-test,
        # namely Anova. We set the number of features to be selected to 500
        feature_selection = SelectKBest(f_classif, k=500)

        ### Pipeline ###
        from sklearn.pipeline import Pipeline
        anova_svr = Pipeline([('anova', feature_selection), ('svr', svr)])

        # fit and predict

        anova_svr.fit(self.X_train, self.Y_train)

        y_pred = anova_svr.predict(self.X_test)


        return anova_svr, y_pred
