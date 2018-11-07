from FloppyToolZ.MasterFuncs import *

tile  = 'Mod3'
#path  = '/home/florus/Seafile/myLibrary/MSc/'
path = 'Z:/_students_data_exchange/FP_FP/Seafile/myLibrary/MSc/'
#path2 = '/home/florus/MSc/RS_Data/MODIS/rasterized/
path2 = 'Z:/_students_data_exchange/FP_FP/RS_Data/MODIS/rasterized/'
cubis = getFilelist(path + 'Modelling/Single_VIs/prediction/' + tile + '/SP', '.sav')
tili  = gdal.Open(path2 + tile + '.tiff')
til   = tili.GetRasterBand(1).ReadAsArray()
# subset to Chaco area
til[til == 0] = np.nan
reader = shrinkNAframe(til)
til   = tili.GetRasterBand(1).ReadAsArray(reader[0], reader[1], reader[2], reader[3])

# make seasonal parameter raster arrays
rasoutL = [np.empty((til.shape[0], til.shape[1])) for i in range(joblib.load(cubis[0]).shape[2])]
rasoutL.append(til)
rasNames = ['SoS', 'EoS', 'SeasMax', 'SeasMin', 'SeasInt', 'SeasLen', 'SeasAmp','BM']
# load models for lowest,median and highest RMSE) - should all be part of apply_along_axis
iter100 = pd.read_csv(path + 'Modelling/Single_VIs/Modelling/runs100/All100Runs.csv')
savs    = getFilelist(path + 'Modelling/Single_VIs/Modelling/runs100/sav', '.sav')
sav     = getMinMaxMedianSAV(iter100, savs)
sav_names = ['Min', 'Max', 'Median']

for mod in range(len(sav_names)):
    # ###### iterate over cubes (tiled MODIS-tile)
    for printer, cubi in enumerate(cubis):
        cub = joblib.load(cubi)
        print('Start predicting cube ' + str(printer))
        # fill in SP-rasterarrays with seasonal parameter data from cubes
        for indi in range(len(rasoutL)-1):
            rasoutL[indi][int(cubi.split('_X_')[-1].split('_')[4]):int(cubi.split('_X_')[-1].split('_')[5].split('.')[0]),
                int(cubi.split('_X_')[-1].split('_')[0]):int(cubi.split('_X_')[-1].split('_')[1])] = cub[:,:,indi]

        # ########## consistency check --> if there are NAs, make sure they are in all bands
        for row in range(cub.shape[0]):
            for col in range(cub.shape[1]):
                if np.count_nonzero(np.isnan(cub[row, col, :])) not in [0, cub.shape[2]]:
                    cub[row, col, :] = np.nan

        # ########### create and populate array with shape [x*y,predictor]
        pred_arr = np.empty((cub.shape[0] * cub.shape[1],cub.shape[2]))
        for dim3 in range(cub.shape[2]):
           pred_arr[:,dim3] = cub[:,:,dim3].ravel()

        # ########### erase NAs
        pred_arr2 = pred_arr[np.logical_not(np.isnan(pred_arr))]
        # ######## check if there are actually values to predict, if not, fill in the values with NAs (taken from the read in cube
        if len(pred_arr2) != 0:
            pred_arr2 = pred_arr2.reshape(int(pred_arr2.shape[0]/pred_arr.shape[1]), pred_arr.shape[1])

            # ########### make prediciton and bring back 2D
            predi = sav[mod][1].predict(pred_arr2)
            dummy = pred_arr[:,0].copy()

            counter = 0
            for ind, entry in enumerate(pred_arr[:,0]):
                if np.isnan(entry) == False:
                    dummy[ind] = predi[counter]
                    counter += 1

            pred2D = dummy.reshape(cub.shape[0],cub.shape[1])

            # ########### fill in prediction into MODIS-Tile
            aa=rasoutL[len(rasoutL)-1][int(cubi.split('_X_')[-1].split('_')[4]):int(cubi.split('_X_')[-1].split('_')[5].split('.')[0]),
                    int(cubi.split('_X_')[-1].split('_')[0]):int(cubi.split('_X_')[-1].split('_')[1])] = pred2D
        else:
            rasoutL[len(rasoutL)-1][int(cubi.split('_X_')[-1].split('_')[4]):int(cubi.split('_X_')[-1].split('_')[5].split('.')[0]),
            int(cubi.split('_X_')[-1].split('_')[0]):int(cubi.split('_X_')[-1].split('_')[1])] = cub[:,:,0]


    print('Prediciton finished - Start to prepare raster')
    gtiff_driver = gdal.GetDriverByName('GTiff')
    for counti in range(len(rasoutL)):
        out_ds = gtiff_driver.Create(path + 'Modelling/Single_VIs/prediction/' + tile + '/' + tile + '_' + rasNames[counti] + '_' + sav_names[mod] + '.tif', til.shape[1],
                                     til.shape[0], 1, gdal.GDT_Float64)
        out_gt = list(tili.GetGeoTransform())
        out_gt[0], out_gt[3] = gdal.ApplyGeoTransform(tili.GetGeoTransform(), reader[0], reader[1])
        out_ds.SetGeoTransform(out_gt)
        out_ds.SetProjection(tili.GetProjection())
        # Set NA to -9999
        outNA_arr = np.where(np.isnan(rasoutL[counti]) == True, -9999, rasoutL[counti])
        out_ds.GetRasterBand(1).WriteArray(outNA_arr)
        out_ds.GetRasterBand(1).SetNoDataValue(-9999)

        del out_ds
        print('Raster ' + rasNames[counti] + ' created :-)')