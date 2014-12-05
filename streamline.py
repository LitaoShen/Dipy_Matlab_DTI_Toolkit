import os
import sys
import numpy as np
import nibabel as nib

fa_img = nib.load(sys.argv[1])
FA = fa_img.get_data()
evecs_img = nib.load(sys.argv[2])
evecs =evecs_img.get_data()
FA[np.isnan(FA)] = 0

from dipy.data import get_sphere
sphere = get_sphere('symmetric724')
from dipy.reconst.dti import quantize_evecs
peak_indices = quantize_evecs(evecs,sphere.vertices)

from dipy.tracking.eudx import EuDX

eu = EuDX(FA.astype('f8'),peak_indices,seeds=50000,odf_vertices = sphere.vertices,a_low= 0.2)
tensor_streamlines =[streamline for streamline in eu]

hdr = nib.trackvis.empty_header()
hdr['voxel_size'] = fa_img.get_header().get_zooms()[:3]
hdr['voxel_order'] = 'LAS'
hdr['dim'] = FA.shape

tensor_streamlines_trk = ((sl,None, None) for sl in tensor_streamlines)
ten_sl_fname = sys.argv[3]+'_streamlines.trk'

nib.trackvis.write(ten_sl_fname, tensor_streamlines_trk, hdr, points_space='voxel')
from dipy.viz import fvtk
ren = fvtk.ren()
position_1=(5.35,59.07,362.79)
focal_point_1=(55.35,59.07,29.54)
viewup_1=(0.00,1.00,0.00)
camera1=fvtk.vtk.vtkCamera()
camera1.SetPosition(position_1)
camera1.SetFocalPoint(focal_point_1)

position_2=(50.35,59.07,362.79)
focal_point_2=(55.35,59.07,29.54)
viewup_2=(0.00,1.00,0.00)
camera2=fvtk.vtk.vtkCamera()
camera2.SetPosition(position_2)
camera2.SetFocalPoint(focal_point_2)
ren.SetActiveCamera(camera1)
ren.SetActiveCamera(camera2)
from dipy.viz.colormap import line_colors
fvtk.add(ren,fvtk.streamtube(tensor_streamlines, line_colors(tensor_streamlines)))
ren.SetBackground(1,1,1)
camera=fvtk.camera(ren)
fvtk.record(ren,n_frames=1, out_path=sys.argv[3]+'_tracks.png',size=(600,600))
fvtk.show(ren)
