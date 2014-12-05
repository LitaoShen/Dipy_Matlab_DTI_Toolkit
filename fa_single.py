import sys
import nibabel as nib
import scipy
from scipy import ndimage


img = nib.load(sys.argv[1])
data= img.get_data()
print(data.shape)

axial_middle = data.shape[2]/2
import matplotlib.pyplot as plt
import numpy as nib
from dipy.viz import fvtk

nimg= data[:,:,axial_middle,:]

plt.figure('Plot of Color FA Single Channel')
plt.subplot(2,2,1)
plt.imshow(data[:,:,axial_middle,0].T)
plt.subplot(2,2,2)
plt.imshow(data[:,:,axial_middle,1].T)
plt.subplot(2,2,3)
plt.imshow(data[:,:,axial_middle,2].T)
plt.savefig('cool.png',bbox_inches='tight')
plt.show()
