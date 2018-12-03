from FloppyToolZ.MasterFuncs import *

toMaskL = getFilelist('/home/florus/Seafile/myLibrary/MSc/Modelling/GAP_FILLED/Single_VIs/prediction/Mosaic', '.tif')
toMaskC = []

for toma in toMaskL:
    a = gdal.Open(toma)
    toMaskC.append(a.GetRasterBand(1).ReadAsArray())

mask = gdal.Open('/home/florus/Seafile/myLibrary/MSc/other_maps_biomass_matthias/resample/baumann-etal_2017_LandCover-Map-CHACO_GlobalChangeBiology_repro_resamp_average_to_MODIS.tif')
mask = mask.GetRasterBand(1).ReadAsArray()

toMaskSt = np.dstack(toMaskC)

for i in range(mask.shape[0]):
    for j in range(mask.shape[1]):
        if mask[i, j] in [6, 7, 9]:
            toMaskSt[i, j, :] = -9999

gtiff_driver = gdal.GetDriverByName('GTiff')
for masked in range(toMaskSt.shape[2]):
    print(masked
    out_ds = gtiff_driver.Create(toMaskL[masked].split('.')[0] + 'masked.tif',
                                 toMaskSt.shape[1], toMaskSt.shape[0], 1, a.GetRasterBand(1).DataType)
    out_ds.SetGeoTransform(a.GetGeoTransform())
    out_ds.SetProjection(a.GetProjection())
    out_ds.GetRasterBand(1).WriteArray(toMaskSt[:,:,masked])
    out_ds.GetRasterBand(1).SetNoDataValue(-9999)

    del out_ds