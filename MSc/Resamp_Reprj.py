from FloppyToolZ.MasterFuncs import *

# masterP = 'Y:/_students_data_exchange/FP_FP/Seafile/myLibrary/MSc/other_maps_biomass_matthias/'
# rasL = [masterP + 'Gasparri/biomasa_rf1.tif',
#         masterP + 'global_ForestWatch/20S_060W_biomass.tif',
#         masterP + 'global_ForestWatch/20S_070W_biomass.tif',
#         masterP + 'LC/baumann-etal_2017_LandCover-Map-CHACO_GlobalChangeBiology_reclassified.tif',
#         masterP + 'Saatchi_2011/Avitabile_AGB_Map/Avitabile_AGB_Map.tif',
#         masterP + 'TC_SC/L_CLEAN_S_CLEAN__SC.vrt',
#         masterP + 'TC_SC/L_CLEAN_S_CLEAN__TC.vrt']

rasL = getFilelist(r'Y:\_students_data_exchange\FP_FP\Seafile\myLibrary\MSc\Modelling\GAP_FILLED\Single_VIs\prediction\Mosaic\check\masked', '.tif')
rasL = rasL[0:4]
# define storagpath
storPath = r'Y:\_students_data_exchange\FP_FP\Seafile\myLibrary\MSc\Modelling\GAP_FILLED\Single_VIs\prediction\resample\check'
# load raster which dimension's and projection serve as template
dum = gdal.Open(r'Y:\_students_data_exchange\FP_FP\Seafile\myLibrary\MSc\Modelling\Single_VIs\prediction\resample\BM_Median_Mosaicresample_fac2.tif')

# load images and reproject/resample
for image in rasL:
        img = gdal.Open(image)
        imgNA  = img.GetRasterBand(1).GetNoDataValue()
        print(imgNA)

        gtiff_driver = gdal.GetDriverByName('GTiff')
        out_ds = gtiff_driver.Create(storPath + '/' + image.split('/')[-1].split('.')[0] + '_fac2_average.tif', dum.RasterXSize, dum.RasterYSize, 1, img.GetRasterBand(1).DataType)
        out_ds.SetGeoTransform(dum.GetGeoTransform())
        out_ds.SetProjection(dum.GetProjection())
        out_ds.GetRasterBand(1).SetNoDataValue(imgNA)
        gdal.ReprojectImage(img, out_ds, img.GetProjection(), out_ds.GetProjection(), gdal.GRA_Average)
        del out_ds