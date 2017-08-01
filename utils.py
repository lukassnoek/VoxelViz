import os.path as op
import nibabel as nib
import json

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
	con = nib.load(op.join(path, 'stats', 'zstat1.nii.gz')).get_data()

	if load_func:
		func = nib.load(op.join(path, 'filtered_func_data.nii.gz')).get_data()
		return func, con
	else:
		return con

def standardize(func):
	return (func - func.mean(axis=-1, keepdims=True)) / func.std(axis=-1, keepdims=True)