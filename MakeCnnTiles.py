from osgeo import gdal, ogr
from qgis.core import QgsVectorLayer, QgsProject
import numpy as np
import os
import matplotlib.pyplot as plt
import glob
import random

# User-specified chip dimensions, raster file path and folder
chip_width = 100
chip_height = 100
output_folder = "C:\\Users\\benjs\\OneDrive - Durham University\\MRes\\Data\\Secondary Data\\Land Cover\\LScomp_Imagery\\2016\\Tiles\\"
vector_file_path = "C:\\Users\\benjs\\OneDrive - Durham University\\MRes\\Data\\Secondary Data\\Land Cover\\LScomp_Imagery\\2016\\Train\\Point Data\\Train_Centroid_DN_41.gpkg"
raster_file_path = "C:\\Users\\benjs\\OneDrive - Durham University\\MRes\\Data\\Secondary Data\\Land Cover\\LScomp_Imagery\\2016\\Train\\TRV_Basin_LScomp2016_train.tif"

# Function to read pixel values from a GeoTiff raster layer
def read_pixel_values(raster_ds, x, y, chip_width, chip_height):
    geotransform = raster_ds.GetGeoTransform()
    origin_x = geotransform[0]
    origin_y = geotransform[3]
    pixel_width = geotransform[1]
    pixel_height = geotransform[5]
    
    px = int((x - origin_x) / pixel_width) - chip_width // 2
    py = int((y - origin_y) / pixel_height) - chip_height // 2
    print(px)
    print(py)
    
    if px>0 and py>0:
        data = raster_ds.ReadAsArray(px, py, chip_width, chip_height)
    else:
        data= -1*np.ones((1,1,1))
    
    
    return np.transpose(data, (1, 2, 0))

# Function to save a chip image as a NumPy array
def save_chip(image, folder_path, image_id):
    if np.amin(image)>=0:
        root=os.path.basename(vector_file_path)[:-6]
        file_name = folder_path +root+f'_{image_id:06d}.npy'
        np.save(file_name, image)




# Ensure the output folder exists
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Get raster data source
raster_ds = gdal.Open(raster_file_path, gdal.GA_ReadOnly)

# Load the vector layer from the gpkg file
vector_layer = QgsVectorLayer(vector_file_path, "vector_layer", "ogr")
#QgsProject.instance().addMapLayer(vector_layer)

# Loop through each feature in the vector layer
for i, feature in enumerate(vector_layer.getFeatures()):
    geometry = feature.geometry()
    x, y = geometry.asPoint().x(), geometry.asPoint().y()
    print(x)
    print(y)
    
    # Read corresponding pixel values from the raster layer
    chip = read_pixel_values(raster_ds, x, y, chip_width, chip_height)
    
    # Save the chip as a numpy array
    save_chip(chip, output_folder, i)

# Randomly select 9 chips and display them
root=os.path.basename(vector_file_path)[:-6]
saved_files=glob.glob(output_folder+'\\'+root+'*.npy')
if len(saved_files) >= 16:
    selected_files = random.sample(saved_files, 16)
else:
    print("Not enough chips to display.")
    selected_files = saved_files

fig, axes = plt.subplots(4, 4, figsize=(9, 9))

for ax, file_name in zip(axes.flatten(), selected_files):
    image_path = os.path.join(output_folder, file_name)
    image = np.load(image_path)
    
    # Select specific bands for visualization (e.g., bands 4, 3, 2 for false color)
    rgb = image[:, :, [5, 3, 2]]  # Adjust band indices as needed
    ax.imshow(rgb)
    ax.axis('off')
    ax.set_title(os.path.basename(file_name))

plt.tight_layout()
plt.show()