from osgeo import gdal, ogr
from qgis.core import QgsVectorLayer, QgsProject
import numpy as np
import os
import matplotlib.pyplot as plt
import glob
import random
import gc  # Garbage collector

# User-specified chip dimensions, raster file path and folder
chip_width = 100
chip_height = 100
output_folder = "C:\\Users\\benjs\\OneDrive - Durham University\\MRes\\Data\\Secondary Data\\Land Cover\\LScomp_Imagery\\2016\\Tiles\\"
vector_file_path = "C:\\Users\\benjs\\OneDrive - Durham University\\MRes\\Data\\Secondary Data\\Land Cover\\LScomp_Imagery\\2016\\Train\\Point Data\\Train_Centroid2_DN_11 Open Water.gpkg"
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
    
    if px > 0 and py > 0:
        try:
            data = raster_ds.ReadAsArray(px, py, chip_width, chip_height)
            if data is None or data.size == 0:
                return None
            # Check for NoData values (usually 0 in Landsat)
            if np.any(data == 0):  # Has NoData pixels
                return None
            return np.transpose(data, (1, 2, 0))
        except:
            return None
    else:
        return None

# Function to save a chip image as a NumPy array
def save_chip(image, folder_path, image_id):
    if image is not None and np.amin(image) >= 0:
        root = os.path.basename(vector_file_path)[:-6]
        file_name = folder_path + root + f'_{image_id:06d}.npy'
        np.save(file_name, image)
        return True
    return False

# Ensure the output folder exists
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Get raster data source
raster_ds = gdal.Open(raster_file_path, gdal.GA_ReadOnly)

# Load the vector layer
vector_layer = QgsVectorLayer(vector_file_path, "vector_layer", "ogr")

# Count total features
total_features = vector_layer.featureCount()
print(f"Total points to process: {total_features}")

# Process with batch clearing and progress
batch_size = 1000  # Process 1000 at a time
saved_count = 0
processed_count = 0

for i, feature in enumerate(vector_layer.getFeatures()):
    geometry = feature.geometry()
    x, y = geometry.asPoint().x(), geometry.asPoint().y()
    
    # Read corresponding pixel values from the raster layer
    chip = read_pixel_values(raster_ds, x, y, chip_width, chip_height)
    
    # Save the chip as a numpy array
    if save_chip(chip, output_folder, i):
        saved_count += 1
    
    processed_count += 1
    
    # Progress update and memory cleanup every batch
    if processed_count % batch_size == 0:
        print(f"Processed: {processed_count}/{total_features} | Saved: {saved_count}")
        gc.collect()  # Force garbage collection
        
    # Optional: Stop after certain number to test
    # if processed_count >= 5000:
    #     break

print(f"Complete! Processed: {processed_count} | Saved: {saved_count}")

# Close raster
raster_ds = None

# Randomly select 16 chips and display them
root = os.path.basename(vector_file_path)[:-6]
saved_files = glob.glob(output_folder + root + '*.npy')

if len(saved_files) >= 16:
    selected_files = random.sample(saved_files, 16)
else:
    print(f"Only {len(saved_files)} chips available.")
    selected_files = saved_files

if selected_files:
    fig, axes = plt.subplots(4, 4, figsize=(9, 9))
    
    for ax, file_name in zip(axes.flatten(), selected_files):
        try:
            image = np.load(file_name)
            ax.imshow(image[:,:,0:3])  # Show RGB bands if available
            ax.axis('off')
            ax.set_title(os.path.basename(file_name)[-15:])
        except:
            ax.axis('off')
    
    plt.tight_layout()
    plt.show()