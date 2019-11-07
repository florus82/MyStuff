from FloppyToolZ.MasterFuncs import *
from joblib import Parallel, delayed
import time

# set the tiling system layer
tile_path = r'Y:\FP_MB\CHACO_extent_tiles_9.shp'

# set time start and time end
t_start = 20180901
t_end = 20190831

# set the path for the polygonized S1 scenes
poly_path = r'E:\Florian\MSc_outside_Seafile\RS_Data\S1\after_preprocess\scene_polys\VV_Polygons.shp'

# paths for VV and VH folders
VVfold = r'E:\Florian\MSc_outside_Seafile\RS_Data\S1\after_preprocess\VV'
VHfold = r'E:\Florian\MSc_outside_Seafile\RS_Data\S1\after_preprocess\VH'

# set OutputFolder
outFo = r'E:\Florian\MSc_outside_Seafile\RS_Data\S1\after_preprocess\Metrics'

# get a list of valid (CHACO_YN ==1) Id_long
tiling = ogr.Open(tile_path)
tiles = tiling.GetLayer()
tiles.SetAttributeFilter('CHACO_YN = 1')
idList = [til.GetField('Id_long') for til in tiles]
tiles.ResetReading()
#
# tilefile = tile_path
# tileID = idList[0]
# time_start = t_start
# time_end = t_end
# polygonfile_path = poly_path
# VVfolder_path = VVfold
# VHfolder_path = VHfold
# outFolder = outFo
def S1_metricizer(tilefile, tileID, time_start, time_end, polygonfile_path, VVfolder_path, VHfolder_path, outFolder):
    # set variables
    drivMemVec = ogr.GetDriverByName('Memory')
    drivMemRas = gdal.GetDriverByName('MEM')
    gtiff_driver = gdal.GetDriverByName('GTiff')

    tiles_open = ogr.Open(tilefile)
    tiles_lyr  = tiles_open.GetLayer()
    query = '{} = {}'.format('Id_long', tileID)
    tiles_lyr.SetAttributeFilter(query)
    tili = tiles_lyr.GetNextFeature()
    geom = tili.geometry() # load geometry

    # create polygon dummy for rasterizing
    shpMem = drivMemVec.CreateDataSource('')
    shpMem_lyr = shpMem.CreateLayer('shpMem', getSpatRefVec(tiles_open), geom_type=ogr.wkbPolygon)
    shpMem_lyr_defn = shpMem_lyr.GetLayerDefn()
    shpMem_feat = ogr.Feature(shpMem_lyr_defn)
    shpMem_feat.SetGeometry(geom)
    shpMem_lyr.CreateFeature(shpMem_feat)

    # intersect
    pol = ogr.Open(polygonfile_path)
    pol_lyr = pol.GetLayer()
    sceneCont = []
    pol_lyr.SetSpatialFilter(geom)
    for p in pol_lyr:
        sceneCont.append(p.GetField('Scene'))
        #print(p.GetField('Scene'))
    pol_lyr.SetSpatialFilter(None)
    pol_lyr.ResetReading()

    arrList = []
    # loop over polarizations
    for polar in [VVfolder_path]:# , VHfolder_path]:
        # loop over scenes in container
        for scene in sceneCont:
            year = int(scene.split('_')[4][0:4])*10000
            month = int(scene.split('_')[4][4:6])*100
            day = int(scene.split('_')[4][6:8])
            if (year + month + day) >= time_start and (year + month + day) <= time_end:
                rasti = gdal.Open(polar + '/' + scene + '.tif')
                gt = rasti.GetGeoTransform()
                # build empty raster based on create memory tile object
                x_min, x_max, y_min, y_max = shpMem_lyr.GetExtent()
                x_res = int((x_max - x_min) / gt[1]) + 1
                y_res = int((y_max - y_min) / gt[1]) + 1
                shpMem_asRaster = drivMemRas.Create('', x_res, y_res, rasti.GetRasterBand(1).DataType)
                shpMem_asRaster.SetProjection(str(getSpatRefRas(rasti)))
                shpMem_asRaster.SetGeoTransform((x_min, gt[1], 0, y_max, 0, gt[5]))
                shpMem_asRaster_band = shpMem_asRaster.GetRasterBand(1)
                shpMem_asRaster_band.SetNoDataValue(0)
                gdal.RasterizeLayer(shpMem_asRaster, [1], shpMem_lyr, burn_values=[1])
                shpMem_array = np.array(shpMem_asRaster_band.ReadAsArray())

                rasMem = drivMemRas.Create('', shpMem_asRaster.RasterXSize, shpMem_asRaster.RasterYSize, 1, rasti.GetRasterBand(1).DataType)
                rasMem.SetGeoTransform(shpMem_asRaster.GetGeoTransform())
                rasMem.SetProjection(shpMem_asRaster.GetProjection())
                gdal.ReprojectImage(rasti, rasMem, rasti.GetProjection(), shpMem_asRaster.GetProjection(), gdal.GRA_NearestNeighbour)
                rasMem_array = np.array(rasMem.GetRasterBand(1).ReadAsArray())
                rasMem_array[rasMem_array<=0] = np.nan
                arrList.append(rasMem_array)

            else:
                continue
            # calculate metrics: mean, median, 5, 25, 75, 95th, std

        if not arrList:
            continue
        else:
            stack = np.dstack(arrList)
            #meanL, medianL, q5L, q25L, q75L, q95L, stdL = [], [], [], [], [], [], []
            metrL = []
            metrL.append(np.nanmean(stack, 2))
            metrL.append(np.nanmedian(stack, 2))
            metrL.append(np.nanquantile(stack, 0.05, axis=2))
            metrL.append(np.nanquantile(stack, 0.25, axis=2))
            metrL.append(np.nanquantile(stack, 0.75, axis=2))
            metrL.append(np.nanquantile(stack, 0.95, axis=2))
            metrL.append(np.nanstd(stack, axis=2))
            metrL.append(np.count_nonzero(~np.isnan(stack), 2))

            if polar is VVfolder_path:
                out_ds = gtiff_driver.Create(outFolder + '/VV/2nd/Id_long_' + str(int(tili.GetField('Id_long'))) +'.tif', x_res, y_res, len(metrL), rasti.GetRasterBand(1).DataType)
            else:
                out_ds = gtiff_driver.Create(outFolder + '/VH/2nd/Id_long_' + str(int(tili.GetField('Id_long'))) + '.tif', x_res, y_res,
                                             len(metrL), rasti.GetRasterBand(1).DataType)
            out_gt = rasMem.GetGeoTransform()
            out_ds.SetGeoTransform(out_gt)
            out_ds.SetProjection(str(getSpatRefRas(rasti)))
            for i in range(0, len(metrL)):
                out_ds.GetRasterBand(i+1).WriteArray(metrL[i])
                out_ds.GetRasterBand(i+1).SetNoDataValue(-9999)
            del out_ds
            print('Tile - done')

    return ('Metricized :)')

# create the joblist
joblist = []
for id in idList:
    joblist.append([tile_path, id, t_start, t_end, poly_path, VVfold, VHfold, outFo])

if __name__ == '__main__':
# ####################################### SET TIME COUNT ###################################################### #
    starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print("--------------------------------------------------------")
    print("Starting process, time:" +  starttime)
    print("")


    Parallel(n_jobs=58)(delayed(S1_metricizer)(job[0], job[1], job[2], job[3], job[4], job[5], job[6], job[7]) for job in joblist)

    print("")
    endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print("--------------------------------------------------------")
    print("--------------------------------------------------------")
    print("start: " + starttime)
    print("end: " + endtime)
    print("")