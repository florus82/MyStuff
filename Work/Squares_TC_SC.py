from FloppyToolZ.MasterFuncs import *

# landsat center coordinate --> UTM 20 S; epsg: 32720

# load plots
plots = ogr.Open('Y:/_students_data_exchange/FP_FP/Seafile/myLibrary/MSc/GIS_Data/PLots/merge/Combined_UTM20S.shp')
plot  = plots.GetLayer()

# sub = ['18-A','18-B','18-C','18-D']
# plot.SetAttributeFilter("UniqueID in {}".format(tuple(sub)))

#plot.SetAttributeFilter(None)
# load a sample landsat image
rasti = gdal.Open('Y:/_students_data_exchange/FP_FP/Seafile/myLibrary/MSc/GIS_Data/TC_SC_squares/landsat_20S.tif')
rast  = rasti.GetGeoTransform()
refX  = rast[0]
refY  = rast[3]
grid_size  = rast[1]
squareList = []
id_list    = []
poly_list  = []
dd_storX   = []
dd_storY   = []

for z, feat in enumerate(plot):
    geomX = feat.geometry().GetX()
    geomY = feat.geometry().GetY()

    # finding close center coordinate
    Xstart = refX - (math.floor((refX - geomX) / grid_size) * 30) - 15
    Ystart = refY - (math.floor((refY - geomY) / grid_size) * 30) - 15


    refP = {'X': [Xstart], 'Y': [Ystart]}
    bb   = ApplySnake(refP, grid_size, BuildSnake(1))
    cc   = boundingCentroidCoord(bb['X'], bb['Y'], grid_size)

    dd = {**bb, **cc}

    for i in range(len(dd['X'])):
        xcheck = [j for j, e in enumerate(dd_storX) if e == dd['ulX'][i]]
        ycheck = [j for j, e in enumerate(dd_storY) if e == dd['ulY'][i]]
        print(xcheck)
        print(ycheck)
        print(i)
        lap = [a1 for a1 in xcheck for b1 in ycheck if a1 == b1]
        if (len(xcheck) is not 0 and len(ycheck) is not 0) and len(lap)>0:
            print('continue')
            continue
        else:
            id_list.append(feat.GetField('UniqueID'))
            poly_list.append(i)
            ring = ogr.Geometry(ogr.wkbLinearRing)
            ring.AddPoint(dd['ulX'][i], dd['ulY'][i])
            ring.AddPoint(dd['urX'][i], dd['urY'][i])
            ring.AddPoint(dd['lrX'][i], dd['lrY'][i])
            ring.AddPoint(dd['llX'][i], dd['llY'][i])
    
            square = ogr.Geometry(ogr.wkbPolygon)
            square.AddGeometry(ring)
            square.CloseRings()
            squareList.append(square)
            dd_storX.append(dd['ulX'][i])
            dd_storY.append(dd['ulY'][i])

# create empty dataset
#ShapeKiller('Y:/_students_data_exchange/FP_FP/Seafile/myLibrary/MSc/GIS_Data/TC_SC_squares/test/test_all3.shp')

driver = ogr.GetDriverByName('ESRI Shapefile')
shapeStor = driver.CreateDataSource('Y:/_students_data_exchange/FP_FP/Seafile/myLibrary/MSc/GIS_Data/TC_SC_squares/')
out_lyr = shapeStor.CreateLayer('combined_plots', getSpatRefVec(plot), ogr.wkbPolygon)

# create fields
#FID
id_fld = ogr.FieldDefn('UniqueID', ogr.OFTString)
id_fld.SetWidth(10)
id_fld.SetPrecision(1)
out_lyr.CreateField(id_fld)

# Poly ID
id_fld.SetName('Poly_ID')
out_lyr.CreateField(id_fld)


out_feat = ogr.Feature(out_lyr.GetLayerDefn())

for i, poly in enumerate(squareList):
    out_feat.SetGeometry(poly)
    out_feat.SetField(0, id_list[i])  # FID
    out_feat.SetField(1, poly_list[i])  # Block_ID
    #out_feat.SetField(2, i)  # Poly_ID
    #out_feat.SetField(3, nam)  # PA Name
    out_lyr.CreateFeature(out_feat)

shapeStor.Destroy()


# load file and store as kml
resi = ogr.Open('Y:/_students_data_exchange/FP_FP/Seafile/myLibrary/MSc/GIS_Data/TC_SC_squares/combined_plots.shp')
resi_lyr = resi.GetLayer()

driver = ogr.GetDriverByName('KML')
shapeStor = driver.CreateDataSource('Y:/_students_data_exchange/FP_FP/Seafile/myLibrary/MSc/GIS_Data/TC_SC_squares/combined_plots.kml')
out_lyr = shapeStor.CreateLayer('combined_plots', resi_lyr.GetSpatialRef(), ogr.wkbPolygon)

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