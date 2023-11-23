from func import *
from veg_indices import *

### box geometry in m
height = 1.5
width = 0.75

### area thresholding
area_thres = 1000
morph_win = 11

# directories
path_to_save = 'generated_grid//test.gpkg'
raster_path =  'data//20220707_3rd_micasense_1601.tif'

# coordinates starts from northwest and goes clockwise
geometries = [
    {
        'type': 'Polygon',
        'coordinates': [[
            [334187, 4.749073e6],
            [334222, 4.749073e6],
            [334253, 4.749000e6],
            [334258, 4.748965e6],
            [334195, 4.748960e6]
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
msa_mask = VI(multispec_wave,840,668).MSA(clipped_raster) > 0.25

### opening operation to remove small vegetation and smooth the boundaries
mask = xarray_morphological_opening(msa_mask,morph_win)

### Generate the bounding boxes
gdf_bbox = gen_bbox_mask(mask,height,width,area_thres)

gdf_bbox.to_file(path_to_save, driver='GPKG', layer='test')

### Plot
fig, ax = plt.subplots(figsize=(10, 8))
clipped_raster[[2,1,0]].plot.imshow(robust=True, ax=ax)
gdf_bbox.boundary.plot(ax=ax,color='red',linewidth=2)
plt.show()