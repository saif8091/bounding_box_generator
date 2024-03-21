'''Functions required for bounding boxes'''
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
import geopandas as gpd
import rioxarray 
import os
from skimage import morphology
import xarray as xr
from skimage import measure
from shapely.geometry import box
from tqdm import tqdm

multispec_wave = np.array([560, 650, 730, 860])

def xarray_morphological_opening(mask,disk_shape=9):
    '''This functionensures that the returned array is an xarray'''
    xmask = morphology.opening(mask,morphology.disk(disk_shape))
    return xr.DataArray(xmask,dims=mask.dims, coords=mask.coords)

def gen_bboxes_single_row(binary_xarray, height, width,area_thres):
    '''This function generates bounding boxes for single row'''

    # Label connected components in the binary image
    labeled_image, num_labels = measure.label(binary_xarray,return_num=True)
    # for calculating area of each labels
    prop = measure.regionprops(labeled_image)

    # Extract coordinates from the xarray
    x_coords = binary_xarray.coords['x'].values
    y_coords = binary_xarray.coords['y'].values

    # Create a list to store bounding boxes
    bounding_boxes = []

    # Iterate over each labeled component
    for label in range(1, num_labels + 1):
        
        #ensure the area is above threshold
        if prop[label-1].area > area_thres:

            # Find the coordinates of the labeled component
            component_coords = np.column_stack(np.where(labeled_image == label))

            # Create a bounding box centered around the labeled component
            centroid_x = int(component_coords[:, 1].mean())
            centroid_y = int(component_coords[:, 0].mean())

            # Get the corresponding coordinates in the xarray
            center_x_coord = x_coords[centroid_x]
            center_y_coord = y_coords.mean()  # this code ensures that y encapsulates the entire row
            #center_y_coord = y_coords[centroid_y] # use this one instead if you want vegetation only box

            # Expand the bounding box based on user-defined length and width
            min_x_coord = center_x_coord - width / 2
            max_x_coord = center_x_coord + width / 2
            min_y_coord = center_y_coord - height / 2
            max_y_coord = center_y_coord + height / 2

            # Create a Shapely bounding box
            bounding_box = box(min_x_coord, min_y_coord, max_x_coord, max_y_coord)

            # Append the bounding box to the list
            bounding_boxes.append(bounding_box)
    return bounding_boxes

def gen_bbox_mask(binary_xarray,height,width,area_thres=500):
    '''This function generates bounding boxes given binary mask (in xarray), 
    height and width (in meters) of the box, the ouput is in geopandas dataframe
    
    '''

    # Extract coordinates from the xarray
    y_coords = binary_xarray.coords['y'].values

    # Create a list to store bounding boxes
    bounding_boxes = []

    # split image according to height:
    y_top = y_coords.max()
    pbar = tqdm(total=int((y_coords.max()-y_coords.min())/height), desc='Scanning rows')
    
    while(y_top>=y_coords.min()+height):
        # slice y values within a height
        sliced_xarray = binary_xarray.sel(y=slice(y_top,y_top-height))
        bounding_boxes.append(gen_bboxes_single_row(sliced_xarray,height,width,area_thres))
        # find the next y_top coordinate
        y_top -= height
        pbar.update(1)
    pbar.close()
    # Flatten the list using list comprehension
    bounding_boxes = [item for sublist in bounding_boxes for item in sublist]
    # Create a GeoDataFrame from the list of bounding boxes
    gdf = gpd.GeoDataFrame(geometry=bounding_boxes, crs=binary_xarray.rio.crs)
    return gdf