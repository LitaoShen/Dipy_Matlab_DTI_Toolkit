import sys
import nibabel as nib
import scipy
import matplotlib.pyplot as plt

img = nib.load(sys.argv[1])
data = img.get_data()
print(data.shape)

axial_middle_x = data.shape[0]/2
axial_middle_y = data.shape[1]/2
axial_middle_z = data.shape[2]/2

plt.figure('MD Value')
plt.subplot(2,2,1).set_axis_off()
plt.imshow(data[:,:,axial_middle_z].T, cmap='gray')
plt.subplot(2,2,2).set_axis_off()
plt.imshow(data[axial_middle_x,:,:].T.T, cmap='gray')
plt.subplot(2,2,3).set_axis_off()
plt.imshow(data[:,axial_middle_y,:].T.T.T, cmap='gray')
plt.show()
