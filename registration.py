import sys
import numpy as np
import nibabel as nib
import pyximport; pyximport.install()
import dipy.reconst.dti as dti
from dipy.core.gradients import gradient_table
from dipy.io import read_bvals_bvecs
import matplotlib.pyplot as plt
from dipy.align.imwarp import SymmetricDiffeomorphicRegistration
from dipy.align.imwarp import DiffeomorphicMap
from dipy.align.metrics import CCMetric
import os.path
from dipy.viz import regtools


fval = sys.argv[7]+'.bval'
fvec = sys.argv[7]+'.bvec'
bvals,bvecs = read_bvals_bvecs(fval,fvec)
fname = sys.argv[7]+'.nii.gz'
gtab=gradient_table(bvals,bvecs)
img=nib.load(fname)
data = img.get_data()
data_b0=np.squeeze(data)[...,0]

from dipy.data.fetcher import fetch_syn_data, read_syn_data
fetch_syn_data()
nib_syn_t1, nib_syn_b0 = read_syn_data()
syn_b0 = np.array(nib_syn_b0.get_data())

from dipy.segment.mask import median_otsu
data_b0_masked, data_b0_mask = median_otsu(data_b0, 4, 4)
syn_b0_masked, syn_b0_mask = median_otsu(syn_b0, 4, 4)

static = data_b0_masked
static_affine = nib_stanford.get_affine()
moving = syn_b0_masked
moving_affine = nib_syn_b0.get_affine()

pre_align = np.array([[1.02783543e+00, -4.83019053e-02, -6.07735639e-02, -2.57654118e+00],
                      [4.34051706e-03, 9.41918267e-01, -2.66525861e-01, 3.23579799e+01],
                      [5.34288908e-02, 2.90262026e-01, 9.80820307e-01, -1.46216651e+01],
                      [0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
import dipy.align.vector_fields as vfu

transform = np.linalg.inv(moving_affine).dot(pre_align.dot(static_affine))
resampled = vfu.warp_3d_affine(moving.astype(np.float32),
                                   np.asarray(static.shape, dtype=np.int32),
                                   transform)
resampled = np.asarray(resampled)

regtools.overlay_slices(static, resampled, None, 1, 'Static', 'Moving', 'input_3d.png')
