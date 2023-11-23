'''Mask generation code should be separate to account for 
differing morphological threshol and flight date'''
from func import *
from veg_indices import *

morph_win = 7

# directories
path_to_save = 'generated_mask//beet_mask_20210720.tif'
raster_path =  'data//20210720_1304_multispec_4.tif'

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

mask.astype(int).rio.to_raster(path_to_save)