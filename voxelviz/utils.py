import subprocess
import os
import zipfile
import platform
import click
import os.path as op
import nibabel as nib
import json
import numpy as np

default_data_dir = op.join(op.dirname(op.dirname(__file__)))

@click.command()
@click.option('--directory', default=default_data_dir)
def download_data(directory):
    ''' Downloads example data. '''

    url = 'https://surfdrive.surf.nl/files/index.php/s/NRhXx2BevS3BDR9/download'

    cmd = "where" if platform.system() == "Windows" else "which"
    with open(os.devnull, 'w') as devnull:  # check if curl is available
        res = subprocess.call([cmd, 'curl'], stdout=devnull)

        if res != 0:
            raise OSError("The program 'curl' was not found on your computer!"
                          " Either install it or download the data from "
                          "surfdrive: %s" % url)

    dst_file = op.join(directory, 'examples.zip')
    if op.isfile(dst_file):
        msg = ('Zip-file already exists (%s). Probably best to unzip yourself '
               'instead of re-downloading it...' % dst_file)
        raise ValueError(msg)

    dst_dir = dst_file.replace('.zip', '')
    if not op.isdir(dst_dir):
        os.makedirs(dst_dir)
        print("Downloading the data ...\n")
        cmd = "curl -o %s %s" % (dst_file, url)
        return_code = subprocess.call(cmd, shell=True)
        print("\nDone!")
        print("Unzipping ...", end='')
        zip_ref = zipfile.ZipFile(dst_file, 'r')
        zip_ref.extractall(dst_dir)
        zip_ref.close()
        print(" done!")
        os.remove(dst_file)
    else:
        print("Data is already downloaded and located at %s/*" % dst_dir)


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
        df1 = np.max([n_pred - 1, 1])
        df2 = y.size - df1
        MSM = SSM / df1
        F = MSM / (SSE / df2)
        if np.isnan(F) or np.isinf(np.abs(F)):
            F = 0
        return 'Model fit (F-test): %s' % str(np.round(F, 3))
