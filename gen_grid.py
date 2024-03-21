from func import *
from veg_indices import *

### box geometry in m
height = 1.5
width = 0.75

### area thresholding
area_thres = 200
morph_win = 5

# directories
path_to_save = 'generated_grid//2023_grid_20230802.gpkg'
raster_path =  'data//20230802_30m_corrected.tif'

# coordinates starts from northwest and goes clockwise
geometries = [
    {
        'type': 'Polygon',
        'coordinates': [[
            [334520.38,4749227.91],
            [334577.46,4749217.20],
            [334580.56,4749109.64],
            [334523.35,4749107.87]
        ]]
    }
]

### Loading raster
print('loading raster')
raster = rioxarray.open_rasterio(raster_path, masked = True)

### Clipping to the extent
print('clipping raster')
clipped_raster = raster.rio.clip(geometries)

### Generating vegetation mask change as required
msa_mask = VI(multispec_wave,840,668).MSA(clipped_raster) > 0.40

### opening operation to remove small vegetation and smooth the boundaries
mask = xarray_morphological_opening(msa_mask,morph_win)

### Generate the bounding boxes
gdf_bbox = gen_bbox_mask(mask,height,width,area_thres)

gdf_bbox.to_file(path_to_save, driver='GPKG', layer='20230802')

### Plot
fig, ax = plt.subplots(figsize=(10, 8))
clipped_raster[[2,1,0]].plot.imshow(robust=True, ax=ax)
gdf_bbox.boundary.plot(ax=ax,color='red',linewidth=2)
plt.show()