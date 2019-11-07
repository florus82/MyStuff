from FloppyToolZ.Funci import *

# set paths
tile_path = 'Y:/FP_MB/CHACO_extent_tiles_9.shp'
VV_path   = r'E:\Florian\MSc_outside_Seafile\RS_Data\S1\after_preprocess\VV'
VH_path   = r'E:\Florian\MSc_outside_Seafile\RS_Data\S1\after_preprocess\VH'
pol_path  = r'E:\Florian\MSc_outside_Seafile\RS_Data\S1\after_preprocess\scene_polys'

# set variables
drivESRI = ogr.GetDriverByName('ESRI Shapefile')
drivMemVec = ogr.GetDriverByName('Memory')
drivMemRas = gdal.GetDriverByName('MEM')
gtiff_driver = gdal.GetDriverByName('GTiff')

# ############################# create empty shapefile for storing scene extent polygons #########################
def sceneFinder_for_tiling(scenefolder, outFolder, outFileName, tilingShape):
    driver = ogr.GetDriverByName('ESRI Shapefile')
    shapeStor = driver.CreateDataSource(outFolder)
    out_lyr = shapeStor.CreateLayer(outFileName, getSpatRefVec(tilingShape), ogr.wkbPolygon)

    # create Fields
    #FID
    id_fld = ogr.FieldDefn('FID', ogr.OFTInteger)
    id_fld.SetWidth(10)
    id_fld.SetPrecision(1)
    out_lyr.CreateField(id_fld)

    # Scene Name
    nam_fld = ogr.FieldDefn('Scene', ogr.OFTString)
    nam_fld.SetWidth(50)
    out_lyr.CreateField(nam_fld)

    out_feat = ogr.Feature(out_lyr.GetLayerDefn())

    # ############################# create polygons for S1 tiles (VV is enough as identical extent as respective VHs) #########################
    files = getFilelist(scenefolder, '.tif')
    # files = files[65:75]
    squareList = []
    sceneList = []
    for i, file in enumerate(files):
        print(i/len(files))
        sceneList.append(file.split('/')[-1].split('.')[0])
        fil = gdal.Open(file, gdal.GA_ReadOnly)
        gt  =fil.GetGeoTransform()
        #load raster
        ras = fil.GetRasterBand(1).ReadAsArray()
        # get corners with of data space
        r, c = np.where(ras[:,:] > 0)
        upper_x1 = gt[0] + (c[0]-1)*gt[1]
        upper_y1 = gt[3] + (r[0]-1)*gt[5]
        upper_x2 = upper_x1 + (np.where(ras[r[0], :] > 0)[0].shape[0]-1)*gt[1]
        upper_y2 = upper_y1

        right_x1 = gt[0] + (np.max(c)+1)*gt[1]
        right_y1 = gt[3] + (r[np.where(c == np.max(c))[0]][0])*gt[5]
        right_x2 = right_x1
        right_y2 = right_y1 + (r[np.where(c == np.max(c))[0]].shape[0]+1)*gt[5]

        lower_x1 = gt[0] + (c[np.where(r == np.flip(r)[0])[0][0]])*gt[1]
        lower_y1 = gt[3] + (np.flip(r)[0]+2)*gt[5]
        lower_x2 = lower_x1 + (np.where(r == np.flip(r)[0])[0].shape[0])*gt[1]
        lower_y2 = lower_y1

        left_x1 = gt[0] + (np.min(c)-1)*gt[1]
        left_y1 = gt[3] + (r[np.where(c == np.min(c))[0]][0]+2)*gt[5]
        left_x2 = left_x1
        left_y2 = left_y1 + (r[np.where(c == np.min(c))[0]].shape[0])*gt[5]

        ring = ogr.Geometry(ogr.wkbLinearRing)
        ring.AddPoint(upper_x1, upper_y1)
        ring.AddPoint(upper_x2, upper_y2)
        ring.AddPoint(right_x1, right_y1)
        ring.AddPoint(right_x2, right_y2)
        ring.AddPoint(lower_x2, lower_y2)
        ring.AddPoint(lower_x1, lower_y1)
        ring.AddPoint(left_x2, left_y2)
        ring.AddPoint(left_x1, left_y1)

        square = ogr.Geometry(ogr.wkbPolygon)
        square.AddGeometry(ring)
        square.CloseRings()
        squareList.append(square)

    # ############################# store polygons in empty shapefile #########################
    for j, squa in enumerate(squareList):
        print(j)
        out_feat.SetGeometry(squa)
        out_feat.SetField(0, j)
        out_feat.SetField(1, sceneList[j])
        out_lyr.CreateFeature(out_feat)
    shapeStor.Destroy()

sceneFinder_for_tiling(VV_path, pol_path, 'VV_Polygons', tile_path)