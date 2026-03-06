import processing
from qgis.core import QgsProject

# Stage 1: Random sample
print("Stage 1: Random sampling...")
result1 = processing.run("native:randomextract", {
    'INPUT': 'DN_11',  # Change this to your layer name if different
    'METHOD': 0,
    'NUMBER': 50000,  # Adjust number as needed
    'OUTPUT': 'memory:temp'
})

print(f"Sampled {result1['OUTPUT'].featureCount()} points")

# Stage 2: Sample raster values
print("Stage 2: Sampling raster values...")
result2 = processing.run("native:rastersampling", {
    'INPUT': result1['OUTPUT'],
    'RASTERCOPY': 'TRV_Basin_LScomp_2016_merge',  # Change to your raster name if different
    'COLUMN_PREFIX': 'b_',
    'OUTPUT': 'C:/Users/benjs/OneDrive - Durham University/MRes/Data/Secondary Data/Land Cover/LScomp_Imagery/2016/Merge/Centroids/DN_11_ndv2.gpkg'  # CHANGE THIS PATH
})


print("Done! Layer added to map.")
print("Now open attribute table and use Select by Expression:")
print('Expression: "b_1" IS NOT NULL AND "b_1" != 0')
```

### **4. Update the Paths**
Before running, you need to change:
- **Line 6**: `'INPUT': 'DN_11'` - Make sure this matches your points layer name exactly
- **Line 15**: `'RASTERCOPY': 'TRV_Basin_LScomp_2016_merge'` - Make sure this matches your raster layer name exactly
- **Line 17**: Update the output path to where you want to save the file (use forward slashes `/` or double backslashes `\\`)

### **5. Run the Code**
- Click the **green "Run Script"** button in the editor toolbar (or press `Ctrl+Alt+R`)
- Watch the console for progress messages

### **6. Filter the Results**
Once it finishes:
1. The new layer will appear in your Layers panel
2. Right-click it → **Open Attribute Table**
3. Click the **Select features using an expression** button (ε icon)
4. Enter: `"b_1" IS NOT NULL AND "b_1" != 0`
5. Click **Select Features**
6. In the attribute table, choose **Show Selected Features** from the dropdown
7. Right-click the layer → **Export → Save Selected Features As...**
8. Save as your final cleaned points file