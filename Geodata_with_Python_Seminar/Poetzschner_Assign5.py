from osgeo import ogr, osr
import os
import math
import random

# def reprojShape(file, epsg):
#     # create spatial reference object
#     sref  = osr.SpatialReference()
#     sref.ImportFromEPSG(epsg)
#     # open the shapefile
#     ds = ogr.Open(file, 1)
#     driv = ogr.GetDriverByName('ESRI Shapefile')  # will select the driver foir our shp-file creation.
#
#     shapeStor = driv.CreateDataSource('/'.join(file.split('/')[:-1]))
#     # get first layer (assuming ESRI is standard) & and create empty output layer with spatial reference plus object type
#     in_lyr = ds.GetLayer()
#     out_lyr = shapeStor.CreateLayer(file.split('/')[-1].split('.')[0] + '_reproj_' + str(epsg), sref, in_lyr.GetGeomType())
#
# # create attribute field
#     out_lyr.CreateFields(in_lyr.schema)
#     # with attributes characteristics
#     out_feat = ogr.Feature(out_lyr.GetLayerDefn())
#
#     for in_feat in in_lyr:
#         geom = in_feat.geometry().Clone()
#         geom.TransformTo(sref)
#         out_feat.SetGeometry(geom)
#         for i in range(in_feat.GetFieldCount()):
#             out_feat.SetField(i, in_feat.GetField(i))
#         out_lyr.CreateFeature(out_feat)
#     shapeStor.Destroy()
#     del ds
#     return()
#
# # apply reprojection
# reprojShape('/home/florian/Geodata_with_Python/session6/Assignment05 - data/gadm36_GERonly.shp', 3035)
# reprojShape('/home/florian/Geodata_with_Python/session6/Assignment05 - data/WDPA_May2018_polygons_GER_select10large.shp', 3035)
# reprojShape('/home/florian/Geodata_with_Python/session6/Assignment05 - data/OnePoint.shp', 3035)

# load the shapes
poi = ogr.Open('/home/florian/Geodata_with_Python/session6/Assignment05 - data/OnePoint_reproj_3035.shp', 0)
PAs = ogr.Open('/home/florian/Geodata_with_Python/session6/Assignment05 - data/WDPA_May2018_polygons_GER_select10large_reproj_3035.shp')


# get reference coordinates
poiL = poi.GetLayer()
poiF = poiL.GetFeature(0)
refX = poiF.geometry().GetX()
refY = poiF.geometry().GetY()

# set grid size
grid_size = 30

# function for creating a list of functions that describe a 'snake' around center with order being the number of outer curls
k = ['X', 'Y']
v = [[], []]
r = dict(zip(k, v))

r['X'].append(refX)
r['Y'].append(refY)


def goleft(dicti, gs):
    dicti['X'].append(dicti['X'][-1] - gs)
    dicti['Y'].append(dicti['Y'][-1])
    return dicti

def goup(dicti, gs):
    dicti['X'].append(dicti['X'][-1])
    dicti['Y'].append(dicti['Y'][-1] + gs)
    return dicti

def goright(dicti, gs):
    dicti['X'].append(dicti['X'][-1] + gs)
    dicti['Y'].append(dicti['Y'][-1])
    return dicti

def godown(dicti, gs):
    dicti['X'].append(dicti['X'][-1])
    dicti['Y'].append(dicti['Y'][-1] - gs)
    return dicti


def BuildSnake(order):
    def goleft(dicti, gs):
        dicti['X'].append(dicti['X'][-1] - gs)
        dicti['Y'].append(dicti['Y'][-1])
        return dicti

    def goup(dicti, gs):
        dicti['X'].append(dicti['X'][-1])
        dicti['Y'].append(dicti['Y'][-1] + gs)
        return dicti

    def goright(dicti, gs):
        dicti['X'].append(dicti['X'][-1] + gs)
        dicti['Y'].append(dicti['Y'][-1])
        return dicti

    def godown(dicti, gs):
        dicti['X'].append(dicti['X'][-1])
        dicti['Y'].append(dicti['Y'][-1] - gs)
        return dicti

    fL = list()
    for i in range(order):
        ordi = i + 1
        fdum = [[goleft], (2* ordi -1) * [goup], 2 * ordi * [goright], 2 * ordi * [godown], 2 * ordi * [goleft]]
        fL.append(fdum)
    ffL = [subitem for sublist in fL for item in sublist for subitem in item]
    return ffL


def ApplySnake(dict, gridsiz, snaki):
    for i in snaki:
        res = i(dict, gridsiz)
    return res


# ## function centroid to polygon


def boundingCentroidCoord(X, Y, celldim):
    if type(X) is not list:
        XX, YY = [X], [Y]
    else:
        XX, YY = X, Y
    k = ['ulX', 'ulY', 'urX', 'urY', 'lrX', 'lrY', 'llX', 'llY']
    v = [[], [], [], [], [], [], [], []]
    res = dict(zip(k, v))
    for i in XX:

        res['ulX'].append(i - celldim/2)
        res['urX'].append(i + celldim/2)
        res['lrX'].append(i + celldim/2)
        res['llX'].append(i - celldim/2)

    for j in YY:
        res['ulY'].append(j + celldim / 2)
        res['urY'].append(j + celldim / 2)
        res['lrY'].append(j - celldim / 2)
        res['llY'].append(j - celldim / 2)

    return res

if os.path.isfile('/home/florian/Geodata_with_Python/session6/test/50perPA.shp'):
   os.remove('/home/florian/Geodata_with_Python/session6/test/50perPA.shp')
   os.remove('/home/florian/Geodata_with_Python/session6/test/50perPA.shx')
   os.remove('/home/florian/Geodata_with_Python/session6/test/50perPA.prj')
   os.remove('/home/florian/Geodata_with_Python/session6/test/50perPA.dbf')

# create empty dataset
sref = osr.SpatialReference()
sref.ImportFromEPSG(3035)

driver = ogr.GetDriverByName('ESRI Shapefile')
shapeStor = driver.CreateDataSource('/home/florian/Geodata_with_Python/session6/test')
out_lyr = shapeStor.CreateLayer('50perPA', sref, ogr.wkbPolygon)

# create fields
#FID
id_fld = ogr.FieldDefn('FID', ogr.OFTInteger)
id_fld.SetWidth(10)
id_fld.SetPrecision(1)
out_lyr.CreateField(id_fld)
# Block ID
id_fld.SetName('Block_ID')
out_lyr.CreateField(id_fld)
# Poly ID
id_fld.SetName('Poly_ID')
out_lyr.CreateField(id_fld)
# PA NAme
nam_fld = ogr.FieldDefn('PA_Name', ogr.OFTString)
nam_fld.SetWidth(50)
out_lyr.CreateField(nam_fld)

out_feat = ogr.Feature(out_lyr.GetLayerDefn())


# fill dataset with build functions on randomly drawn locations within PA's features' extents
PAsL = PAs.GetLayer()
for z, feat in enumerate(PAsL):
    nam = feat.GetField('NAME')
    geom = feat.geometry()
    ext = geom.GetEnvelope()

    # finding x sequence
    Xseq_start = refX - (math.floor((refX - ext[0]) / grid_size) * 30)
    Xseq_end   = refX - (math.ceil((refX - ext[1]) / grid_size) * 30)
    # finding y sequence
    Yseq_start = refY - (math.floor((refY - ext[2]) / grid_size) * 30)
    Yseq_end   = refY - (math.ceil((refY - ext[3]) / grid_size) * 30)

    success = 0
    megasquares = ogr.Geometry(ogr.wkbMultiPolygon)
    while success < 50:
        #random.seed(130)
        print(success)
        ranX = (random.choice(range(int(Xseq_start*10000000000), int(Xseq_end*10000000000), int(grid_size*10000000000)))) / 10000000000
        ranY = (random.choice(range(int(Yseq_start*10000000000), int(Yseq_end*10000000000), int(grid_size*10000000000)))) / 10000000000

        ranPoi = {'X': [ranX], 'Y': [ranY]}
        bb = ApplySnake(ranPoi, grid_size, BuildSnake(1))
        cc = boundingCentroidCoord(bb['X'], bb['Y'], grid_size)

        dd = {**bb, **cc}

        # then put corners into polygons
        squareList = []

        for i in range(len(dd['X'])):
            ring = ogr.Geometry(ogr.wkbLinearRing)
            ring.AddPoint(dd['ulX'][i], dd['ulY'][i])
            ring.AddPoint(dd['urX'][i], dd['urY'][i])
            ring.AddPoint(dd['lrX'][i], dd['lrY'][i])
            ring.AddPoint(dd['llX'][i], dd['llY'][i])

            square = ogr.Geometry(ogr.wkbPolygon)
            square.AddGeometry(ring)
            square.CloseRings()
            squareList.append(square)

        TF = []
        TFm = []
        for sq in squareList:
            TF.append(sq.Within(geom))

        if (len(set(TF))== 1) and (set(TF)== {True}):
            if success == 0:
                for sq in squareList:
                    megasquares.AddGeometry(sq)
                for i, poly in enumerate(squareList):
                    out_feat.SetGeometry(poly)
                    out_feat.SetField(0, i + (success * 9) + (z * 450))  # FID
                    out_feat.SetField(1, success + 1)  # Block_ID
                    out_feat.SetField(2, i)  # Poly_ID
                    out_feat.SetField(3, nam)  # PA Name
                    out_lyr.CreateFeature(out_feat)
                success = success + 1
            else:  # check if squares overlap with other randomly creates squares
                for sq in squareList:
                    TFm.append(sq.Intersects(megasquares))
                if (len(set(TFm))==1) and (set(TFm)=={False}):
                    for sq in squareList:
                        megasquares.AddGeometry(sq)
                    for i, poly in enumerate(squareList):
                        out_feat.SetGeometry(poly)
                        out_feat.SetField(0, i + (success*9) + (z*450)) # FID
                        out_feat.SetField(1, success + 1) # Block_ID
                        out_feat.SetField(2, i) # Poly_ID
                        out_feat.SetField(3, nam) # PA Name
                        out_lyr.CreateFeature(out_feat)
                    success = success + 1
    print(nam)
shapeStor.Destroy()




## load file and store as kml
resi = ogr.Open('/home/florian/Geodata_with_Python/session6/test/50perPA.shp')
resi_lyr = resi.GetLayer()

driver = ogr.GetDriverByName('KML')
shapeStor = driver.CreateDataSource('/home/florian/Geodata_with_Python/session6/test/50perPA.kml')
out_lyr = shapeStor.CreateLayer('50perPA_GE', resi_lyr.GetSpatialRef(), ogr.wkbPolygon)

out_lyr.CreateFields(resi_lyr.schema)

out_feat = ogr.Feature(out_lyr.GetLayerDefn())

for in_feat in resi_lyr:
    geom = in_feat.geometry().Clone()
    out_feat.SetGeometry(geom)
    for i in range(in_feat.GetFieldCount()):
        out_feat.SetField(i, in_feat.GetField(i))
    out_lyr.CreateFeature(out_feat)
shapeStor.Destroy()
del resi


### zipp shape

import zipfile

zf = zipfile.ZipFile('/home/florian/Geodata_with_Python/session6/test/50perPA.zip', mode='w')
orig_wd = os.getcwd()
os.chdir('/home/florian/Geodata_with_Python/session6/test/')
zf.write('50perPA.shx')
zf.write('50perPA.shp')
zf.write('50perPA.prj')
zf.write('50perPA.dbf')

zf.close()

os.chdir(orig_wd)

