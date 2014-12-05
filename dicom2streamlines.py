#!/usr/bin/env python

# Convert dicom 2 nrrd
def dicom2nrrd(dicomdir, out_prefix):
    import os
    from nipype.interfaces.base import CommandLine
    cmd = CommandLine('DWIConvert --inputDicomDirectory %s --outputVolume %s.nrrd' % (dicomdir, out_prefix))
    cmd.run()
    return os.path.abspath('%s.nrrd' % out_prefix)

# run through DTIPrep
def dtiprep(in_file):
    from glob import glob
    import os
    from nipype.interfaces.base import CommandLine
    cmd = CommandLine('DTIPrep -w %s -c -d -p default.xml' % in_file)
    cmd.run()
    
    qcfile = os.path.abspath(glob('*QC*nrrd')[0])
    xmlfile = os.path.abspath(glob('*QC*xml')[0])
    sumfile = os.path.abspath(glob('*QC*txt')[0])
    
    return qcfile, xmlfile, sumfile

# convert nrrd to Nifti
def nrrd2nii(in_file):
    from os.path import abspath as opap
    from nipype.interfaces.base import CommandLine
    from nipype.utils.filemanip import split_filename
    _, name, _ = split_filename(in_file)
    out_vol = '%s.nii.gz' % name
    out_bval = '%s.bval' % name
    out_bvec = '%s.bvec' % name
    cmd = CommandLine(('DWIConvert --inputVolume %s --outputVolume %s --outputBValues %s'
                       ' --outputBVectors %s --conversionMode NrrdToFSL') % (in_file, out_vol,
                                                                             out_bval, out_bvec))
    cmd.run()    
    return opap(out_vol), opap(out_bval), opap(out_bvec)

def correctbvec4fsl(dwifile, bvec):
    import nibabel as nib
    import numpy as np
    from nipype.utils.filemanip import split_filename

    aff = nib.load(dwifile).get_affine()[:3, :3]
    for i in range(10):
        #aff = aff.dot(np.linalg.inv(np.eye(3) + 3*aff.T.dot(aff)).dot(3*np.eye(3) + aff.T.dot(aff)))
        aff = 0.5 * (aff + np.linalg.inv(aff.T))
    mat = np.dot(aff, np.array([[1,0,0],[0,1,0],[0,0,-1]])) # DTIPrep output in nifti
    bvecs = np.genfromtxt(bvec)
    if bvecs.shape[1] != 3:
        bvecs = bvecs.T
    bvecs = mat.dot(bvecs.T).T
    outfile = '%s_forfsl.bvec' % split_filename(bvec)[1]
    np.savetxt(outfile, bvecs, '%.17g %.17g %.17g')
    return outfile

def runbet(dwifile):
    from nipype.interfaces.fsl import BET
    res = BET(in_file=dwifile, frac=0.15, mask=True).run()
    return res.outputs.mask_file

# generate streamlines
def nii2streamlines(imgfile, maskfile, bvals, bvecs):
    import numpy as np
    import nibabel as nib
    import os
    
    from dipy.reconst.dti import TensorModel
    
    img = nib.load(imgfile)
    bvals = np.genfromtxt(bvals)
    bvecs = np.genfromtxt(bvecs)
    if bvecs.shape[1] != 3:
        bvecs = bvecs.T

    from nipype.utils.filemanip import split_filename
    _, prefix, _  = split_filename(imgfile)
    
    from dipy.data import gradient_table
    
    gtab = gradient_table(bvals, bvecs)
    data = img.get_data()
    affine = img.get_affine()
    zooms = img.get_header().get_zooms()[:3]
    new_zooms = (2., 2., 2.)
    data2, affine2 = data, affine
    mask = nib.load(maskfile).get_data().astype(np.bool)
    tenmodel = TensorModel(gtab)
    tenfit = tenmodel.fit(data2, mask)
    
    from dipy.reconst.dti import fractional_anisotropy
    FA = fractional_anisotropy(tenfit.evals)
    FA[np.isnan(FA)] = 0
    fa_img = nib.Nifti1Image(FA, img.get_affine())
    nib.save(fa_img, '%s_tensor_fa.nii.gz' % prefix)
    
    evecs = tenfit.evecs
    
    evec_img = nib.Nifti1Image(evecs, img.get_affine())
    nib.save(evec_img, '%s_tensor_evec.nii.gz' % prefix)
    
    from dipy.data import get_sphere
    sphere = get_sphere('symmetric724')
    from dipy.reconst.dti import quantize_evecs
    
    peak_indices = quantize_evecs(tenfit.evecs, sphere.vertices)
    
    from dipy.tracking.eudx import EuDX
    
    eu = EuDX(FA, peak_indices, odf_vertices = sphere.vertices, a_low=0.2, seeds=10**6, ang_thr=35)
    tensor_streamlines = [streamline for streamline in eu]
    
    hdr = nib.trackvis.empty_header()
    hdr['voxel_size'] = new_zooms
    hdr['voxel_order'] = 'LPS'
    hdr['dim'] = data2.shape[:3]
    
    import dipy.tracking.metrics as dmetrics
    tensor_streamlines = ((sl, None, None) for sl in tensor_streamlines if dmetrics.length(sl) > 15)
    
    ten_sl_fname = '%s_streamline.trk' % prefix
    
    nib.trackvis.write(ten_sl_fname, tensor_streamlines, hdr, points_space='voxel')
    return ten_sl_fname

from argparse import ArgumentParser
if __name__ == "__main__":
     parser = ArgumentParser()
     parser.add_argument("--dicomdir", dest="dicomdir", help="dicomdir", required=True)
     parser.add_argument("--subject", dest="subject", help="subject id", required=True)
     args = parser.parse_args()
     
     out_file = dicom2nrrd(args.dicomdir, args.subject)
     qcfile, _, _ = dtiprep(out_file)
     dwifile, bval_file, bvec_file = nrrd2nii(qcfile)
     corr_bvec = correctbvec4fsl(dwifile, bvec_file)
     mask_file = runbet(dwifile)
     nii2streamlines(dwifile, mask_file, bval_file, corr_bvec)
     