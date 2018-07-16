from osgeo import ogr
import csv
import ee
import os
from tqdm import tqdm
ee.Initialize()
from FloppyToolZ.Funci import *


# # ####################################### FILES AND FOLDER-PATHS ############################################## #

#files = getFilelist('/home/florian/MSc/GEE/Landsat_Test','shp')
files = ['/home/florian/MSc/GEE/Landsat_Test3/Control_reproj_4326.shp']
storpath = '/home/florian/MSc/GEE/Landsat_Test3/'
#
# # ####################################### SEARCH PARAMETERS ################################################### #
#
startDate = '2007-11-01'
endDate   = '2007-11-10'

# ####################################### FUNCTIONS ########################################################### #
def Retrieve_SR01_fromGEE_Point(geometry, startDate, endDate):
    # startDate & endDate has to be in the format "2018-01-01"
    # Coordinate system has to be be WGS84 (EPSG:4326)
    # Material for masking
    # --> https://gis.stackexchange.com/questions/274048/apply-cloud-mask-to-landsat-imagery-in-google-earth-engine-python-api
    # --> https://github.com/gee-community/gee_tools
    def getQABit(image, start, end, newName):
        pattern = 0
        for i in range(start, end + 1):
            pattern += 2 ** i
        return image.select([0], [newName]).bitwiseAnd(pattern).rightShift(start)


    def maskQuality(image):
        # Select the QA band.
        QA = image.select('pixel_qa')
        # Get the internal_cloud_algorithm_flag bit.
        shadow = getQABit(QA, 3, 3, 'cloud_shadow')
        cloud = getQABit(QA, 5, 5, 'cloud')
        water = getQABit(QA, 2, 2,'water')
        #  var cloud_confidence = getQABits(QA,6,7,  'cloud_confidence')
        #cirrus = getQABit(QA, 9, 9, 'cirrus')
        # Return an image masking out cloudy areas.
        return image.updateMask(cloud.eq(0)).updateMask(shadow.eq(0).updateMask(water.eq(0)))

    def maskQualityMODIS(image):
        # Select the QA band.
        QA2 = image.select('DetailedQA')
        # Get the internal_cloud_algorithm_flag bit.
        internalQuality = getQABit(QA2,0, 0, 'internal_quality_flag')

        # Return an image masking out cloudy areas.
        return image.updateMask(internalQuality.eq(0))

    # Build an earth engine feature
    xCoord = geometry.GetX()
    yCoord = geometry.GetY()
    pts = {'type': 'Point', 'coordinates': [xCoord, yCoord]}
    # Now extract the individual data from the collections based on the definitions above
    # Define the band names that we want to extract
    l8bands = ee.List(['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B1', 'B10', 'B11', 'pixel_qa'])
    l8band_names = ee.List(['B', 'G', 'R', 'NIR', 'SWIR1', 'SWIR2', 'UB', 'T1', 'T2','pixel_qa'])
    l8bands = ee.List(['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'pixel_qa']) # as demanded by gee
    l8band_names = ee.List(['B', 'G', 'R', 'NIR', 'SWIR1', 'SWIR2', 'pixel_qa'])
    l457bands = ee.List(['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'pixel_qa'])
    l457band_names = ee.List(['B', 'G', 'R', 'NIR', 'SWIR1', 'SWIR2', 'pixel_qa'])
    modvegbands = ee.List(['NDVI', 'EVI', 'DetailedQA'])
    modvegbands_names = ee.List(['MOD_NDVI', 'MOD_EVI', 'DetailedQA'])

    # Landsat 8
    coll_L8 = ee.ImageCollection('LANDSAT/LC08/C01/T1_SR'). \
        filterDate(startDate, endDate). \
        select(l8bands, l8band_names). \
        map(maskQuality)
    # Landsat 7
    coll_L7 = ee.ImageCollection('LANDSAT/LE07/C01/T1_SR'). \
        filterDate(startDate, endDate). \
        select(l457bands, l457band_names). \
        map(maskQuality)
    # Landsat 5
    coll_L5 = ee.ImageCollection('LANDSAT/LT05/C01/T1_SR'). \
        filterDate(startDate, endDate). \
        select(l457bands, l457band_names). \
        map(maskQuality)
    # Landsat 4
    coll_L4 = ee.ImageCollection('LANDSAT/LT04/C01/T1_SR'). \
        filterDate(startDate, endDate). \
        select(l457bands, l457band_names). \
        map(maskQuality)
    # MODIS TERRA 16days 250m
    # coll_MOD_T = ee.ImageCollection('MODIS/006/MOD13Q1'). \
    #     filterDate(startDate, endDate). \
    #     select(modvegbands, modvegbands_names). \
    #     map(maskQualityMODIS)
    # # MODIS AQUA 16days 250m
    # coll_MOD_A = ee.ImageCollection('MODIS/006/MYD13Q1'). \
    #     filterDate(startDate, endDate). \
    #     select(modvegbands, modvegbands_names). \
    #     map(maskQualityMODIS)
    # Merge
    #values_all = ee.ImageCollection(coll_MOD_A.merge(coll_MOD_T)).getRegion(pts, 30).getInfo()
    values_all = ee.ImageCollection(coll_L4.merge(coll_L5).merge(coll_L7).merge(coll_L8)).getRegion(pts, 30).getInfo()
    return values_all
# ####################################### COLLECT THE VALUES PER POINT ######################################## #

for file in files:
    shp = ogr.Open(file)

    print("Extract values for points in SHP-file")
    valueList = []
    lyr = shp.GetLayer()
    coord = lyr.GetSpatialRef()
    nFeat = lyr.GetFeatureCount()

    #while feat:
    for feat in tqdm(lyr):
    # Extract ID-Info from SHP-file and other informations
        Pid = feat.GetField('POINT_ID')
        #Bid = feat.GetField('Block_ID')

        #print("Processing Point ID " + str(Pid))
    # Now get the geometry and do stuff
        geom = feat.GetGeometryRef()
    # Now extract the individual data from the collections based on the definitions above
        vals = Retrieve_SR01_fromGEE_Point(geometry=geom, startDate=startDate, endDate=endDate)
    # Add to the header-line the Variable-Name Point-ID, and add it to each element as well
        vals[0].append("Point-ID")
        for i in range(1,len(vals)):
            vals[i].append(Pid)

        # vals[0].append("Block-ID")
        # for i in range(1, len(vals)):
        #     vals[i].append(Bid)
    # Remove right away the masked values, and some remnants from the sceneID
        val_reduced = []
        for val in vals:
            if not None in val:
            #    val[0] = '-'.join(val[0].split('_')[1:])
                sceneID = val[0]
                p1 = sceneID.find("L")
                sceneID = sceneID[p1:]
                val[0] = sceneID
                val_reduced.append(val)
    # Append to output then get next feature


        valueList.append(val_reduced)
        #feat = lyr.GetNextFeature()
    # ##################################### WRITE OUTPUT ######################################################## #

    with open(storpath + file.split('/')[-1].split('.')[0] + '_LANDSAT_TEST_Extracts.csv', "w") as theFile:
        csv.register_dialect("custom", delimiter=",", skipinitialspace=True, lineterminator='\n')
        writer = csv.writer(theFile, dialect="custom")
        # Write the complete set of values (incl. the header) of the first entry
        for element in valueList[0]:
            writer.writerow(element)
        valueList.pop(0)
        # Now write the remaining entries, always pop the header
        for element in valueList:
            element.pop(0)
            for row in element:
                writer.writerow(row)