from FloppyToolZ.Funci import *
from joblib import Parallel, delayed
import numpy as np

files   = getFilelist('/home/florian/Geodata_with_Python/session7/Assignment06_data','tif')
files2  = [[i] for i in files]   # movinWinni wants lists....
names   = [[150], [300], [450]]
outpath = '/home/florian/Geodata_with_Python/session11/output/'


jobs = [[i, j, Shanni, 'none', outpath] for i in files2 for j in names]  # 'none' does not work!!!!


Parallel(n_jobs=3)(delayed(movinWinni)(i[0], i[1], i[2], storpath = i[4]) for i in jobs)

# ## Appendix
# ## FloppyToolZ functions for this assignment


def getFilelist(originpath, ftyp):
    files = os.listdir(originpath)
    out   = []
    for i in files:
        if i.split('.')[-1] in ftyp:
            if originpath.endswith('/'):
                out.append(originpath + i)
            else:
                out.append(originpath + '/' + i)
        else:
            print("non-matching file - {} - found".format(i.split('.')[-1]))
    return out



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


def Shanni(a):
    b = len(a)
    unique, counts = np.unique(a, return_counts=True) # np.count_nonzero
    res = np.sum((counts / b) * np.log(counts / b)) * -1
    return res
