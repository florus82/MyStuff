from FloppyToolZ.MasterFuncs import *

resa_path = 'Z:/_students_data_exchange/FP_FP/Seafile/myLibrary/MSc/Modelling/Single_VIs/prediction/resample'
resa = 'BM_Median_Mosaicresample_fac3.tif'
img = gdal.Open(resa_path + '/' + resa)
arr = img.GetRasterBand(1).ReadAsArray()
arr[arr== -9999] = np.nan
arr[arr<0] = np.nan
arr2 = np.reshape(arr,(arr.shape[0], arr.shape[1],1))
mini = np.nanmin(arr)
maxi = np.nanmax(arr)

def minmax_recipr(x):
    xx = (x - mini) / (maxi - mini)
    xxx = abs(xx-1)
    return xxx
normi =np.apply_along_axis(minmax_recipr, 2, arr2)
normi[normi == 0] = 0.00001

gtiff_driver = gdal.GetDriverByName('GTiff')
out_ds = gtiff_driver.Create(('/').join(resa_path.split('/')[0:len(resa_path.split('/'))-1]) + '/CS/Normalized_Input/' +
    resa.split('.')[0] + '_norm.tif', img.RasterXSize, img.RasterYSize, 1,
    img.GetRasterBand(1).DataType)
out_ds.SetGeoTransform(img.GetGeoTransform())
out_ds.SetProjection(img.GetProjection())
normi[np.isnan(normi)==True] = -9999
normi = np.reshape(normi, (arr.shape[0], arr.shape[1]))
out_ds.GetRasterBand(1).WriteArray(normi)
out_ds.GetRasterBand(1).SetNoDataValue(-9999)

del out_ds