from FloppyToolZ.MasterFuncs import *
import ee
ee.Initialize()
import pandas as pd

# load modis center coordinates
# create polygons
# transform to 4326
# reduce

# output dictionary

k = ['POINT_ID', 'Block_ID', 'X', 'Y', 'Scene', 'Long', 'Lat', 'Val', 'Polar', 'Mode']
v = [list() for i in k]
res = dict(zip(k, v))

points = 'Y:/_students_data_exchange/FP_FP/Seafile/myLibrary/MSc/2nd_round/plot_coords/Combined_cont_gasp1_centerCoord_MODIS_ordered_XY_snaked_10.shp'
points_op = ogr.Open(points, 0)
poi_lyr = points_op.GetLayer()

start = '2015-07-15'
end = '2016-09-14'


# get asc/desc metadata
def orbiter(image):
    return image.addBands(ee.Number(image.metadata('orbitProperties_pass')))

## VV
s1_VV_a = ee.ImageCollection('COPERNICUS/S1_GRD'). \
    filterDate(start, end). \
    filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV')). \
    filter(ee.Filter.eq('instrumentMode', 'IW')). \
    select('VV'). \
    filter(ee.Filter.eq('orbitProperties_pass', 'ASCENDING'))

s1_VV_d = ee.ImageCollection('COPERNICUS/S1_GRD'). \
    filterDate(start, end). \
    filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV')). \
    filter(ee.Filter.eq('instrumentMode', 'IW')). \
    select('VV'). \
    filter(ee.Filter.eq('orbitProperties_pass', 'DESCENDING'))

# VH
s1_VH_a = ee.ImageCollection('COPERNICUS/S1_GRD'). \
    filterDate(start, end). \
    filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH')). \
    filter(ee.Filter.eq('instrumentMode', 'IW')). \
    select('VH'). \
    filter(ee.Filter.eq('orbitProperties_pass', 'ASCENDING'))

s1_VH_d = ee.ImageCollection('COPERNICUS/S1_GRD'). \
    filterDate(start, end). \
    filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH')). \
    filter(ee.Filter.eq('instrumentMode', 'IW')). \
    select('VH'). \
    filter(ee.Filter.eq('orbitProperties_pass', 'DESCENDING'))

# HV
s1_HV_a = ee.ImageCollection('COPERNICUS/S1_GRD'). \
    filterDate(start, end). \
    filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'HV')). \
    filter(ee.Filter.eq('instrumentMode', 'IW')). \
    select('HV'). \
    filter(ee.Filter.eq('orbitProperties_pass', 'ASCENDING'))

s1_HV_d = ee.ImageCollection('COPERNICUS/S1_GRD'). \
    filterDate(start, end). \
    filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'HV')). \
    filter(ee.Filter.eq('instrumentMode', 'IW')). \
    select('HV'). \
    filter(ee.Filter.eq('orbitProperties_pass', 'DESCENDING'))

# HH
s1_HH_a = ee.ImageCollection('COPERNICUS/S1_GRD'). \
    filterDate(start, end). \
    filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'HH')). \
    filter(ee.Filter.eq('instrumentMode', 'IW')). \
    select('HH'). \
    filter(ee.Filter.eq('orbitProperties_pass', 'ASCENDING'))

s1_HH_d = ee.ImageCollection('COPERNICUS/S1_GRD'). \
    filterDate(start, end). \
    filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'HH')). \
    filter(ee.Filter.eq('instrumentMode', 'IW')). \
    select('HH'). \
    filter(ee.Filter.eq('orbitProperties_pass', 'DESCENDING'))


# iterate over points
print('start extracting')

for poi in poi_lyr:
    #poi = poi_lyr.GetFeature(0)
    pts = {'type': 'Point', 'coordinates': [poi.geometry().GetX(), poi.geometry().GetY()]}

    collects = [s1_VV_a, s1_VV_d, s1_VH_a, s1_VH_d, s1_HV_a, s1_HV_d, s1_HH_a, s1_HH_d]
    polar    = ['VV', 'VV', 'VH', 'VH', 'HV', 'HV', 'HH', 'HH']
    mode     = ['Ascending', 'Descending', 'Ascending', 'Descending', 'Ascending', 'Descending', 'Ascending', 'Descending']

    for j, coll in enumerate(collects):
        cont = ee.ImageCollection(coll).getRegion(pts, 10).getInfo()

        if(len(cont) > 1):
            for i in range(1,len(cont)):
                res['POINT_ID'].append(poi.GetField('POINT_ID'))
                res['Block_ID'].append(poi.GetField('Block_ID'))
                res['X'].append(pts['coordinates'][0])
                res['Y'].append(pts['coordinates'][1])
                res['Scene'].append(cont[i][0])
                res['Long'].append(cont[i][1])
                res['Lat'].append(cont[i][2])
                res['Val'].append(cont[i][3])
                res['Polar'].append(polar[j])
                res['Mode'].append(mode[j])
        print(j)


    df    = pd.DataFrame(data = res)
    df.to_csv('Y:/_students_data_exchange/FP_FP/Seafile/myLibrary/MSc/2nd_round/extracts/from_ee/S1/' + poi.GetField('POINT_ID') + '.csv', sep=',',index=False)
    print(poi.GetField('POINT_ID'))