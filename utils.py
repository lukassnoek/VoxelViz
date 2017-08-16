import os.path as op
import nibabel as nib
import json
import numpy as np


def index_by_slice(direction, sslice, img):

    if isinstance(img, str):
        img = nib.load(img).get_data()

    if direction == 'X':
        img = img[sslice, :, :, ...]
    elif direction == 'Y':
        img = img[:, sslice, :, ...]
    else:
        img = img[:, :, sslice, ...]

    return img


def load_data(feat_dir, load_func=False):

    path = op.join(feat_dir + '.feat')
    con = nib.load(op.join(path, 'stats', 'tstat1.nii.gz')).get_data()

    if load_func:
        func = nib.load(op.join(path, 'filtered_func_data.nii.gz')).get_data()
        return func, con
    else:
        return con


def standardize(func):
    return (func - func.mean(axis=-1, keepdims=True)) / func.std(axis=-1, keepdims=True)


def read_design_file(feat_dir):
    path = op.join(feat_dir + '.feat')
    design_file = op.join(path, 'design.mat')
    mat = np.loadtxt(design_file, skiprows=5)

    if not np.all(mat == 1.0):
        mat = np.hstack((np.ones((mat.shape[0], 1)), mat))

    if mat.ndim == 1:
        mat = mat[:, np.newaxis]

    return mat


def calculate_statistics(y, y_hat, n_pred, grouplevel):

    SSE = ((y_hat - y) ** 2).sum()
    
    if grouplevel:
        return 'Model fit (mean squared error): %.3f' % (SSE / float(y.size))
    else:
        SSM = ((y_hat - y.mean()) ** 2).sum()
        df1 = np.max(n_pred - 1, 1)
        df2 = y.size - df1
        MSM = SSM / df1
        F = MSM / (SSE / df2)
        if np.isnan(F) or np.isinf(np.abs(F)):
            F = 0
        return 'Model fit (F-test): %s' % str(np.round(F, 3))
