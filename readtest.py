import os
import sys
import numpy as np
import nibabel as nib
from dipy.reconst.dti import TensorModel, fractional_anisotropy
from dipy.reconst.csdeconv import (ConstrainedSphericalDeconvModel,
                                 auto_response)
from dipy.reconst.peaks import peaks_from_model
from dipy.tracking.eudx import EuDX
from dipy.data import get_sphere
from dipy.segment.mask import median_otsu
from dipy.viz import fvtk
from dipy.viz.colormap import line_colors
from dipy.core.gradients import gradient_table
from dipy.io import read_bvals_bvecs
fval = sys.argv[1]+'.bval'
fvec = sys.argv[1]+'.bvec'
bvals,bvecs = read_bvals_bvecs(fval,fvec)
fname = sys.argv[1]+'.nii.gz'
gtab=gradient_table(bvals,bvecs)
img=nib.load(fname)
data = img.get_data()
maskdata, mask = median_otsu(data, 3, 1, False,
                           vol_idx=range(10, 50), dilate=2)
response, ratio = auto_response(gtab, data, roi_radius=10, fa_thr=0.7)

csd_model = ConstrainedSphericalDeconvModel(gtab, response)
sphere = get_sphere('symmetric724')
