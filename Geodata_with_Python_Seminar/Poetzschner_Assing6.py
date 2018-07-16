import numpy as np
import gdal
import os
import math
import zipfile

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


# ## Calc Shannon-Diversity-Index


def Shanni(a):
    b = len(a)
    unique, counts = np.unique(a, return_counts=True) # np.count_nonzero
    res = np.sum((counts / b) * np.log(counts / b)) * -1
    return res



# ## moving window
# rasterList = list of one or multiple paths towards rasterfiles
# win_names  = names which are used if storpath is not 'none'; if win_dim is 'none', win_names MUST be the radius of an equi-distant window size
# funci      = function to be applied on window
# win_dim    = rows and cols of windows can here be given; overwrites the radius of an equi-distant window
# storpath   = path to folder where outputs are stored; if not given, only the objects are returned by movingWinni

def movinWinni(rasterlist, win_names, funci, win_dim = 'none', storpath = 'none'):
    # check storpath
    if storpath is not 'none':
        if storpath.endswith('/'):
            storpath = storpath
        else:
            storpath = storpath + '/'

    # create list to store output
    res = []

    # loop through files and
    for wc, w in enumerate(win_names):
        for img in rasterlist:
            # get raster info and data
            in_ras = gdal.Open(img)
            in_ras_band = in_ras.GetRasterBand(1)
            in_ras_data = in_ras_band.ReadAsArray()
            in_rows = in_ras_data.shape[0]  # rows of image
            in_cols = in_ras_data.shape[1]  # cols of image
            in_ras_gt = in_ras.GetGeoTransform()
            ras_res = in_ras_gt[1]

            # check for dimensions; if none given, the radius is converted to cells for window
            if win_dim is 'none':
                ww = int((w * 2 + ras_res) / ras_res)
                win = (ww, ww)
            else:
                win = (win_dim[0], win_dim[1])

            rows = in_rows - win[0] + 1
            cols = in_cols - win[1] + 1

            # slice the data times the product of window dimensions
            slici = []
            for i in range(win[0]):
                for j in range(win[1]):
                    slici.append(in_ras_data[i:rows+i,j:cols+j])
            # stack slices and fill empty array with funci returns
            stacki = np.dstack(slici)
            print(stacki.shape)
            out_data = np.zeros(in_ras_data.shape, np.float32)
            out_data[math.floor(win[0]/2):-(math.floor(win[0]/2)), math.floor(win[1]/2):-(math.floor(win[1]/2))] = np.apply_along_axis(Shanni, 2, stacki)
            res.append(out_data)

            #write in raster (optional)
            if storpath is 'none':
                print("did you assign this function's output to an object? - no copy on drive")
            else:
                print('copy on drive')
                gtiff_driver = gdal.GetDriverByName('GTiff')
                out_ds = gtiff_driver.Create(storpath + '_' + img.split('/')[-1].split('.')[0] + '_' +
                                             str(win_names[wc]) + '_' + funci.__name__ + '.tif', in_cols,
                                             in_rows, 1, eType=gdal.GDT_Float32)
                out_ds.SetGeoTransform(in_ras.GetGeoTransform())
                out_ds.SetProjection(in_ras.GetProjection())
                out_ds.GetRasterBand(1).WriteArray(out_data)
                del out_ds
    return(res)


# ####### run assignment
# create variables
files   = getFilelist('/home/florian/Geodata_with_Python/session7/Assignment06_data','tif')
names   = [150, 300, 450]
outpath = '/home/florian/Geodata_with_Python/session7/output/'
# run movinWinni
test    = movinWinni(files, names, Shanni, storpath= outpath)

# ###zip the results
# get files to zip and create empty zip container
to_zip = getFilelist(outpath, 'tif')
zf = zipfile.ZipFile(outpath + 'MW_SHDI.zip', mode='w')
# get original wd
orig_wd = os.getcwd()
# set wd to zipfiles
os.chdir(outpath)
# zip em
for i in to_zip:
    zf.write(i.split('/')[-1])
zf.close()
#set original wd
os.chdir(orig_wd)