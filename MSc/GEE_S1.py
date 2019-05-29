from FloppyToolZ.MasterFuncs import *
import ee
ee.Initialize()

# load modis center coordinates
# create polygons
# transform to 4326
# reduce

points = 'Y:/_students_data_exchange/FP_FP/Seafile/myLibrary/MSc/2nd_round/plot_coords/Combined_cont_gasp1_centerCoord_MODIS_ordered_XY_snaked_10.shp'
points_op = ogr.Open(points, 0)
poi_lyr = points_op.GetLayer()

start = '2016-07-01'
end = '2016-10-01'

s1_VV = ee.ImageCollection('COPERNICUS/S1_GRD'). \
    filterDate(start, end). \
    filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV')). \
    filter(ee.Filter.eq('instrumentMode', 'IW')). \
    select('VV')

s1_VH = ee.ImageCollection('COPERNICUS/S1_GRD'). \
    filterDate(start, end). \
    filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH')). \
    filter(ee.Filter.eq('instrumentMode', 'IW')). \
    select('VH')

s1_HV = ee.ImageCollection('COPERNICUS/S1_GRD'). \
    filterDate(start, end). \
    filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'HV')). \
    filter(ee.Filter.eq('instrumentMode', 'IW')). \
    select('HV')

s1_HH = ee.ImageCollection('COPERNICUS/S1_GRD'). \
    filterDate(start, end). \
    filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'HH')). \
    filter(ee.Filter.eq('instrumentMode', 'IW')). \
    select('HH')

poi = poi_lyr.GetFeature(0)
pts = {'type': 'Point', 'coordinates': [poi.geometry().GetX(), poi.geometry().GetY()]}

val_VV = ee.ImageCollection(s1_VV).getRegion(pts, 10).getInfo()
val_VH = ee.ImageCollection(s1_VH).getRegion(pts, 10).getInfo()
val_HV = ee.ImageCollection(s1_HV).getRegion(pts, 10).getInfo()
val_HH = ee.ImageCollection(s1_HH).getRegion(pts, 10).getInfo()


print(val_VV)
