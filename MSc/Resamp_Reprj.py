from FloppyToolZ.MasterFuncs import *

masterP = 'Y:/_students_data_exchange/FP_FP/Seafile/myLibrary/MSc/other_maps_biomass_matthias/'
rasL = [masterP + 'Gasparri/biomasa_rf1.tif',
        masterP + 'global_ForestWatch/20S_060W_biomass.tif',
        masterP + 'global_ForestWatch/20S_070W_biomass.tif',
        masterP + 'LC/baumann-etal_2017_LandCover-Map-CHACO_GlobalChangeBiology_reclassified.tif',
        masterP + 'Saatchi_2011/Avitabile_AGB_Map/Avitabile_AGB_Map.tif',
        masterP + 'TC_SC/L_CLEAN_S_CLEAN__SC.vrt',
        masterP + 'TC_SC/L_CLEAN_S_CLEAN__TC.vrt']

# define storagpath
storPath = masterP + 'resample/'
# load raster which dimension's and projection serve as template
dum = gdal.Open('Y:/_students_data_exchange/FP_FP/Seafile/myLibrary/MSc/Modelling/Single_VIs/prediction/Mosaic/BM_Median_Mosaic.tif')

# load image to reproject/resample
img    = gdal.Open('Y:/_students_data_exchange/FP_FP/Seafile/myLibrary/MSc/other_maps_biomass_matthias/TC_SC/L_CLEAN_S_CLEAN__SC.vrt')
imgNA  = img.GetRasterBand(1).GetNoDataValue()
print(imgNA)

gtiff_driver = gdal.GetDriverByName('GTiff')
out_ds = gtiff_driver.Create(storPath + '_repro_resamp_average_to_MODIS.tif', dum.RasterXSize, dum.RasterYSize, 1, img.GetRasterBand(1).DataType)
out_ds.SetGeoTransform(dum.GetGeoTransform())
out_ds.SetProjection(dum.GetProjection())
out_ds.GetRasterBand(1).SetNoDataValue(imgNA)
gdal.ReprojectImage(img, out_ds, img.GetProjection(), out_ds.GetProjection(), gdal.GRA_Average)
del out_ds