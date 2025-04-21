import numpy as np
import pandas as pd
import nibabel


def unmask(X, mask_img, order='C'):
    """
    Take masked data and bring them back to 3D (space only)

    Parameters
    ==========
    X: numpy.ndarray
        Masked data. shape: (samples,)

    mask_img: niimg
        3D mask array: True where a voxel should be used

    """
    
    if X.ndim == 1:
        data = np.zeros(
            (mask_data.shape[0], mask_data.shape[1], mask_data.shape[2]),
            detype=X.dtype, order=order)
        data[mask_data] = X
        return data
    elif X.ndim == 2:
        data = np.zeros(
            mask_data.shape + (X.shape[0],), dtype=X.dtype, order=order)
        data[mask_data, :] = X.T
        return data
    raise ValueError("X must be 1-dimensional or 2-dimensional")


class Cope:
    """
    Object intended to store information on a cope image
    (contrast of parameter estimates) output by either FSL or SPM first-level
    general linear modelling with FMRI data. 

    .nii or .nii.gz paths should be sufficient

    Best used on data stored in BIDS format
    """
    def __init__(
        self,
        path,
        mask=None,
        cov=None):
        
        self.path = path
        self.cov = cov
        func_data = nibabel.load(path).get_data()

        ### masking step ###
        if mask is not None:
            mask = nibabel.load(mask).get_data()

            # ensure that the mask is boolean
            mask = mask.astype(bool)
            self.mask = mask
            # apply the mask, X= timeseries * voxels
            X = func_data[mask].T
            self.data = X

            """
            unmask data:
            unmasked_data = numpy.zeros(mask.shape, dtype=X.dtype)
            unmasked_data[mask] = X
            """

    def plot(self, bg_img):
        import matplotlib.pyplot as plt

        bg = nibabel.load(bg_img).get_data()

        act = bg.copy()
        act[act < 6000] = 0.

        plt.imshow(
            bg[..., 10].T,
            origin='lower',
            interpolation='nearest',
            cmap='gray')
        
        masked_act = np.ma.masked_equal(act, 0.)

        plt.imshow(
            masked_act[..., 10].T,
            origin='lower',
            interpolation='nearest',
            cmap='hot')

        plt.show(block=True)

    
    def f_score(self):

        from sklearn.feature_selection import f_classif
        f_values, p_values = f_classif(self.data, self.cov)
        p_values = -np.log10(p_values)
        p_values[np.isnan(p_values)] = 0
        p_values[p_values > 10] = 10
        p_unmasked = masking.unmask(p_values, mask)

        plot_haxby(p_unmasked, 'F-score')
