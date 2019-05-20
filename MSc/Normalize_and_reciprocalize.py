from FloppyToolZ.MasterFuncs import *

stor_path = r'Y:\_students_data_exchange\FP_FP\Seafile\myLibrary\MSc\Modelling\GAP_FILLED\Single_VIs\prediction\CS\checkunscaled\post'
files     = getFilelist(r'Y:\_students_data_exchange\FP_FP\Seafile\myLibrary\MSc\Modelling\GAP_FILLED\Single_VIs\prediction\CS\checkunscaled\post\mean', '.tif')
files     = files[1:9:2]

def minmax_recipr(x):
    xx = (x - mini) / (maxi - mini)
    #xxx = abs(xx-1)
    return xx

glob_min = []
glob_max = []
for fi in files:
    a = gdal.Open(fi)
    b = a.GetRasterBand(1).ReadAsArray()
    b[b == -9999] = np.nan
    b[b<0] = np.nan
    glob_min.append(np.nanmin(b))
    glob_max.append(np.nanmax(b))


for fil in files:
    print(fil)
    img = gdal.Open(fil)
    arr = img.GetRasterBand(1).ReadAsArray()
    arr[arr== -9999] = np.nan
    arr[arr<0] = np.nan
    arr2 = np.reshape(arr,(arr.shape[0], arr.shape[1],1))
    mini = np.min(glob_min)#np.nanmin(arr)
    maxi = np.max(glob_max)#np.nanmax(arr)

    normi =np.apply_along_axis(minmax_recipr, 2, arr2)
    #normi[normi == 0] = 0.00001 # Circuitscape does not like zeros

    gtiff_driver = gdal.GetDriverByName('GTiff')
    out_ds = gtiff_driver.Create(stor_path + '/' +
        fil.split('/')[-1].split('.')[0] + '_glob.tif', img.RasterXSize, img.RasterYSize, 1,
        img.GetRasterBand(1).DataType)
    out_ds.SetGeoTransform(img.GetGeoTransform())
    out_ds.SetProjection(img.GetProjection())
    normi[np.isnan(normi)==True] = -9999
    normi = np.reshape(normi, (arr.shape[0], arr.shape[1]))
    out_ds.GetRasterBand(1).WriteArray(normi)
    out_ds.GetRasterBand(1).SetNoDataValue(-9999)

    del out_ds