from FloppyToolZ.MasterFuncs import *

rasterpath = 'Y:/_students_data_exchange/FP_FP/LS_CHACO_WC_2015_FINAL_1KM_WETDRY_CHACO_int_No0.tif'
oldL = [2, 3, 4, 5, 6, 7, 200, 105, 10, 104, 8, 9, 110, 15, 112, 255]
newL = [1, 2, 3, 4, 5, 6, 199, 104, 9, 103, 7, 8, 109, 14, 111, 255]

ras  = gdal.Open(rasterpath)
data = ras.GetRasterBand(1)
out_data = data.ReadAsArray()

keys = oldL
vals = newL
res  = dict(zip(keys, vals))

for k, v in sorted(res.items()):
    out_data[out_data == k] = v


gtiff_driver = gdal.GetDriverByName('GTiff')
out_ds = gtiff_driver.Create(('/').join(rasterpath.split('/')[:-1]) + '/' + rasterpath.split('/')[-1].split('.')[0] + '_reclassified.tif',
             ras.RasterXSize, ras.RasterYSize, 1, ras.GetRasterBand(1).DataType)
out_ds.SetGeoTransform(ras.GetGeoTransform())
out_ds.SetProjection(ras.GetProjection())
out_ds.GetRasterBand(1).WriteArray(out_data)
out_ds.GetRasterBand(1).SetNoDataValue(data.GetNoDataValue())
del out_ds