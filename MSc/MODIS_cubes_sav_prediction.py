from FloppyToolZ.MasterFuncs import *

tile  = 'Mod1'
path  = '/home/florus/Seafile/myLibrary/MSc/'
cubis = getFilelist(path + 'Modelling/Single_VIs/prediction/' + tile + '/SP', '.sav')
tili  = gdal.Open('/home/florus/MSc/RS_Data/MODIS/rasterized/Mod1.tiff')
til   = tili.GetRasterBand(1).ReadAsArray()

# load models for lowest,median and highest RMSE) - should all be part of apply_along_axis
iter100 = pd.read_csv(path + 'Modelling/Single_VIs/Modelling/runs100/AllRuns.csv')
savs    = getFilelist(path + 'Modelling/Single_VIs/Modelling/runs100/sav', '.sav')
sav     = getMinMaxMedianSAV(iter100, savs)

test = cubis[122]
tes = joblib.load(test)

pred_arr = np.empty((tes.shape[0] * tes.shape[1],tes.shape[2]))
for dim3 in range(tes.shape[2]):
   pred_arr[:,dim3] = tes[:,:,dim3].ravel()

res_arr = np.where(np.isnan(pred_arr) == True, np.nan, 1)
pred_arr = pred_arr[np.logical_not(np.isnan(pred_arr))]
pred_arr = pred_arr.reshape(int(pred_arr.shape[0]/res_arr.shape[1]), res_arr.shape[1])


predi = sav[1][2].predict(pred_arr)


r, c = np.where(np.isnan(pred_arr) == True)
r[0:20]
c[0:20]
print(str(r[30*7]) + '_' + str(c[0]))


stack_array = np.ones((rows * cols, bandsALL), dtype=np.int16)
i = 0
for ds in ds_paths:
    path = ds[0]
    bands = ds[1]
    ds_open = gdal.Open(path, GA_ReadOnly)
    for band in bands:
        ar = ds_open.GetRasterBand(band).ReadAsArray(0, 0, cols, rows).ravel()
        # Check if it is a sentinel-1 band --> then multiply values by 10000
        if path.find("Sentinel1") >= 0:
            ar = ar * 10000
        else:
            ar = ar
        stack_array[:, i] = ar
        i = i + 1
    ds_open = None
prediction = model.predict(stack_array)
stack_array = None
prediction = prediction.reshape((rows, cols))


