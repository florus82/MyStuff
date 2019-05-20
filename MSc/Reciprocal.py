from FloppyToolZ.MasterFuncs import *

stor_path = r'Y:\_students_data_exchange\FP_FP\Seafile\myLibrary\MSc\Modelling\GAP_FILLED\Single_VIs\prediction\CS\check\Normalized_Input_not_scaled'
files     = getFilelist(r'Y:\_students_data_exchange\FP_FP\Seafile\myLibrary\MSc\Modelling\GAP_FILLED\Single_VIs\prediction\resample\check', '.tif')

def invert(x, maxVal):
    xx = (maxVal + 0.00001) - x
    return xx

for fil in files:
    img = gdal.Open(fil)
    arr = img.GetRasterBand(1).ReadAsArray()
    arr[arr== -9999] = np.nan
    arr[arr<0] = np.nan
    arr2 = np.reshape(arr,(arr.shape[0], arr.shape[1],1))
    mini = np.nanmin(arr)
    maxi = np.nanmax(arr)

    normi =np.apply_along_axis(invert, 2, arr2, maxi)
    #normi[normi == 0] = 0.00001 # Circuitscape does not like zeros

    gtiff_driver = gdal.GetDriverByName('GTiff')
    out_ds = gtiff_driver.Create(stor_path + '/' +
        fil.split('/')[-1].split('.')[0] + '_reci_not_scaled.tif', img.RasterXSize, img.RasterYSize, 1,
        img.GetRasterBand(1).DataType)
    out_ds.SetGeoTransform(img.GetGeoTransform())
    out_ds.SetProjection(img.GetProjection())
    normi[np.isnan(normi)==True] = -9999
    normi = np.reshape(normi, (arr.shape[0], arr.shape[1]))
    out_ds.GetRasterBand(1).WriteArray(normi)
    out_ds.GetRasterBand(1).SetNoDataValue(-9999)

    del out_ds