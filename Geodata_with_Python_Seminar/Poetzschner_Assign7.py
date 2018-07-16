from osgeo import ogr, osr
import gdal
import os
import struct
import pandas as pd

# asstert isinstance()

def getFilelist(originpath, ftyp):
    files = os.listdir(originpath)
    out   = []
    for i in files:
        if i.split('.')[-1] in ftyp:
            if originpath.endswith('/'):
                out.append(originpath + i)
            else:
                out.append(originpath + '/' + i)
        else:
            print("non-matching file - {} - found".format(i.split('.')[-1]))
    return out


def getAttributes(layer):

    # check the type of layer
    if type(layer) is ogr.Layer:
        lyr = layer

    elif type(layer) is ogr.DataSource:
        lyr = layer.GetLayer(0)

    elif type(layer) is str:
        lyrOpen = ogr.Open(layer)
        lyr = lyrOpen.GetLayer(0)

    # create empty dict and fill it
    header = dict.fromkeys(['Name', 'Type'])
    head   = [[lyr.GetLayerDefn().GetFieldDefn(n).GetName(),
             ogr.GetFieldTypeName(lyr.GetLayerDefn().GetFieldDefn(n).GetType())]
            for n in range(lyr.GetLayerDefn().GetFieldCount())]

    header['Name'], header['Type'] = zip(*head)

    return header


def getSpatRefRas(layer):
    # check type of layer
    if type(layer) is gdal.Dataset:
        SPRef = osr.SpatialReference()
        SPRef.ImportFromWkt(layer.GetProjection())

    elif type(layer) is str:
        lyr   = gdal.Open(layer)
        SPRef = osr.SpatialReference()
        SPRef.ImportFromWkt(lyr.GetProjection())

    #print(SPRef)
    return(SPRef)


def getSpatRefVec(layer):

    # check the type of layer
    if type(layer) is ogr.Geometry:
        SPRef   = layer.GetSpatialReference()

    elif type(layer) is ogr.Feature:
        lyrRef  = layer.GetGeometryRef()
        SPRef   = lyrRef.GetSpatialReference()

    elif type(layer) is ogr.Layer:
        SPRef   = layer.GetSpatialRef()

    elif type(layer) is ogr.DataSource:
        lyr     = layer.GetLayer(0)
        SPRef   = lyr.GetSpatialRef()

    elif type(layer) is str:
        lyrOpen = ogr.Open(layer)
        lyr     = lyrOpen.GetLayer(0)
        SPRef   = lyr.GetSpatialRef()

    #print(SPRef)
    return(SPRef)


def getHexType(raster):
    if type(raster) is str:
        ras    = gdal.Open(raster)
        rasti  = ras.GetRasterBand(1)
        ras_DT = rasti.DataType

    elif type(raster) is gdal.Dataset:
        rasti  = raster.GetRasterBand(1)
        ras_DT = rasti.DataType

    if type(raster) is gdal.Band:
        ras_DT = raster.DataType

    gdals = [1,2,3,4,5,6,7]
    hexas = ['b', 'H', 'h', 'I', 'i', 'f', 'd']
    lookUp = dict(zip(gdals, hexas))

    hexa = []
    for k ,v in lookUp.items():
        if k == ras_DT:
            hexa = lookUp[k]
    return hexa


def getRasCellFromXY(X, Y, rasterpath):
    ras = gdal.Open(rasterpath)
    gt  = ras.GetGeoTransform()
    col = int((X - gt[0]) / gt[1])
    row = int((Y - gt[3]) / gt[5])
    return([col, row])

path = '/home/florian/Geodata_with_Python/session8/Assignment07_data'

# get all the files for the assignment
files = getFilelist(path, ['tif', 'shp'])
# get the attribute name for the point layer
print(getAttributes(files[3]))

# get the points ready for looping
po       = ogr.Open(files[3])
in_SPRef = getSpatRefVec(files[3])
poi      = po.GetLayer(0)
poin     = poi.GetNextFeature()

# create output dict for panda-power-export
keys = ['Point ID', 'Variable', 'Value']
vals = [[], [], []]
res  = dict(zip(keys, vals))

# create order lists for easy looping
file_order = [files[0], files[1], files[2], files[4]]
func_order = [getSpatRefRas, getSpatRefVec, getSpatRefRas, getSpatRefVec]
name_order = ['Elevation', 'Private', 'Road_Dist', 'OldGrowth']

# tracker for debugging
count = 0
# do the loop
while poin:
    print(count)
    # for every layer a point extracts from
    for i in range(4):
        # fill point id and variable for every iteration
        res['Point ID'].append(poin.GetField('Id'))
        res['Variable'].append(name_order[i])
        # reproject point in order to match the respective layer's projection
        point = poin.geometry().Clone() # to reset the transformation from prior iteration
        out_SPRef = func_order[i](file_order[i])
        transF = osr.CoordinateTransformation(in_SPRef, out_SPRef)
        point.Transform(transF)
        # different procedure for raster files
        if i in [0,2]:
            cell = getCellFromXY(point.GetX(), point.GetY(), file_order[i])
            ras = gdal.Open(file_order[i])
            rasti = ras.GetRasterBand(1)
            hex = rasti.ReadRaster(cell[0], cell[1], 1, 1)
            res['Value'].append(str(round(struct.unpack(getHexType(ras), hex)[0], 2)))
        # different procedure for vector files
        elif i in [1,3]:
            sha = ogr.Open(file_order[i])
            shap = sha.GetLayer()
            shap.SetSpatialFilter(point)
            if len(shap) == 0:
                res['Value'].append(str(0))
            else:
                res['Value'].append(str(1))
    poin = poi.GetNextFeature() # next point
    count += 1 # increase tracker
poi.ResetReading() # reset the feature count

# panda-power export after sorting by 'Variable' according to panel requirements
df    = pd.DataFrame(data = res)
sorti = ['Private', 'OldGrowth', 'Elevation', 'Road_Dist']
df['Variable'] = df['Variable'].astype('category')
df['Variable'].cat.set_categories(sorti, inplace=True)
df   = df.sort_values(by=['Point ID', 'Variable'])

df.to_csv('/home/florian/Geodata_with_Python/session8/Poetzschner_Assign_7.csv', sep=',',index=False)
