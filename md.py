import nibabel as nib
import scipy
import matplotlib.pyplot as plt

img = nib.load('tensors_md.nii.gz')
data = img.get_data()
print(data.shape)

plt.figure('MD Value')
plt.subplot(2,2,1).set_axis_off()
plt.imshow(data[:,:,38].T)
plt.subplot(2,2,2).set_axis_off()
plt.imshow(data[40,:,:])
plt.subplot(2,2,3).set_axis_off()
plt.imshow(data[:,83,:].T)
plt.show()
