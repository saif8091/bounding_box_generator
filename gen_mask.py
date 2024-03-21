'''Mask generation code should be separate to account for 
differing morphological threshol and flight date'''
from func import *
from veg_indices import *

morph_win = 5

# directories
path_to_save = 'generated_mask//beet_mask_20230821.tif'
raster_path =  'data//20230821_30m.tif'

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
msa_mask = VI(multispec_wave,840,668).MSA(clipped_raster) > 0.35

### opening operation to remove small vegetation and smooth the boundaries
mask = xarray_morphological_opening(msa_mask,morph_win)

mask.astype(int).rio.to_raster(path_to_save)