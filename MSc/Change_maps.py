from FloppyToolZ.MasterFuncs import *

def getRange(x):
    mini = np.nanmin(x)
    maxi = np.nanmax(x)
    xx = maxi - mini
    return xx

BM_path = '/home/florus/Seafile/myLibrary/MSc/Modelling/GAP_FILLED/Single_VIs/prediction/Mosaic/check/masked'
# load BM-Maps
BMs = getFilelist(BM_path, '.tif')
BMs.sort()
BMs = BMs[0:4]

# load and stack em
bm_cont = []
for b in BMs:
    b1 = gdal.Open(b)
    b2 = b1.GetRasterBand(1).ReadAsArray()
    b2[b2 == -9999] = np.nan
    bm_cont.append(b2)
bmsta = np.dstack(bm_cont)

# get range and write away
bm_range = np.apply_along_axis(getRange, 2, bmsta)

gtiff_driver = gdal.GetDriverByName('GTiff')
out_ds = gtiff_driver.Create(BM_path + '/BM_RANGE.tiff', b1.RasterXSize, b1.RasterYSize, 1, gdal.GDT_Float32)
out_ds.SetGeoTransform(b1.GetGeoTransform())
out_ds.SetProjection(b1.GetProjection())
bm_range[bm_range == np.nan] = -9999
out_ds.GetRasterBand(1).WriteArray(bm_range)
out_ds.GetRasterBand(1).SetNoDataValue(-9999)

del out_ds