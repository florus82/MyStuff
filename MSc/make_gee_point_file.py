from FloppyToolZ.Funci import *

#
# file = '/home/florian/MSc/Biomass data/FP_MB/Conti/Conti-etal_BiomassData_withInfo_modID_and_BM.shp'
# id_fields = 'Changed_ID'


file = '//home/florian/MSc/Biomass data/FP_MB/Gasparri_DryChaco/parcelas.shp'
id_fields = 'conglomera'
id_fields2 = 'PLOT'
storpath = '/home/florian/MSc/GEE/9Points'

grid = 250

if os.path.isfile(storpath + '/' + file.split('/')[-1].split('.')[0] + '_9Points_' + str(grid) + '.shp'):
    os.remove(storpath + '/' + file.split('/')[-1].split('.')[0] + '_9Points_' + str(grid) + '.shp')
    os.remove(storpath + '/' + file.split('/')[-1].split('.')[0] + '_9Points_' + str(grid) + '.shx')
    os.remove(storpath + '/' + file.split('/')[-1].split('.')[0] + '_9Points_' + str(grid) + '.prj')
    os.remove(storpath + '/' + file.split('/')[-1].split('.')[0] + '_9Points_' + str(grid) + '.dbf')


b1     = ogr.Open(file)
b1l    = b1.GetLayer()


# create shapefile
driver = ogr.GetDriverByName('ESRI Shapefile')
shapeStor = driver.CreateDataSource(storpath)
out_lyr = shapeStor.CreateLayer(file.split('/')[-1].split('.')[0] + '_9Points_' + str(grid), getSpatRefVec(b1), ogr.wkbPoint)
# create fields
id_fld = ogr.FieldDefn('POINT_ID', ogr.OFTString)
out_lyr.CreateField(id_fld)
id_fld.SetName('Block_ID')
out_lyr.CreateField(id_fld)
out_feat = ogr.Feature(out_lyr.GetLayerDefn())

pointList = []


feat = b1l.GetNextFeature()
out_SPRef = osr.SpatialReference()
out_SPRef.ImportFromEPSG(3035)


while feat:
    geom = feat.geometry()
    transF = osr.CoordinateTransformation(getSpatRefVec(feat), out_SPRef)
    geom.Transform(transF)
    poi = dict.fromkeys('X', 'Y')
    poi['X'] = [geom.GetX()]
    poi['Y'] = [geom.GetY()]
    poin = ApplySnake(poi, grid, BuildSnake(1))
    for i in range(len(poin['X'])):
        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint(poin['X'][i], poin['Y'][i])
        transF2 = osr.CoordinateTransformation(out_SPRef, getSpatRefVec(b1))
        point.Transform(transF2)
        out_feat.SetGeometry(point)
        #out_feat.SetField(0, str(feat.GetField(id_fields)))
        out_feat.SetField(0, str(feat.GetField(id_fields))+ feat.GetField(id_fields2))
        out_feat.SetField(1, i)
        out_lyr.CreateFeature(out_feat)
    feat = b1l.GetNextFeature()

b1l.ResetReading()
shapeStor.Destroy()
del b1