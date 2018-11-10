from FloppyToolZ.MasterFuncs import *

aa = gdal.Open('/home/florus/Seafile/myLibrary/MSc/Modelling/Single_VIs/prediction/Mod1/Mod1_EoS_Max.tif')
bb = aa.GetRasterBand(1).ReadAsArray()

aggFac = 2

# check if raster has even dimenensions for cutting out 2x2 squaree
if bb.shape[0] % 2 != 0:
    dd = np.empty((1, bb.shape[1]))
    dd.fill(np.nan)
    bb = np.concatenate([bb, dd])
if bb.shape[1] % 2 != 0:
    dd = np.empty((bb.shape[0], 1))
    dd.fill(np.nan)
    bb = np.concatenate([bb, dd],axis=1)

# create empty array for aggregation output
arr = np.empty((int(bb.shape[0]/2), int(bb.shape[1]/2)))

for row in range(0, bb.shape[0], 2):
    for col in range(0,bb.shape[1], 2):
        arr[int(row/aggFac), int(col/aggFac)] = np.nanmean(bb[row:row+(aggFac-1), col:col+(aggFac-1)])

# write raster
gtiff_driver = gdal.GetDriverByName('GTiff')
out_ds = gtiff_driver.Create('/home/florus/MSc/trash/resamp.tif', arr.shape[1], arr.shape[0], 1, aa.GetRasterBand(1).DataType)
out_gt = list(aa.GetGeoTransform())
out_gt[1], out_gt[5] = out_gt[1] * aggFac, out_gt[5]*aggFac
out_ds.SetGeoTransform(out_gt)
out_ds.SetProjection(aa.GetProjection())
out_ds.GetRasterBand(1).WriteArray(arr)
out_ds.GetRasterBand(1).SetNoDataValue(-9999)

del out_ds
