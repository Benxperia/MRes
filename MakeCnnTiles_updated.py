from osgeo import gdal, ogr
from qgis.core import QgsVectorLayer, QgsProject
import numpy as np
import os
import matplotlib.pyplot as plt
import glob
import random

# User-specified chip dimensions, raster file path and folder
chip_width = 32
chip_height = 32
output_folder = "C:\\Users\\benjs\\OneDrive - Durham University\\MRes\\Data\\Secondary Data\\Land Cover\\LScomp_Imagery\\2016\\Tiles_v2\\"
vector_file_path = "C:\\Users\\benjs\\OneDrive - Durham University\\MRes\\Data\\Secondary Data\\Land Cover\\LScomp_Imagery\\2016\\Regrouped\\Points\\Wetland_DN_90_95.gpkg"
raster_file_path = "C:\\Users\\benjs\\OneDrive - Durham University\\MRes\\Data\\Secondary Data\\Land Cover\\LScomp_Imagery\\2016\\Train\\TRV_Basin_LScomp2016_train.tif"

# Custom file name prefix (change this for each run)
file_prefix = "Wetland"

# Function to read pixel values from a GeoTiff raster layer
def read_pixel_values(raster_ds, x, y, chip_width, chip_height):
    geotransform = raster_ds.GetGeoTransform()
    origin_x = geotransform[0]
    origin_y = geotransform[3]
    pixel_width = geotransform[1]
    pixel_height = geotransform[5]
    
    # Get raster dimensions
    raster_width = raster_ds.RasterXSize
    raster_height = raster_ds.RasterYSize
    
    # Calculate top-left corner of the chip
    px = int((x - origin_x) / pixel_width) - chip_width // 2
    py = int((y - origin_y) / pixel_height) - chip_height // 2
    print(f"Pixel coordinates: ({px}, {py})")
    
    # Check if the entire chip is within raster bounds
    if (px >= 0 and py >= 0 and 
        px + chip_width <= raster_width and 
        py + chip_height <= raster_height):
        
        data = raster_ds.ReadAsArray(px, py, chip_width, chip_height)
        return np.transpose(data, (1, 2, 0))
    else:
        print(f"Chip out of bounds: px={px}, py={py}, " +
              f"raster size=({raster_width}, {raster_height})")
        return -1 * np.ones((chip_height, chip_width, 1))

# Function to save a chip image as a NumPy array
def save_chip(image, folder_path, image_id, prefix):
    if np.amin(image) >= 0:
        file_name = folder_path + prefix + f'_{image_id:06d}.npy'
        np.save(file_name, image)
        return True
    return False

# Ensure the output folder exists
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Get raster data source
raster_ds = gdal.Open(raster_file_path, gdal.GA_ReadOnly)

# Load the vector layer from the gpkg file
vector_layer = QgsVectorLayer(vector_file_path, "vector_layer", "ogr")

# Track statistics
total_features = 0
saved_chips = 0

# Loop through each feature in the vector layer
for i, feature in enumerate(vector_layer.getFeatures()):
    geometry = feature.geometry()
    x, y = geometry.asPoint().x(), geometry.asPoint().y()
    total_features += 1
    print(f"\nProcessing feature {i}: ({x}, {y})")
    
    # Read corresponding pixel values from the raster layer
    chip = read_pixel_values(raster_ds, x, y, chip_width, chip_height)
    
    # Save the chip as a numpy array
    if save_chip(chip, output_folder, i, file_prefix):
        saved_chips += 1

print(f"\nProcessed {total_features} features, saved {saved_chips} valid chips")

# Randomly select 16 chips and display them
saved_files = glob.glob(output_folder + '\\' + file_prefix + '*.npy')

if len(saved_files) >= 16:
    selected_files = random.sample(saved_files, 16)
else:
    print(f"Only {len(saved_files)} chips available (requested 16).")
    selected_files = saved_files

if selected_files:
    fig, axes = plt.subplots(4, 4, figsize=(9, 9))
    
    for ax, file_name in zip(axes.flatten(), selected_files):
        image_path = os.path.join(output_folder, file_name)
        image = np.load(image_path)
        
        # Select specific bands for visualization (e.g., bands 5, 3, 2 for false color)
        rgb = image[:, :, [5, 3, 2]]  # Adjust band indices as needed
        
        # Normalize to 0-1 range for display
        # Use 2nd and 98th percentile for better contrast
        p2, p98 = np.percentile(rgb, (2, 98))
        rgb_normalized = np.clip((rgb - p2) / (p98 - p2), 0, 1)
        
        ax.imshow(rgb_normalized)
        ax.axis('off')
        ax.set_title(os.path.basename(file_name), fontsize=8)
    
    plt.tight_layout()
    plt.show()
else:
    print("No valid chips were created to display.")