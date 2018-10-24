from FloppyToolZ.MasterFuncs import *

tile  = 'Mod1'
path  = 'Y:/_students_data_exchange/FP_FP/Seafile/myLibrary/MSc/'
cubis = getFilelist(path + 'Modelling/prediction/megadump/' + tile + '/SP', '.sav')
tili  = gdal.Open('Y:/_students_data_exchange/FP_FP/RS_Data/MODIS/rasterized/Mod1.tiff')
til   = tili.GetRasterBand(1).ReadAsArray()

# load models for lowest,median and highest RMSE) - should all be part of apply_along_axis
iter100 = pd.read_csv(path + 'Modelling/All_VIs/runs100/AllRuns.csv')
savs    = getFilelist(path + 'Modelling/All_VIs/runs100/sav', '.sav')
sav     = getMinMaxMedianSAV(iter100, savs)


test = cubis[0]
tes = joblib.load(test)

pred_arr = np.empty((tes.shape[0] * tes.shape[1],tes.shape[2]))
for dim3 in range(tes.shape[2]):
   pred_arr[:,dim3] = tes[:,:,dim3].ravel()

aa = np.ma.masked_where(np.isnan(pred_arr) == True, pred_arr)
predi = sav[1][1][0][0].predict()



a=np.array([7,1,10,0,5,4,5,0,9,9,3,3])
b=np.array([10,9,3,0,4,7,7,0,8,1,10,9])
a=a.reshape(12,1)
b=b.reshape(12,1)
maa = np.ma.masked_array(a, mask=[0, 0, 0, 1,0, 0,0,1,0,0,0,0])
mbb = np.ma.masked_array(b, mask=[0, 0, 0, 1,0, 0,0,1,0,0,0,0])
maa= np.ma.compressed(maa).reshape(10,1)
mbb= np.ma.compressed(mbb).reshape(10,1)





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


