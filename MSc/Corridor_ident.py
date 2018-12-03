from FloppyToolZ.MasterFuncs import *

# paths to cs product and sc/tc
path = ('/home/florus/Seafile/myLibrary/MSc/Modelling/Single_VIs/prediction/CS/post_process/BM_Median_Mosaicresample_fac2_norm_60_nodes_25_cum_curmap_nobuff_noNA.tif', '/home/florus/Seafile/myLibrary/MSc/other_maps_biomass_matthias/resample/L_CLEAN_S_CLEAN__SC_repro_resamp_average_to_MODIS.tif', '/home/florus/Seafile/myLibrary/MSc/other_maps_biomass_matthias/resample/L_CLEAN_S_CLEAN__TC_repro_resamp_average_to_MODIS.tif')

# load them; beware of NA values, masking not possible due to numpy bug float nan to int
conti = []
for p in path:
    print(p)
    a = gdal.Open(p)
    gt = a.GetGeoTransform()
    pj = a.GetProjection()
    conti.append(a.GetRasterBand(1).ReadAsArray())

# set NAs
conti[0][conti[0]<0] = np.nan
conti[1] = np.where(conti[1] == 0, np.nan, conti[1])
conti[2] = np.where(conti[2] == 0, np.nan, conti[2])

# mask cs product by threshold, based on distribution of values, and disaggregate cs product back to resampled tc/sc maps (resampled to MODIS)
quanti = 0.95
threshold = np.nanquantile(conti[0], quanti)
out = np.where(conti[0] >= threshold, 1 , 0)
out_newshape = np.zeros((conti[1].shape[0], conti[1].shape[1]))
counti_y = 0
for i in range(out.shape[0]):
    counti_x = 0
    for j in range(out.shape[1]):
        out_newshape[counti_y, counti_x]       = out[i, j]
        out_newshape[counti_y, counti_x+ 1]    = out[i, j]
        out_newshape[counti_y +1, counti_x]    = out[i, j]
        out_newshape[counti_y +1, counti_x +1] = out[i, j]
        counti_x += 2
    counti_y += 2

# define class for tc/sc
quanti2 = 0.5
sc_thresh = np.nanquantile(conti[1], quanti2)
tc_thresh = np.nanquantile(conti[2], quanti2)

# 11 = low sc/tc, 12 = high sc/low tc, 21 = low sc/high tc, 22 = high sc/tc
sc_cat = np.where(conti[1] < sc_thresh, 1, 2)
tc_cat = np.where(conti[2] < tc_thresh, 10, 20)

out_arr = np.where(out_newshape == 1, sc_cat + tc_cat,-9999)


# export as tif
gtiff_driver = gdal.GetDriverByName('GTiff')
out_ds = gtiff_driver.Create('/home/florus/Seafile/myLibrary/MSc/Modelling/Single_VIs/prediction/CS/Identify/Corridors_' + str(quanti) + 'sctc_' + str(quanti2) + '.tif', out_arr.shape[1], out_arr.shape[0], 1, gdal.GDT_Float32)
out_ds.SetGeoTransform(gt)
out_ds.SetProjection(pj)
out_ds.GetRasterBand(1).WriteArray(out_arr)
out_ds.GetRasterBand(1).SetNoDataValue(-9999)

del out_ds