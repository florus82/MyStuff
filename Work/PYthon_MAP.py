from FloppyToolZ.MasterFuncs import *

# select modis files for growing season 2014 - 2015
hdfs = getFilelist('Y:/_students_data_exchange/FP_FP/RS_Data/MODIS/raw/raw1', 'hdf')
hdf2015 = []

for hdf in hdfs:
    if hdf.split('.')[1][1:5] in ['2014'] and int(hdf.split('.')[1][5:8]) > 220:
        hdf2015.append(hdf)
    elif hdf.split('.')[1][1:5] in ['2015'] and int(hdf.split('.')[1][5:8]) < 220:
        hdf2015.append(hdf)

# order hdf paths
aa = [a.split('.')[1][1:8] for a in hdf2015]
bb = dict(zip(aa, hdf2015))
hdf2015_sorted = [v for k, v in sorted(bb.items())]


# set MODIS bands, NAvalues and masks
bands  = ['NDVI', 'EVI', 'NIR reflectance', 'MIR reflectance', 'pixel reliability', 'VI Quality']
NaList = [-3000, -1000, -3000, -1000, 65535, 255]
VI_oki = [2112, 4160, 6208]

# start power loop
ndvi_list = []
evi_list = []

for hdf in hdf2015_sorted:
    print(hdf)
    mod = gdal.Open(hdf)
    sdsdict = mod.GetMetadata('SUBDATASETS')
    sdslist = [sdsdict[k] for k in sdsdict.keys() if '_NAME' in k]
    select = [img for img in sdslist for sub in bands if img.endswith(sub)]
    select.sort()

    # load bands into numpy stack with quality band as third array
    arr_list = []
    for s in [img for i, img in enumerate(select) if i in [0, 2, 4]]:
        a = gdal.Open(s)
        arr_list.append(a.GetRasterBand(1).ReadAsArray())

    # mask bad quality pixel

    stacki = np.dstack(arr_list[0:2])
    rows, cols = np.where(np.isin(arr_list[2], VI_oki, invert = True))
    stacki[rows, cols, :] = -9999

    # load Chaco bounds and mask stack
    ma  = gdal.Open('Y:/_students_data_exchange/FP_FP/RS_Data/MODIS/rasterized/Mod1.tiff')
    mas = ma.GetRasterBand(1).ReadAsArray()
    rows, cols = np.where(mas == 0)
    stacki[rows, cols, :] = -9999

    evi_list.append(stacki[:, :, 0])
    ndvi_list.append(stacki[:, :, 1])

# write raster
gtiff_driver = gdal.GetDriverByName('GTiff')
dummy  = gdal.Open(select[0])
dt     = dummy.GetRasterBand(1).DataType
out_ds = gtiff_driver.Create('Y:/_students_data_exchange/FP_FP/RS_Data/MODIS/for_matthias_python_map/EVI_DryChaco.tif', mas.shape[1], mas.shape[0], len(evi_list), dt)
out_ds.SetGeoTransform(list(dummy.GetGeoTransform()))
out_ds.SetProjection(dummy.GetProjection())
for i in range(0, len(evi_list)):
    out_ds.GetRasterBand(i+1).WriteArray(evi_list[i])
    out_ds.GetRasterBand(i+1).SetNoDataValue(-9999)
del out_ds

gtiff_driver = gdal.GetDriverByName('GTiff')
dummy  = gdal.Open(select[0])
dt     = dummy.GetRasterBand(1).DataType
out_ds = gtiff_driver.Create('Y:/_students_data_exchange/FP_FP/RS_Data/MODIS/for_matthias_python_map/NDVI_DryChaco.tif', mas.shape[1], mas.shape[0], len(ndvi_list), dt)
out_ds.SetGeoTransform(list(dummy.GetGeoTransform()))
out_ds.SetProjection(dummy.GetProjection())
for i in range(0, len(ndvi_list)):
    out_ds.GetRasterBand(i+1).WriteArray(ndvi_list[i])
    out_ds.GetRasterBand(i+1).SetNoDataValue(-9999)
del out_ds