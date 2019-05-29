from FloppyToolZ.Funci import *


file = 'Y:/_students_data_exchange/FP_FP/Seafile/myLibrary/MSc/2nd_round/plot_coords/Combined_cont_gasp1_centerCoord_MODIS_ordered_XY.shp'
id_fields = 'UniqueID'
storpath = 'Y:/_students_data_exchange/FP_FP/Seafile/myLibrary/MSc/2nd_round/plot_coords'

grid = 10

if os.path.isfile(storpath + '/' + file.split('/')[-1].split('.')[0] + '_snaked_' + str(grid) + '.shp'):
    os.remove(storpath + '/' + file.split('/')[-1].split('.')[0] + '_snaked_' + str(grid) + '.shp')
    os.remove(storpath + '/' + file.split('/')[-1].split('.')[0] + '_snaked_' + str(grid) + '.shx')
    os.remove(storpath + '/' + file.split('/')[-1].split('.')[0] + '_snaked_' + str(grid) + '.prj')
    os.remove(storpath + '/' + file.split('/')[-1].split('.')[0] + '_snaked_' + str(grid) + '.dbf')


b1     = ogr.Open(file)
b1l    = b1.GetLayer()
out_SPRef = osr.SpatialReference()
out_SPRef.ImportFromEPSG(4326)

# create shapefile
driver = ogr.GetDriverByName('ESRI Shapefile')
shapeStor = driver.CreateDataSource(storpath)
out_lyr = shapeStor.CreateLayer(file.split('/')[-1].split('.')[0] + '_snaked_' + str(grid), out_SPRef, ogr.wkbPoint)
# create fields
id_fld = ogr.FieldDefn('POINT_ID', ogr.OFTString)
out_lyr.CreateField(id_fld)
id_fld.SetName('Block_ID')
out_lyr.CreateField(id_fld)

out_feat = ogr.Feature(out_lyr.GetLayerDefn())

pointList = []


feat = b1l.GetNextFeature()

while feat:
    if(feat.GetField('Dups') == 'N'):
        geom = feat.geometry()
        poi = dict.fromkeys('X', 'Y')
        poi['X'] = [geom.GetX()]
        poi['Y'] = [geom.GetY()]
        poin = ApplySnake(poi, grid, BuildSnake(12))
        for i in range(len(poin['X'])):
            point = ogr.Geometry(ogr.wkbPoint)
            point.AddPoint(poin['X'][i], poin['Y'][i])
            transF2 = osr.CoordinateTransformation(getSpatRefVec(b1), out_SPRef)
            point.Transform(transF2)
            out_feat.SetGeometry(point)
            #out_feat.SetField(0, str(feat.GetField(id_fields)))
            out_feat.SetField(0, feat.GetField(id_fields))
            out_feat.SetField(1, i)
            out_lyr.CreateFeature(out_feat)
        feat = b1l.GetNextFeature()
    else:
        feat = b1l.GetNextFeature()

b1l.ResetReading()
shapeStor.Destroy()
del b1