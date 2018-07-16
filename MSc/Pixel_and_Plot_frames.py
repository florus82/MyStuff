import pandas as pd
from FloppyToolZ.Funci import *

ShapeKiller('/home/florian/MSc/test_GE/GEE_Points_shapes/Gasparri_MODIS_9points_4326_reproj_3035.shp')
ShapeKiller('/home/florian/MSc/test_GE/GEE_Points_shapes/Gasparri_MODIS_9points_4326.shp')
ShapeKiller('/home/florian/MSc/test_GE/GEE_Points_shapes/Gasparri_MODIS_9points_4326_reproj_3035_Pixel.shp')

# load the extract and remove duplicates
da = pd.read_csv('/home/florian/MSc/test_GE/extracts/MODIS/Conti-etal_rightIDs_9Points_250_MODIS_Extracts.csv')
da2 = da.rename(index = str, columns = {'Unnamed: 0' : 'Time', 'longitude':'longitude', 'latitude':'latitude', 'time':'time',
                                  'MOD_NDVI':'MOD_NDVI', 'MOD_EVI':'MOD_EVI', 'DetailedQA':'DetailedQA',
                                  'Point-ID':'Point.ID', 'Block-ID':'Block.ID'})
da2 = da2.drop_duplicates(['longitude', 'latitude', 'Point.ID', 'Block.ID'],keep='first')
da2.reset_index()

# extract coordinates
coords = dict.fromkeys(['X', 'Y'])
coords['X'] = list(da2['longitude'])
coords['Y'] = list(da2['latitude'])

# get attributes
attri = dict.fromkeys(['Point.ID', 'Block.ID', 'Time'])
attri['Point.ID'] = list(da2['Point.ID'])
attri['Block.ID'] = list(da2['Block.ID'])
attri['Time']     = list(da2['Time'])

# make point shapefile and create reprojected file as well
XYtoShape(coords, attri, 4326, '/home/florian/MSc/test_GE/GEE_Points_shapes', 'Gasparri_MODIS_9points_4326', 'point')

reprojShape('/home/florian/MSc/test_GE/GEE_Points_shapes/Gasparri_MODIS_9points_4326.shp', 3035)

xy = getXYfromShape('/home/florian/MSc/test_GE/GEE_Points_shapes/Gasparri_MODIS_9points_4326_reproj_3035.shp')

xySquares = boundingCentroidCoord(list(xy['X']),list(xy['Y']),250)

XYtoShape(xySquares, attri, 3035, '/home/florian/MSc/test_GE/GEE_Points_shapes', 'Gasparri_MODIS_9points_4326_reproj_3035_Pixel', 'poly')

reprojShape('/home/florian/MSc/test_GE/GEE_Points_shapes/Gasparri_MODIS_9points_4326_reproj_3035_Pixel.shp', 4326)


# warp actual MODIS images
#
# img = getFilelist('/home/florian/MSc/RS_Data/MODIS/raw','hdf')
# out = ['/home/florian/MSc/RS_Data/MODIS/GTiff/3035', '/home/florian/MSc/RS_Data/MODIS/GTiff/4326']
# codes = [3035, 4326]
#
# for file in img:
#     for i, coord in enumerate(codes):
#         warpMODIS(file, out[i], coord)