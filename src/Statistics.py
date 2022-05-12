import os
import numpy as np
import math
from tqdm import tqdm

# INTRACLASS CORRELATION COEFFICIENT
# ===================================

# https://stats.stackexchange.com/questions/63368/
# intra-class-correlation-and-experimental-design

def unordered_pearson(Y):
    """
    The assessment of correlation via the familiar Pearson product-moment
    procedure applies only to those situations where one particular member of a
    bivariate pair of measures unequivocally belongs to the X variable and the
    other unequivocally belongs to the Y variable.

    When it is entirely arbitrary which of the items within the pair is listed
    first and which is listed second.

    :param Y: N x X matrix (rows = raters, columns = measurements)
    :type Y: numpy.array


    """


# def simple_icc(
#     X,
#     Y,
#     icc_type='ICC1'):
#     """
#     Computes the intraclass correlation coefficient via Pingouin
#     of a given 2 equally-sized arrays. The expectation at build
#     is that they are linear time-series.
#
#     :param X: TimeSeries
#     :type X: TimeSeries.TimeSeries
#     :param Y: TimeSeries
#     :type Y: TimeSeries.TimeSeries
#     :param icc_type: one of {ICC1, ICC2, ICC3, ICC1k, ICC2k, ICC3k}
#     :type icc_type: str
#     """
#     import pingouin as pg
#     import pandas as pd
#
#     df1 = pd.DataFrame(X.signal, columns=['rating'])
#     df1['participant'] = X.meta['participant']
#     df1['time'] = X.time
#
#     df2 = pd.DataFrame(Y.signal, columns=['rating'])
#     df2['participant'] = Y.meta['participant']
#     df2['time'] = Y.time
#
#     df3 = pd.concat([df1, df2])
#
#     icc = pg.intraclass_corr(
#         data=df3,
#         targets='time',
#         raters='participant',
#         ratings='rating')
#
#     icc.set_index("Type")
#
#     return icc

def ping_icc(
    dX,
    icc_type='ICC1'):
    """
    Computes the intraclass correlation coefficient via Pingouin
    of a given 2 equally-sized arrays. The expectation at build
    is that they are linear time-series.

    :param dX: list of TimeSeries.TimeSeries objects for which the
        icc will be calculated
    :type dX: list of TimeSeries.TimeSeries
    :param icc_type: one of {ICC1, ICC2, ICC3, ICC1k, ICC2k, ICC3k}
    :type icc_type: str
    """
    import pingouin as pg
    import pandas as pd

    dfs = []
    for ts in dX:
        df = pd.DataFrame(ts.signal, columns=['rating'])
        df['participant'] = ts.meta['participant']
        df['time'] = ts.time
        dfs.append(df)

    df = pd.concat(dfs)

    icc = pg.intraclass_corr(
        data=df,
        targets='time',
        raters='participant',
        ratings='rating',
        # nan_policy='omit'
    )

    icc.set_index("Type")

    return icc

def icc(Y, icc_type='ICC(3,k)'):
    """
    Calculate intraclass correlation coefficient

    ICC Formulas are based on:
    Shrout, P. E., & Fleiss, J. L. (1979). Intraclass correlations: uses in
    assessing rater reliability. Psychological bulletin, 86(2), 420.
    icc1:  x_ij = mu + beta_j + w_ij
    icc2/3:  x_ij = mu + alpha_i + beta_j + (ab)_ij + epsilon_ij
    Code modifed from nipype algorithms.icc
    https://github.com/nipy/nipype/blob/master/nipype/algorithms/icc.py

    :param Y: N x X matrix (rows = raters, columns = measurements)
    :type Y: numpy.array
    :param icc_type: type of ICC to calculate, one of: {ICC(2,1), ICC(2, k),
        ICC(3, 1), ICC(3, k)}
    :type icc_type: str

    :return: ICC (numpy.array) intraclass correlation coefficient
    """
    from numpy import ones, kron, mean, eye, hstack, dot, tile
    from numpy.linalg import pinv

    try:
        [n, k] = Y.shape
    except:
        n = Y.shape[0]
        k = 2

    # Degrees of Freedom
    dfc = k - 1
    dfr = n - 1

    # if dfc == 0:
    #     dfc = 1
    # if dfr == 0:
    #     dfr = 1

    dfe = dfc * dfr

    # Sum Square Total
    mean_Y = np.mean(Y)
    SST = ((Y - mean_Y) ** 2).sum()

    # create the design matrix for the different levels
    x = np.kron(np.eye(k), np.ones((n, 1)))  # sessions
    x0 = np.tile(np.eye(n), (k, 1))  # subjects
    X = np.hstack([x, x0])

    # Sum Square Error
    predicted_Y = np.dot(np.dot(np.dot(X, np.linalg.pinv(np.dot(X.T, X))),
                                X.T), Y.flatten('F'))
    residuals = Y.flatten('F') - predicted_Y
    SSE = (residuals ** 2).sum()

    MSE = SSE / dfe

    # Sum square column effect - between columns
    SSC = ((np.mean(Y, 0) - mean_Y) ** 2).sum() * n
    MSC = SSC / dfc  # / n (without n in SPSS results)

    # Sum Square subject effect - between rows/subjects
    SSR = SST - SSC - SSE
    MSR = SSR / dfr

    if icc_type == 'icc1':
        # ICC(2,1) = (mean square subject - mean square error) /
        # (mean square subject + (k-1)*mean square error +
        # k*(mean square columns - mean square error)/n)
        # ICC = (MSR - MSRW) / (MSR + (k-1) * MSRW)
        NotImplementedError("This method isn't implemented yet.")

    elif icc_type == 'ICC(2,1)' or icc_type == 'ICC(2,k)':
        # ICC(2,1) = (mean square subject - mean square error) /
        # (mean square subject + (k-1)*mean square error +
        # k*(mean square columns - mean square error)/n)
        if icc_type == 'ICC(2,k)':
            k = 1
        ICC = (MSR - MSE) / (MSR + (k-1) * MSE + k * (MSC - MSE) / n)

    elif icc_type == 'ICC(3,1)' or icc_type == 'ICC(3,k)':
        # ICC(3,1) = (mean square subject - mean square error) /
        # (mean square subject + (k-1)*mean square error)
        if icc_type == 'ICC(3,k)':
            k = 1
        ICC = (MSR - MSE) / (MSR + (k-1) * MSE)

    return ICC

# def simple_icc(Y):
#     s2 = (1 / (2 * Y.shape[0])) * (np.sum([
#         ((Y[rater] - np.mean(Y))**2) for rater in Y]) +\
#         np.sum()
#     ])
#     r = (1 / (3 * Y.shape[0] * ))

# INTER-RATER RELIABILITY METHODS
# =================================
# https://www.statisticshowto.com/inter-rater-reliability/
