from FloppyToolZ.Funci import *
import struct
import datetime as dt
import pandas as pd

# import shapefiles with plot coordinates
parc_XY    = getXYfromShape('/home/florian/MSc/GIS_Data/Plots/gasparri/parcelas_reproj_102033.shp')
parc_Attri = getAttributesALL('/home/florian/MSc/GIS_Data/Plots/gasparri/parcelas_reproj_102033.shp')

# transform the coordinates into cell dimensions (all tiles are equal, therefore one is enough

dummy = '/home/florian/MSc/RS_Data/MODIS/GTiff/102033/EVI/MYD13Q1.A2008105.h12v11.006.2015173133721_EVI.tif'
k = ['col', 'row']
v = [[], []]
cells = dict(zip(k, v))
for i in range(len(parc_XY['X'])):
    cells['col'].append(getRasCellFromXY(parc_XY['X'][i], parc_XY['Y'][i], dummy)[0])
    cells['row'].append(getRasCellFromXY(parc_XY['X'][i], parc_XY['Y'][i], dummy)[1])

# get center coordinates from MODIS here --> transform cells.dict; again, all the same

dum = gdal.Open(dummy)
in_gt = dum.GetGeoTransform()

k = ['X', 'Y']
v = [[], []]
center = dict(zip(k, v))

for count in range(len(cells['col'])):
    center['X'].append((in_gt[0] + in_gt[1] * cells['col'][count]) + in_gt[1] / 2)
    center['Y'].append((in_gt[3] + in_gt[5] * cells['row'][count]) + in_gt[5] / 2)

# ## make a shape of centroids
# XYtoShape(center, parc_Attri, 102033, '/home/florian/MSc/GIS_Data/overlap', 'MODIS_center', 'point')
# squares = boundingCentroidCoord(center['X'], center['Y'], in_gt[1])
#
# XYtoShape(squares, parc_Attri, 102033, '/home/florian/MSc/GIS_Data/overlap', 'MODIS_centerPoly', 'poly')


NDVI = getFilelist('/home/florian/MSc/RS_Data/MODIS/GTiff/102033/NDVI','.tif')
EVI  = getFilelist('/home/florian/MSc/RS_Data/MODIS/GTiff/102033/EVI','.tif')
NBR  = getFilelist('/home/florian/MSc/RS_Data/MODIS/GTiff/102033/NBR','.tif')
NDVI.sort()
EVI.sort()
NBR.sort()


k = ['conglomera', 'PLOT', 'survey year', 'NDVI', 'EVI', 'NBR','AccDate','CellX','CellY']
v = [ [] for i in range(len(k)) ]
res = dict(zip(k, v))




for n, img in enumerate(NDVI):
    print(n)

    for i in range(len(cells['col'])):
        res['conglomera'].append(parc_Attri['conglomera'][i])
        res['PLOT'].append(parc_Attri['PLOT'][i])
        res['survey year'].append(parc_Attri['survey yea'][i])
        res['AccDate'].append(dt.datetime.strptime(img.split('.')[1][1:], '%Y%j').date())
        ras = gdal.Open(img)
        rasti = ras.GetRasterBand(1)
        hex = rasti.ReadRaster(cells['col'][i], cells['row'][i], 1, 1)
        res['NDVI'].append(struct.unpack(getHexType(ras), hex)[0])
        res['CellX'].append(cells['col'][i])
        res['CellY'].append(cells['row'][i])



for n, img in enumerate(EVI):
    print(n)

    for i in range(len(cells['col'])):
        ras = gdal.Open(img)
        rasti = ras.GetRasterBand(1)
        hex = rasti.ReadRaster(cells['col'][i], cells['row'][i], 1, 1)
        res['EVI'].append(struct.unpack(getHexType(ras), hex)[0])

for n, img in enumerate(NBR):
    print(n)

    for i in range(len(cells['col'])):
        ras = gdal.Open(img)
        rasti = ras.GetRasterBand(1)
        hex = rasti.ReadRaster(cells['col'][i], cells['row'][i], 1, 1)
        res['NBR'].append(struct.unpack(getHexType(ras), hex)[0])


df = pd.DataFrame(data = res)
df[df==10000] = np.NaN
df.to_csv('/home/florian/MSc/MOD_extr_test.csv', sep=',',index=False)