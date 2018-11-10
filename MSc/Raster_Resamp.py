from FloppyToolZ.MasterFuncs import *

mos_path = 'Z:/_students_data_exchange/FP_FP/Seafile/myLibrary/MSc/other_biomass _maps/TC_SC'
mos = 'SC_Landsat-Sentinel.tif'
aa = gdal.Open(mos_path + '/' + mos)
bb = aa.GetRasterBand(1).ReadAsArray()
bb[bb == -9999] = np.nan
aggFac = 3

# check if raster has even dimenensions for cutting out 2x2 squaree
while bb.shape[0] / aggFac % 2 != 0:
    dd = np.empty((1, bb.shape[1]))
    dd.fill(np.nan)
    bb = np.concatenate([bb, dd])
while bb.shape[1] / aggFac % 2 != 0:
    dd = np.empty((bb.shape[0], 1))
    dd.fill(np.nan)
    bb = np.concatenate([bb, dd],axis=1)

# create empty array for aggregation output
arr = np.empty((int(bb.shape[0]/aggFac), int(bb.shape[1]/aggFac)))

for row in range(0, bb.shape[0], 2):
    for col in range(0,bb.shape[1], 2):
        arr[int(row/aggFac), int(col/aggFac)] = np.nanmean(bb[row:row+(aggFac-1), col:col+(aggFac-1)])

# write raster
gtiff_driver = gdal.GetDriverByName('GTiff')
out_ds = gtiff_driver.Create(('/').join(mos_path.split('/')[0:len(mos_path.split('/'))-1]) + '/resample/' +
                mos.split('.')[0] + 'resample_fac' + str(aggFac) +'.tif',
                             arr.shape[1], arr.shape[0], 1, aa.GetRasterBand(1).DataType)
out_gt = list(aa.GetGeoTransform())
out_gt[1], out_gt[5] = out_gt[1] * aggFac, out_gt[5]*aggFac
out_ds.SetGeoTransform(out_gt)
out_ds.SetProjection(aa.GetProjection())
out_ds.GetRasterBand(1).WriteArray(arr)
out_ds.GetRasterBand(1).SetNoDataValue(-9999)

del out_ds
