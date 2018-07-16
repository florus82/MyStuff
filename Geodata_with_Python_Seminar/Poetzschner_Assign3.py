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


# ##task 1

# get a list with the three tiffs and their extens
rasL = getFilelist('/home/florian/Geodata_with_Python/session4/Assignment03 - data', 'tif')
extL = getExtent(rasL)

# forward extent-list in order to find upper left and lower right coordinates of common extent
BBdi = commonBoundsDim(extL)
BBco = commonBoundsCoord(BBdi)

# define NoData values - could have been obtained by matching raster values with list of sensible ranges for themes
nope = [65536, 65535, -3.402823060737096525084e+38]
# get raster offsets and subsetted data
subs = rastersubbyCord(rasL, BBco[0]['UpperLeftXY'][0], BBco[0]['UpperLeftXY'][1],
                       BBco[0]['LowerRightXY'][0], BBco[0]['LowerRightXY'][1],
                       # '/home/florian/Geodata_with_Python/session4/Assignment03 - data/subs',
                       nodata = nope)

# print statistics
for i, j in enumerate(rasL):
    print(j)
    print('Mean = {}'.format(round(np.nanmean(subs['Data'][i]), 2)))
    print('Maxi = {}'.format(round(np.nanmax(subs['Data'][i]), 2)))
    print('Mini = {}'.format(round(np.nanmin(subs['Data'][i]), 2)))

# ## task 2

# mask DEM and Slope values
DEM = np.ma.array(subs['Data'][0], mask=np.isnan(subs['Data'][0]))
SLO = np.ma.array(subs['Data'][2], mask=np.isnan(subs['Data'][2]))

# create new array meeting the conditions; warning seems to have no effect, probably connected to nan
aa = np.ma.where((DEM < 1000) & (SLO < 30), 1, 0)

# count zeros and ones (and nans)
unique, counts = np.unique(aa, return_counts = True)
bb = dict(zip(unique[:-1], counts[:-1]))
print(round(bb[1] / (bb[1] + bb[0]), 4))

#write Raster - take subsetted THP as template as this is the only one that really fulfills the common extent condition;
# the others don't, because the three raster don't line up
in_ds = gdal.Open(subs['Raster'][1])
gtiff_driver = gdal.GetDriverByName('GTiff')
out_ds = gtiff_driver.Create('/home/florian/Geodata_with_Python/session4/mask.tif',
                                         subs['LRx_off'][1] - subs['ULx_off'][1],
                                         subs['LRy_off'][1] - subs['ULy_off'][1],
                                         1, in_ds.GetRasterBand(1).DataType)

in_gt = in_ds.GetGeoTransform()
out_gt = list(in_gt)
out_gt[0], out_gt[3] = gdal.ApplyGeoTransform(in_gt, subs['ULx_off'][1], subs['ULy_off'][1])
out_ds.SetGeoTransform(out_gt)
out_ds.SetProjection(in_ds.GetProjection())

out_ds.GetRasterBand(1).WriteArray(aa)
out_ds.GetRasterBand(1).SetNoDataValue(np.nan)
del out_ds


# ## task 3

# mask subsetted THP layer
THP = np.ma.array(subs['Data'][1], mask=np.isnan(subs['Data'][1]))

# create a dictionary containing three lists corresponding to individual years and respective extracted means
k = ['Year','Mean_elev','Mean_slope']
a = [[int(i), round(DEM[THP==i].mean(), 2), round(SLO[THP==i].mean(), 2)] for i in np.unique(THP)[:-1]]
res = dict(zip(k, zip(*a)))

# export dictionary as data.frame :-)
df = pandas.DataFrame(data=res)
df.to_csv('/home/florian/Geodata_with_Python/session4/Poetzschner_Task3.csv', sep=',',index=False)