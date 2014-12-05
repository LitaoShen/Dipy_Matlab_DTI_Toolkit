import sys
import numpy as np
from dipy.data import get_data

fbval='t0.bval'
fbvec='t0.bvec'



import nibabel as nib
img = nib.load('t0.nii.gz')
data = img.get_data()
print('data.shape (%d, %d, %d, %d)' % data.shape)

mask = data[..., 0] > 50

from dipy.io import read_bvals_bvecs
bvals, bvecs = read_bvals_bvecs(fbval, fbvec)

from dipy.core.gradients import gradient_table
gtab = gradient_table(bvals, bvecs)

from dipy.reconst.dti import TensorModel
ten = TensorModel(gtab)
tenfit = ten.fit(data,mask)

from dipy.reconst.dti import fractional_anisotropy
fa = fractional_anisotropy(tenfit.evals)
fa[np.isnan(fa)] = 0


from dipy.reconst.dti import color_fa
Rgbv = color_fa(fa, tenfit.evecs)


fa = np.clip(fa, 0,1)
#save FA to image

nib.save(nib.Nifti1Image(np.array(255*Rgbv,'uint8'),img.get_affine()),'tensor_rgb.nii.gz')

import matplotlib.pyplot as plt

axial_middle = data.shape[2] / 2
plt.figure('Showing the datasets')
plt.subplot(1, 2, 1).set_axis_off()
plt.imshow(data[:, :, axial_middle, 0].T, cmap='gray', origin='lower')
plt.subplot(1, 2, 2).set_axis_off()
plt.imshow(data[:, :, axial_middle, 10].T, cmap='gray', origin='lower')
plt.show()
plt.savefig('data.png', bbox_inches='tight')


from dipy.data import get_sphere
sphere = get_sphere('symmetric642')

from dipy.viz import fvtk
ren = fvtk.ren()

evals=tenfit.evals[55:85,80:90,40:45]
evecs=tenfit.evecs[55:85,80:90,40:45]

cfa = Rgbv[55:80, 80:90, 40:45]

#print cfa[1,1,1]
cfa /= cfa.max()

fvtk.add(ren, fvtk.tensor(evals, evecs, cfa))


fvtk.show(ren)
print('Saving illustration as fa.png')
fvtk.record(ren, n_frames=1, out_path='fa.png', size=(600, 600))
print "Hello World!"
