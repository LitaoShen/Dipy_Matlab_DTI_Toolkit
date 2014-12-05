import sys
import nibabel as nib
import scipy
from scipy import ndimage
import matplotlib.pyplot as plt
import numpy as np

img = nib.load(sys.argv[1])
data= img.get_data()
print(data.shape)

axial_middle_x = data.shape[0]/2
axial_middle_y = data.shape[1]/2
axial_middle_z = data.shape[2]/2

nimg_x= data[axial_middle_x,:,:,:]
nimg_y= data[:,axial_middle_y,:,:]
nimg_z= data[:,:,axial_middle_z,:]
plt.imshow(nimg_z.transpose(1,0,2))

plt.figure('Plot of Color FA')
plt.subplot(2,2,1)
plt.imshow(nimg_z.transpose(1,0,2))
plt.subplot(2,2,2)
plt.imshow(nimg_x.transpose(1,0,2))
plt.subplot(2,2,3)
plt.imshow(nimg_y.transpose(1,0,2))
plt.show()

