import os.path as op
import nibabel as nib


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


def load_data(dataset, contrast):

	mappings = {'action': 'Cope1',
	            'interoception': 'Cope2',
	            'situation': 'Cope3',
	            'action>interoception': 'Cope4',
	            'action>situation': 'Cope5',
	            'interoception>situation': 'Cope6'}
	contrast = mappings[contrast]
	
	path = op.join(dataset, contrast + '.gfeat')
	func = nib.load(op.join(path, 'filtered_func_data.nii.gz')).get_data()
	con = nib.load(op.join(path, 'stats', 'zstat1.nii.gz')).get_data()

	return func, con 