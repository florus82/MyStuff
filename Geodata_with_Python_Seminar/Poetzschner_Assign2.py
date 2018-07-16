import os
import gdal
import glob
import sys

path = '/home/florian/Geodata_with_Python/session3/Week04 - Assignment/'

# sanity check - only for tiffs - maybe replace with list of acceptable data types
if len(glob.glob(path + '*' + 'tif')) == len(os.listdir(path)):
    print('All files in folder are tiff format - proceed')
else:
    sys.exit('Warning - non-matching files found; please check')


# function that extracts extent and corner coordinates of a raster file - checked only with UTM projection
def getcorners(single_ras):
    ds = gdal.Open(single_ras)
    gt = ds.GetGeoTransform()
    ext = {'Xmin': gt[0],
           'Xmax': gt[0] + (gt[1] * ds.RasterXSize),
           'Ymin': gt[3] + (gt[5] * ds.RasterYSize),
           'Ymax': gt[3]}
    coo = {'UpperLeftXY': [ext['Xmin'], ext['Ymax']],
           'UpperRightXY': [ext['Xmax'], ext['Ymax']],
           'LowerRightXY': [ext['Xmax'], ext['Ymin']],
           'LowerLeftXY': [ext['Xmin'], ext['Ymin']]}
    return ext, coo


# exercise 1
# get corners and print in a readable way
ex_a = [[i, getcorners(path + i)[1]] for i in os.listdir(path)]
for i in ex_a:
    print(i[0])
    print(i[1])
    print('')

#  exercise 2
# create empty dictionary with list slots for corner coordinates
k = ['Xmin', 'Xmax', 'Ymin', 'Ymax']
v = [[], [], [], []]
res = dict(zip(k, v))

# fill it with values of all raster files
for i in os.listdir(path):
    for j in k:
        res[j].append(getcorners(path + i)[0][j])

# determine min or max values per values' list in a fashion to
# get a bounding box indicating the overlap for all raster images
ff = [max, min, max, min]
for i, j in enumerate(ff):
    print("{} of bounding box is {}".format(k[i],j(res[k[i]])))  # strange warning - it works; maybe too dirty to pass list with functions??
