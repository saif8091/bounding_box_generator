# Generate a grid of bounding boxes

## Running
edit gen_grid.py to get an array of bounding boxes stored as .gpkg file
Input the height and weight of the boxes, specify the geometries to clip.

## Algorthim
1. Loads and then crops the entire scene.
2. Performs thresholding using suitable VIs
3. Them perform morphological opening to smooth out the mask
4. Splits the rasters into rows of height equal to the height of the box then determines the column midpoint of the vegetation to determine the midpoint of the boxes.
5. Saves it in a .gpkg file