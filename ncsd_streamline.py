import os
import sys
import numpy as np
import nibabel as nib
from multiprocessing import freeze_support
from dipy.reconst.dti import TensorModel, fractional_anisotropy
from dipy.reconst.csdeconv import (ConstrainedSphericalDeconvModel,
                                 auto_response)
from dipy.reconst.peaks import peaks_from_model
from dipy.tracking.eudx import EuDX
from dipy.data import fetch_stanford_hardi, read_stanford_hardi, get_sphere
from dipy.segment.mask import median_otsu
from dipy.viz import fvtk
from dipy.viz.colormap import line_colors
from dipy.core.gradients import gradient_table
from dipy.io import read_bvals_bvecs
#fetch_stanford_hardi()
if __name__ == '__main__':
                   freeze_support()
img, gtab = read_stanford_hardi()

data = img.get_data()
maskdata, mask = median_otsu(data, 3, 1, False,
                           vol_idx=range(10, 50), dilate=2)
response, ratio = auto_response(gtab, data, roi_radius=10, fa_thr=0.7)

csd_model = ConstrainedSphericalDeconvModel(gtab, response)
sphere = get_sphere('symmetric724')

csd_peaks = peaks_from_model(model=csd_model,
                           data=data,
                           sphere=sphere,
                           mask=mask,
                           relative_peak_threshold=.5,
                           min_separation_angle=25,
                           parallel=True)
tensor_model = TensorModel(gtab, fit_method='WLS')
tensor_fit = tensor_model.fit(data, mask)

FA = fractional_anisotropy(tensor_fit.evals)
stopping_values = np.zeros(csd_peaks.peak_values.shape)
stopping_values[:] = FA[..., None]
ren = fvtk.ren()

slice_no = data.shape[2] / 2

fvtk.add(ren, fvtk.peaks(csd_peaks.peak_dirs[:, :, slice_no:slice_no + 1],
                       stopping_values[:, :, slice_no:slice_no + 1]))

print('Saving illustration as csd_direction_field.png')
fvtk.record(ren, out_path=sys.argv[1]+'_csd_direction_field.png', size=(900, 900))
streamline_generator = EuDX(stopping_values,
                          csd_peaks.peak_indices,
                          seeds=10**4,
                          odf_vertices=sphere.vertices,
                          a_low=0.1)

streamlines = [streamline for streamline in streamline_generator]
fvtk.clear(ren)

fvtk.add(ren, fvtk.line(streamlines, line_colors(streamlines)))

print('Saving illustration as csd_streamlines_eudx.png')
fvtk.record(ren, out_path=sys.argv[1]+'_csd_streamlines_eudx.png', size=(900, 900))

hdr = nib.trackvis.empty_header()
hdr['voxel_size'] = img.get_header().get_zooms()[:3]
hdr['voxel_order'] = 'LAS'
hdr['dim'] = FA.shape[:3]

csd_streamlines_trk = ((sl, None, None) for sl in streamlines)

csd_sl_fname = 'csd_streamline.trk'

nib.trackvis.write(csd_sl_fname, csd_streamlines_trk, hdr, points_space='voxel')

nib.save(nib.Nifti1Image(FA, img.get_affine()), 'FA_map.nii.gz')
