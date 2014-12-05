import sys
import numpy as np
import nibabel as nib
import dipy.reconst.dti as dti
from dipy.core.gradients import gradient_table
from dipy.io import read_bvals_bvecs
fval = sys.argv[7]+'.bval'
fvec = sys.argv[7]+'.bvec'
bvals,bvecs = read_bvals_bvecs(fval,fvec)
fname = sys.argv[7]+'.nii.gz'
gtab=gradient_table(bvals,bvecs)
img=nib.load(fname)
data = img.get_data()
print('data.shape (%d, %d, %d, %d)' % data.shape)
x_f=int(sys.argv[1])
y_f=int(sys.argv[2])
z_f=int(sys.argv[3])
x_t=int(sys.argv[4])
y_t=int(sys.argv[5])
z_t=int(sys.argv[6])
mask = data[..., 0] > 50
tenmodel = dti.TensorModel(gtab)
print('Tensor fitting computation')
tenfit = tenmodel.fit(data, mask)
print('Computing anisotropy measures (FA, MD, RGB)')
from dipy.reconst.dti import fractional_anisotropy, color_fa, lower_triangular
FA = fractional_anisotropy(tenfit.evals)
FA[np.isnan(FA)] = 0
fa_img = nib.Nifti1Image(FA.astype(np.float32), img.get_affine())
nib.save(fa_img, sys.argv[7]+'_fa.nii.gz')
evecs_img = nib.Nifti1Image(tenfit.evecs.astype(np.float32), img.get_affine())
nib.save(evecs_img, sys.argv[7]+'_evecs.nii.gz')
MD1 = dti.mean_diffusivity(tenfit.evals)
nib.save(nib.Nifti1Image(MD1.astype(np.float32), img.get_affine()), sys.argv[7]+'_md.nii.gz')
MD2 = tenfit.md
FA = np.clip(FA, 0, 1)
RGB = color_fa(FA, tenfit.evecs)
nib.save(nib.Nifti1Image(np.array(255 * RGB, 'uint8'), img.get_affine()), sys.argv[7]+'_rgb.nii.gz')
print('Computing tensor ellipsoids in a part of the splenium of the CC')
from dipy.data import get_sphere
sphere = get_sphere('symmetric724')

from dipy.viz import fvtk
ren = fvtk.ren()

evals = tenfit.evals[x_f:x_t,y_f:y_t, z_f:z_t]
evecs = tenfit.evecs[x_f:x_t,y_f:y_t, z_f:z_t]

cfa = RGB[x_f:x_t,y_f:y_t, z_f:z_t]
cfa /= (cfa.max()+0.0000000001)

fvtk.add(ren, fvtk.tensor(evals, evecs, cfa, sphere))

fvtk.show(ren)

print('Saving illustration as tensor_ellipsoids.png')
fvtk.record(ren, n_frames=1, out_path='tensor_ellipsoids.png', size=(600, 600))
fvtk.clear(ren)
tensor_odfs = tenmodel.fit(data[x_f:x_t,y_f:y_t, z_f:z_t]).odf(sphere)
fvtk.add(ren, fvtk.sphere_funcs(tensor_odfs, sphere, colormap=None))
fvtk.show(ren)
print('Saving illustration as tensor_odfs.png')
fvtk.record(ren, n_frames=1, out_path='tensor_odfs.png', size=(600, 600))
