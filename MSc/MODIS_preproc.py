from FloppyToolZ.Funci import *

# ########################## get a common extent between the Chaco region and the MODIS tile (projected reference image needed)
# modis reference extent
ModExt   = getExtent('/home/florian/MSc/RS_Data/MODIS/test/MODIS_samp.tif')

# Chaco extent
in_ds  = ogr.Open('/home/florian/MSc/GIS_Data/CHACO/CHACO_VeryDry_Dry_Humid_LAEA_modFP.shp')
in_lyr = in_ds.GetLayer()
xmin, xmax, ymin, ymax = in_lyr.GetExtent()
ChacoExt = {'Xmin': xmin,
            'Xmax': xmax,
            'Ymin': ymin,
            'Ymax': ymax}

# common extent
ComExt = commonBoundsCoord(commonBoundsDim([ModExt[0], ChacoExt]))

# rastersubbyCord('/home/florian/MSc/RS_Data/MODIS/test/MODIS_samp.tif', ComExt[0]['UpperLeftXY'][0], ComExt[0]['UpperLeftXY'][1], ComExt[0]['LowerRightXY'][0], ComExt[0]['LowerRightXY'][1],
#                 '/home/florian/MSc/RS_Data/MODIS/reference_extent')

# ########################## rasterizing the Chaco for masking pixel outside
# reference image
ChacoImg = gdal.Open('/home/florian/MSc/RS_Data/MODIS/reference_extent/MODIS_samp_subby.tif')
# create memory object
ChacoM = gdal.GetDriverByName('MEM').Create('', ChacoImg.RasterXSize, ChacoImg.RasterYSize, 1, gdal.GDT_Float32)
ChacoM.SetProjection(ChacoImg.GetProjectionRef())
ChacoM.SetGeoTransform(ChacoImg.GetGeoTransform())
# rasterize
Band = ChacoM.GetRasterBand(1)
Band.SetNoDataValue(0)
gdal.RasterizeLayer(ChacoM, [1], in_lyr, burn_values=[1])
# get mask array
Chaco_arr = ChacoM.ReadAsArray()
ChacoNA   = ChacoM.GetRasterBand(1).GetNoDataValue()


# ################################# set the stage
# get all the hdf containers and specify output location
files = getFilelist('/home/florian/MSc/RS_Data/MODIS/raw','.hdf')
storNDVI = '/home/florian/MSc/RS_Data/MODIS/GTiff/102033/NDVI/'
storEVI  = '/home/florian/MSc/RS_Data/MODIS/GTiff/102033/EVI/'
storNBR  = '/home/florian/MSc/RS_Data/MODIS/GTiff/102033/NBR/'

pathlist = [storEVI, storNBR, storNDVI]
NamList  = ['EVI', 'NBR', 'NDVI']
# set parameter
epsg   = 102033
bands  = ['NDVI', 'EVI', 'NIR reflectance', 'MIR reflectance', 'pixel reliability', 'VI Quality']
NaList = [-3000, -1000, -3000, -1000, 65535, 255]

###################################### loop from here (parallel????)
# open a container, retrieve information about layer and select the ones indicated above
for j, file in enumerate(files):
    hdf  = gdal.Open(file)
    sdsdict = hdf.GetMetadata('SUBDATASETS')
    sdslist = [sdsdict[k] for k in sdsdict.keys() if '_NAME' in k]
    select  = [img for img in sdslist for sub in bands if img.endswith(sub)]
    select.sort()

    # ################build quality masks
    # pixel reliability (0-3)
    # q1 = gdal.Open(select[5])
    #
    # ds = gdal.Warp('', q1, dstSRS='EPSG:'+ str(epsg), format='VRT',outputType=q1.GetRasterBand(1).DataType)
    # q1NA = ds.GetRasterBand(1).GetNoDataValue()
    #
    # q1_res = rastersubbyCord(ds,ComExt[0]['UpperLeftXY'][0], ComExt[0]['UpperLeftXY'][1], ComExt[0]['LowerRightXY'][0],
    #                      ComExt[0]['LowerRightXY'][1])['Data'][0]
    # # probably close ds here


    # VI Quality (more stuff)
    q2 = gdal.Open(select[4])
    q2_gt = q2.GetGeoTransform()
    ds = gdal.Warp('', q2, dstSRS='EPSG:'+ str(epsg), format='MEM',outputType=q2.GetRasterBand(1).DataType, xRes=q2_gt[1], yRes=q2_gt[1])
    q2NA = ds.GetRasterBand(1).GetNoDataValue()

    q2_res = rastersubbyCord(ds,ComExt[0]['UpperLeftXY'][0], ComExt[0]['UpperLeftXY'][1], ComExt[0]['LowerRightXY'][0],
                         ComExt[0]['LowerRightXY'][1])

    q2_arr = q2_res['Data'][0]

    del q2
    del ds

    # set NAs
    Chaco_arr[Chaco_arr == ChacoNA] = np.nan
    #q1_arr[q1_arr == q1NA] = np.nan
    q2_arr[q2_arr == q2NA] = np.nan

    #q1m = q1_arr * Chaco_arr
    q2m = q2_arr * Chaco_arr

    # maybe only 2112
    #testi = np.where(q1m ==0,1, np.where((q1m==1) & (q2m == 2057),2,np.nan))
    powMa = np.where(q2m == 2112,1,np.nan)
    #testi[np.isnan(testi)] = 10000

    # np.isin(mask, bad value)
    # ##### for output testing only!!!!!!!!
    # gtiff_driver = gdal.GetDriverByName('GTiff')
    # out_ds = gtiff_driver.Create('/home/florian/MSc/RS_Data/MODIS/GTiff/'+'testi2' +
    #                              '.tif', q1_arr.shape[1],
    #                              q1_arr.shape[0], 1, ds.GetRasterBand(1).DataType)
    # out_ds.SetGeoTransform(ChacoImg.GetGeoTransform())
    # out_ds.SetProjection(ds.GetProjection())
    # out_ds.GetRasterBand(1).WriteArray(testi)
    # out_ds.GetRasterBand(1).SetNoDataValue(10000)
    # del out_ds

    # then, the rastersubbycoords of the bands list has to be masked with NAs of q1m an q2m and q3m




    # and stored to disk

    # then close all connections

    # think about parallel
    conti = []
    for i in range(4):
        go = gdal.Open(select[i])
        ds = gdal.Warp('', go, dstSRS='EPSG:' + str(epsg), format='VRT', outputType=ChacoImg.GetRasterBand(1).DataType, xRes=q2_gt[1], yRes=q2_gt[1])
        ds_NA = ds.GetRasterBand(1).GetNoDataValue()
        ds_arr = rastersubbyCord(ds, ComExt[0]['UpperLeftXY'][0], ComExt[0]['UpperLeftXY'][1], ComExt[0]['LowerRightXY'][0],
                        ComExt[0]['LowerRightXY'][1])['Data'][0]
        ds_arr[ds_arr == NaList[i]] = np.nan
        DS = ds_arr * powMa
       # DS[np.isnan(DS)] = 10000
        conti.append(DS)
        del go


    # calc NBR
    conti[1] = (conti[3] - conti[1]) / (conti[3] + conti[1]) * 10000
    del conti[3]
    for arr in conti:
        arr[np.isnan(arr)] = 10000

    gtiff_driver = gdal.GetDriverByName('GTiff')

    for i, path in enumerate(pathlist):
        out_ds = gtiff_driver.Create(path + file.split('.hdf')[0].split('/')[-1] + '_' + NamList[i] +
            '.tif', conti[i].shape[1], conti[i].shape[0], 1, ds.GetRasterBand(1).DataType)
        out_ds.SetGeoTransform(ChacoImg.GetGeoTransform())
        out_ds.SetProjection(ds.GetProjection())
        out_ds.GetRasterBand(1).WriteArray(conti[i])
        out_ds.GetRasterBand(1).SetNoDataValue(10000)
        del out_ds
    del hdf
    del ds
    print('{} % done'.format(round(((j+1)/702)*100,2)))


