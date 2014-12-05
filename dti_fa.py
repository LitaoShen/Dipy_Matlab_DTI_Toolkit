from dipy.data import get_data
fimg,fbval,fbvec = get_data('small_101D')

import numpy as np

import nibabel as nib
img = nib.load(fimg)
data = img.get_data()

from dipy.io import read_bvals_bvecs
bvals,bvecs = read_bvals_bvecs(fbval,fbvec)

from dipy.core.gradients import gradient_table
gtab = gradient_table(bvals,bvecs)

from dipy.reconst.dti import TensorModel
ten = TensorModel(gtab)
tenfit = ten.fit(data)

from dipy.reconst.dti import fractional_anisotropy
fa = fractional_anisotropy(tenfit.evals)

from dipy.reconst.dti import color_fa
cfa = color_fa(fa,tenfit.evecs)

#save FA to image

nib.save(nib.Nifti1Image(np.array(255*cfa,'uint8'),img.get_affine()),'tensor_rgb.nii.gz')
from dipy.data import get_sphere
sphere = get_sphere('symmetric724')

from dipy.viz import fvtk
ren = fvtk.ren()

evals=tenfit.evals[20:50,55:85,38:39]
evecs=tenfit.evecs[20:50,55:85,38:39]


print "Hello World!"