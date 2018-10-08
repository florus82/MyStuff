from FloppyToolZ.Funci import *

img = '/home/florus/MSc/RS_Data/LANDSAT/LE072300752007110901T1-SC20180622115313/LE07_L1TP_230075_20071109_20161231_01_T1_sr_band1.tif'

rastersubbyCord(img, 471000, -2395000, 479000, -2401000,'/home/florian/MSc/GEE/Landsat_Test3')

sub = '/home/florus/MSc/GEE/Landsat_Test3/LE07_L1TP_230075_20071109_20161231_01_T1_sr_band1_subby.tif'

in_ds = gdal.Open(sub)
in_gt = in_ds.GetGeoTransform()

proj = osr.SpatialReference(wkt=in_ds.GetProjection())
epsg = int(proj.GetAttrValue('AUTHORITY',1))


Xarr   = np.zeros((in_ds.RasterYSize, in_ds.RasterXSize), dtype=np.float)
Yarr   = np.zeros((in_ds.RasterYSize, in_ds.RasterXSize), dtype=np.float)

k = ['X', 'Y']
v = [[], []]
res = dict(zip(k, v))

res1 = dict.fromkeys(['POINT_ID'])
res1['POINT_ID'] = [i for i in range(in_ds.RasterXSize*in_ds.RasterYSize)]

ShapeKiller('/home/florian/MSc/GEE/Landsat_Test/center_test.shp')

for row in range(in_ds.RasterYSize):
    for col in range(in_ds.RasterXSize):
        res['X'].append((in_gt[0] + in_gt[1] * col) + in_gt[1] / 3)
        res['Y'].append((in_gt[3] + in_gt[5] * row) + in_gt[5] / 3)


XYtoShape(res, res1, epsg, '/home/florian/MSc/GEE/Landsat_Test3/', 'Shift', 'point')
reprojShape('/home/florian/MSc/GEE/Landsat_Test3/Shift.shp',4326)