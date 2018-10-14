from FloppyToolZ.Funci import *

modfolder1 = '/home/florus/MSc/RS_Data/MODIS/raw'
modfolder2 = '/home/florus/MSc/RS_Data/MODIS/raw2'
modHDF    = getFilelist(modfolder1, '.hdf')
modi  = gdal.Open(modHDF[0])
modis = gdal.Open(list(modi.GetMetadata('SUBDATASETS').values())[0])


Chac     = ogr.Open('/home/florus/MSc/GIS_Data/CHACO/CHACO_No_WET_Humid_LAEA_modFP_Sinusoidal.shp')
Chac_lyr = Chac.GetLayer()



gtiff_driver = gdal.GetDriverByName('GTiff')
out_ds = gtiff_driver.Create('/home/florus/MSc/RS_Data/MODIS/rasterized/Mod2.tiff',
                             modis.RasterXSize, modis.RasterYSize, 1, gdal.GDT_Float32)
out_ds.SetGeoTransform(modis.GetGeoTransform())
out_ds.SetProjection(modis.GetProjection())
Band = modis.GetRasterBand(1)
Band.SetNoDataValue(0)
gdal.RasterizeLayer(out_ds, [1], Chac_lyr, burn_values=[1])
del out_ds