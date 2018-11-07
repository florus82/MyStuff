from FloppyToolZ.MasterFuncs import *

path = '/home/florus/MSc/RS_Data/MODIS/rasterized'
tiles = getFilelist(path,'.tiff')
# get resolution --> should build in a check for resolution consistency
sc = gdal.Open(tiles[2])
sc_b = sc.GetRasterBand(1)
gt = sc.GetGeoTransform()

Xmin = [getExtentRas(t)['Xmin'] for t in tiles]
Xmax = [getExtentRas(t)['Xmax'] for t in tiles]
Ymin = [getExtentRas(t)['Ymin'] for t in tiles]
Ymax = [getExtentRas(t)['Ymax'] for t in tiles]

xoff = abs(int((max(Xmax) - min(Xmin)) / gt[5]))

yoff = abs(int((max(Ymax) - min(Ymin)) / gt[5]))


# make mosaic
gtiff_driver = gdal.GetDriverByName('GTiff')
out_ds = gtiff_driver.Create(path + '/Mosaic.tif', xoff, yoff, 1, sc.GetRasterBand(1).DataType)
out_gt = list(gt)
out_gt[0], out_gt[3] = min(Xmin), max(Ymax)
out_ds.SetGeoTransform(out_gt)
out_ds.SetProjection(sc.GetProjection())

# fill the array
data = np.zeros((yoff, xoff), dtype='float64')

for til in tiles:
    print(til)
    ti = gdal.Open(til)
    in_gt = ti.GetGeoTransform()
    col_off = abs(int((out_gt[0] - in_gt[0]) / out_gt[5]))
    row_off = abs(int((out_gt[3] - in_gt[3]) / out_gt[5]))
    data[row_off : (row_off + ti.RasterYSize) , col_off : (col_off + ti.RasterXSize)] = ti.GetRasterBand(1).ReadAsArray()

data[data==0] = -9999
out_ds.GetRasterBand(1).WriteArray(data)
out_ds.GetRasterBand(1).SetNoDataValue(-9999)

del out_ds
