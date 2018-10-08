from FloppyToolZ.Funci import *

# read data
files = getFilelist('/home/florus/Desktop/bison_poland','.shp')

gri  = ogr.Open(files[0])
biso = ogr.Open(files[1])

grid  = gri.GetLayer()
bison = biso.GetLayer()

# create a copy of grid
driver    = ogr.GetDriverByName('ESRI Shapefile')
shapeStor = driver.CreateDataSource('/home/florus/Desktop/bison_poland')
out_lyr   = shapeStor.CreateLayer('grid_bison', getSpatRefVec(grid), ogr.wkbPolygon)
out_lyr.CreateFields(grid.schema)
# create new attribute fields
id_fld = ogr.FieldDefn('Presence', ogr.OFTInteger)
id_fld.SetWidth(10)
id_fld.SetPrecision(1)
out_lyr.CreateField(id_fld)

id_fld.SetName('Count')
out_lyr.CreateField(id_fld)

out_feat = ogr.Feature(out_lyr.GetLayerDefn())


for square in grid:
    dum = square.geometry().Clone()
    out_feat.SetGeometry(dum)
    out_feat.SetField(0, square.GetField('CellCode'))
    out_feat.SetField(1, square.GetField('Region'))
    out_feat.SetField(2, square.GetField('ESRI_OID'))
    bison.SetSpatialFilter(dum)
    if len(bison) == 0:
        out_feat.SetField(3, 0)
        out_feat.SetField(4, 0)
    else:
        out_feat.SetField(3, 1)
        out_feat.SetField(4, len(bison))
    bison.SetSpatialFilter(None)
    out_lyr.CreateFeature(out_feat)
grid.ResetReading()

shapeStor.Destroy()