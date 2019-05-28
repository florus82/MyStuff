from FloppyToolZ.MasterFuncs import *

# load files to mask and stack them
toMaskL = getFilelist('Y:/_students_data_exchange/FP_FP/Seafile/myLibrary/MSc/Modelling/GAP_FILLED/Single_VIs/prediction/Mosaic/check', '.tif')
# 0-3 = BM, Eos, Seasamp, seasint, seaslen, seasmax, seasmin, sos
toMaskC = []
for toma in toMaskL:
    a = gdal.Open(toma)
    toMaskC.append(a.GetRasterBand(1).ReadAsArray())
toMaskSt = np.dstack(toMaskC)

# load LC file
mask = gdal.Open('Y:/_students_data_exchange/FP_FP/Seafile/myLibrary/MSc/other_maps_biomass_matthias/resample/baumann-etal_2017_LandCover-Map-CHACO_GlobalChangeBiology_repro_resamp_average_to_MODIS.tif')
mask = mask.GetRasterBand(1).ReadAsArray()

# make a mask
maski = np.ones((mask.shape[0],mask.shape[1]))
# find 'bad' LC classes and set mask -9999
rows, cols = np.where(np.isin(mask, [6,7,9]))
maski[rows, cols] = -9999

# mask BM <0
rows, cols = np.where(toMaskSt[:,:,0] < 0) # EoS
maski[rows, cols] = -9999
rows, cols = np.where(toMaskSt[:,:,1] < 0) # Seasamp
maski[rows, cols] = -9999
rows, cols = np.where(toMaskSt[:,:,2] < 0) # seasint
maski[rows, cols] = -9999
rows, cols = np.where(toMaskSt[:,:,3] < 0) # seaslen
maski[rows, cols] = -9999


# set bad predictor ranges -9999
rows, cols = np.where(toMaskSt[:,:,4] <= 200) # EoS
maski[rows, cols] = -9999
rows, cols = np.where(toMaskSt[:,:,5] >= 0.8) # Seasamp
maski[rows, cols] = -9999
rows, cols = np.where(toMaskSt[:,:,6] <= 10) # seasint
maski[rows, cols] = -9999
rows, cols = np.where(toMaskSt[:,:,7] <= 50) # seaslen
maski[rows, cols] = -9999
rows, cols = np.where(np.logical_and(toMaskSt[:,:,8] < 0.2, toMaskSt[:,:,8] > 0.95)) # seasmax
maski[rows, cols] = -9999
rows, cols = np.where(toMaskSt[:,:,9] <= 0.1) # seasmin
maski[rows, cols] = -9999
rows, cols = np.where(toMaskSt[:,:,10] >= 220) # sos
maski[rows, cols] = -9999

# apply mask on stack
killer_row, killer_col = np.where(maski == -9999)
toMaskSt[killer_row, killer_col, :] = -9999

gtiff_driver = gdal.GetDriverByName('GTiff')
for masked in range(toMaskSt.shape[2]):
    print(masked)
    out_ds = gtiff_driver.Create(toMaskL[masked].split('.')[0] + '_masked_pred.tif',
                                 toMaskSt.shape[1], toMaskSt.shape[0], 1, a.GetRasterBand(1).DataType)
    out_ds.SetGeoTransform(a.GetGeoTransform())
    out_ds.SetProjection(a.GetProjection())
    out_ds.GetRasterBand(1).WriteArray(toMaskSt[:,:,masked])
    out_ds.GetRasterBand(1).SetNoDataValue(-9999)

    del out_ds