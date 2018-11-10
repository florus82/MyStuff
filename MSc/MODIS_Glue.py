from FloppyToolZ.MasterFuncs import *
import sys

path1 = 'Z:/_students_data_exchange/FP_FP/Seafile/myLibrary/MSc/Modelling/Single_VIs/prediction/Mod1'
path2 = 'Z:/_students_data_exchange/FP_FP/Seafile/myLibrary/MSc/Modelling/Single_VIs/prediction/Mod2'
path3 = 'Z:/_students_data_exchange/FP_FP/Seafile/myLibrary/MSc/Modelling/Single_VIs/prediction/Mod3'
path4 = 'Z:/_students_data_exchange/FP_FP/Seafile/myLibrary/MSc/Modelling/Single_VIs/prediction/Mod4'

storpath = 'Z:/_students_data_exchange/FP_FP/Seafile/myLibrary/MSc/Modelling/Single_VIs/prediction/Mosaic/'

tiles1 = getFilelist(path1,'.tiff')
tiles2 = getFilelist(path2,'.tiff')
tiles3 = getFilelist(path3,'.tiff')
tiles4 = getFilelist(path4,'.tiff')

# check if all lists have the same order
length = [len(tiles1), len(tiles2), len(tiles3), len(tiles4)]
if len(set(length)) == 1:
    print('All lists have equal length')
else:
    sys.exit('Lists are not the same length!')

for i in range(len(tiles1)):
    if ('_'.join(tiles1[i].split('/')[-1].split('.')[0].split('_')[1:3]) == '_'.join(tiles2[i].split('/')[-1].split('.')[0].split('_')[1:3]) and
        '_'.join(tiles1[i].split('/')[-1].split('.')[0].split('_')[1:3]) == '_'.join(tiles3[i].split('/')[-1].split('.')[0].split('_')[1:3]) and
        '_'.join(tiles1[i].split('/')[-1].split('.')[0].split('_')[1:3]) == '_'.join(tiles4[i].split('/')[-1].split('.')[0].split('_')[1:3])):
        print('_'.join(tiles1[i].split('/')[-1].split('.')[0].split('_')[1:3]) + 'Lists are in order')
    else:
        sys.exit('Lists not in order!')

tilesL = [[tiles1[i], tiles2[i], tiles3[i], tiles4[i]] for i in range(len(tiles1))]

for i in range(len(tilesL)):
    # get resolution --> should build in a check for resolution consistency
    tiles = tilesL[i]
    sc = gdal.Open(tiles[3])
    sc_b = sc.GetRasterBand(1)
    gt = sc.GetGeoTransform()

    Xmin = [getExtentRas(t)['Xmin'] for t in tiles]
    Xmax = [getExtentRas(t)['Xmax'] for t in tiles]
    Ymin = [getExtentRas(t)['Ymin'] for t in tiles]
    Ymax = [getExtentRas(t)['Ymax'] for t in tiles]

    xoff = abs(int((max(Xmax) - min(Xmin)) / gt[5]))

    yoff = abs(int((max(Ymax) - min(Ymin)) / gt[5]))


    # make mosaic
    gtiff_driver = gdal.GetDriverByName('GTiff')
    out_ds = gtiff_driver.Create(storpath + '_'.join(tiles1[i].split('/')[-1].split('.')[0].split('_')[1:3]) + '_Mosaic.tif', xoff, yoff, 1, sc.GetRasterBand(1).DataType)
    out_gt = list(gt)
    out_gt[0], out_gt[3] = min(Xmin), max(Ymax)
    out_ds.SetGeoTransform(out_gt)
    out_ds.SetProjection(sc.GetProjection())

    # fill the array
    data = np.zeros((yoff, xoff), dtype='float64')

    for til in tiles:
        print(til)
        ti = gdal.Open(til)
        in_gt = ti.GetGeoTransform()
        col_off = abs(int((out_gt[0] - in_gt[0]) / out_gt[5]))
        row_off = abs(int((out_gt[3] - in_gt[3]) / out_gt[5]))
        data[row_off : (row_off + ti.RasterYSize) , col_off : (col_off + ti.RasterXSize)] = ti.GetRasterBand(1).ReadAsArray()
        print(row_off)
        print(row_off + ti.RasterYSize)
        print(col_off)
        print(col_off + ti.RasterXSize)
    data[data==0] = -9999
    out_ds.GetRasterBand(1).WriteArray(data)
    out_ds.GetRasterBand(1).SetNoDataValue(-9999)

    del out_ds
