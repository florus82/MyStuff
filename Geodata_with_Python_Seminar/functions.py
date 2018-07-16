

def reprojShape(file, epsg):
    
    from osgeo import ogr, osr
    # create spatial reference object
    sref  = osr.SpatialReference()
    sref.ImportFromEPSG(epsg)
    # open the shapefile
    ds = ogr.Open(file, 1)
    driv = ogr.GetDriverByName('ESRI Shapefile')  # will select the driver foir our shp-file creation.

    shapeStor = driv.CreateDataSource('/'.join(file.split('/')[:-1]))
    # get first layer (assuming ESRI is standard) & and create empty output layer with spatial reference plus object type
    in_lyr = ds.GetLayer()
    out_lyr = shapeStor.CreateLayer(file.split('/')[-1].split('.')[0] + '_reproj_' + str(epsg), sref, in_lyr.GetGeomType())

# create attribute field
    out_lyr.CreateFields(in_lyr.schema)
    # with attributes characteristics
    out_feat = ogr.Feature(out_lyr.GetLayerDefn())

    for in_feat in in_lyr:
        geom = in_feat.geometry().Clone()
        geom.TransformTo(sref)
        out_feat.SetGeometry(geom)
        for i in range(in_feat.GetFieldCount()):
            out_feat.SetField(i, in_feat.GetField(i))
        out_lyr.CreateFeature(out_feat)

    shapeStor.Destroy()
    del ds
    return()



import os
import gdal
import numpy as np
import pandas


# ## get all files in a folder according to string of extension or a list of such strings


def getFilelist(originpath, ftyp):
    files = os.listdir(originpath)
    out = []
    for i in files:
        if i.split('.')[-1] in ftyp:
            if originpath.endswith('/'):
                out.append(originpath + i)
            else:
                out.append(originpath + '/' + i)
        else:
            print("non-matching file - {} - found".format(i.split('.')[-1]))
    return out


# ## get minmax values of x,y of a raster(path) or a list with raster (paths)


def getExtent(raster):
    if type(raster) is str:
        raster = [raster]
    else:
        raster = raster
    extL = []
    for i in raster:
        ds = gdal.Open(i)
        gt = ds.GetGeoTransform()
        ext = {'Xmin': gt[0],
                'Xmax': gt[0] + (gt[1] * ds.RasterXSize),
                'Ymin': gt[3] + (gt[5] * ds.RasterYSize),
                'Ymax': gt[3]}
        extL.append(ext)

    return extL


# ## get common bounding box dimensions for list of Extent_dictionaries


def commonBoundsDim(extentList):
    # create empty dictionary with list slots for corner coordinates
    k = ['Xmin', 'Xmax', 'Ymin', 'Ymax']
    v = [[], [], [], []]
    res = dict(zip(k, v))

    # fill it with values of all raster files
    for i in extentList:
        for j in k:
            res[j].append(i[j])
    # determine min or max values per values' list to get common bounding box
    ff = [max, min, max, min]
    for i, j in enumerate(ff):
        res[k[i]] = j(res[k[i]])
    return res


# ## get common bounding box coordinates for Extent_dictionaries


def commonBoundsCoord(ext):
    if type(ext) is dict:
        ext = [ext]
    else:
        ext = ext
    cooL = []
    for i in ext:
        coo = {'UpperLeftXY': [i['Xmin'], i['Ymax']],
               'UpperRightXY': [i['Xmax'], i['Ymax']],
               'LowerRightXY': [i['Xmax'], i['Ymin']],
               'LowerLeftXY': [i['Xmin'], i['Ymin']]}
        cooL.append(coo)
    return cooL

# ## read in one or multiple raster as one or multiple subsets based on coordinates
# ## optional: write away subsets and set NoData manually : only for single raster tiles at the moment!!!!!


def rastersubbyCord(raster,ULx,ULy,LRx,LRy,storpath='none', nodata='fromimage'):
    # check storpath
    if storpath is not 'none':
        if storpath.endswith('/'):
            storpath = storpath
        else:
            storpath = storpath + '/'
    # check if raster is list
    if type(raster) is str:
        raster = [raster]
    else:
         raster = raster
    k = ['Raster', 'ULx_off', 'ULy_off', 'LRx_off', 'LRy_off', 'Data']
    v = [[], [], [], [], [], []]
    res = dict(zip(k, v))

    for z, i in enumerate(raster):
        in_ds = gdal.Open(i)
        in_gt = in_ds.GetGeoTransform()
        inv_gt = gdal.InvGeoTransform(in_gt)
        # transform coordinates into offsets (in cells) and make them integer
        off_UpperLeft = gdal.ApplyGeoTransform(inv_gt, ULx,ULy)  # new UL * rastersize^-1  + original ul/rastersize(opposite sign
        off_LowerRight = gdal.ApplyGeoTransform(inv_gt, LRx, LRy)
        off_ULx, off_ULy = map(round, off_UpperLeft)  # or int????????????????
        off_LRx, off_LRy = map(round, off_LowerRight)

        in_band = in_ds.GetRasterBand(1)
        data = in_band.ReadAsArray(off_ULx, off_ULy, off_LRx - off_ULx, off_LRy - off_ULy)
        if storpath is not 'none':
            gtiff_driver = gdal.GetDriverByName('GTiff')
            out_ds = gtiff_driver.Create(storpath + (i.split('/')[-1]).split('.')[0] + '_subby.tif', off_LRx - off_ULx,
                                         off_LRy - off_ULy, 1, in_ds.GetRasterBand(1).DataType)
            # overwrite the GetGeoTransform information (coordinates of upper left cell) by transforming offset values back to coordinates
            out_gt = list(in_gt)
            out_gt[0], out_gt[3] = gdal.ApplyGeoTransform(in_gt, off_ULx, off_ULy)
            out_ds.SetGeoTransform(out_gt)
            out_ds.SetProjection(in_ds.GetProjection())

            out_ds.GetRasterBand(1).WriteArray(data)
            if nodata is 'fromimage':
                out_ds.GetRasterBand(1).SetNoDataValue(in_band.GetNoDataValue())
            else:
                out_ds.GetRasterBand(1).SetNoDataValue(nodata[z])
            del out_ds

        a = [i, off_ULx, off_ULy, off_LRx, off_LRy, np.where(data != nodata[z], data, np.nan)]
        for t, j in enumerate(k):
            res[j].append(a[t])

    cols = [res['LRx_off'][i] - res['ULx_off'][i] for i, j in enumerate(raster)]
    if len(set(cols)) > 1:
        print('')
        print("WARNING: subsets vary in x extent!!!!!!!!!!!!!!")
        print('')
    rows = [res['LRy_off'][i] - res['ULy_off'][i] for i, j in enumerate(raster)]
    if len(set(rows)) > 1:
        print('')
        print("WARNING: subsets vary in y extent!!!!!!!!!!!!!!")
        print('')

    return res
