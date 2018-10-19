from FloppyToolZ.Funci import *

ras = gdal.Open('Z:/_students_data_exchange/BB_FP/nodata_cor/caucasus_lc_30m.img')
rast = ras.GetRasterBand(1)
rasti = rast.ReadAsArray()


vec = ogr.Open('Z:/_students_data_exchange/BB_FP/nodata_cor/Aze_Geo_Rus_greatCauc_ext.shp')
rasE = getExtentRas(ras)
vecE = getExtentVec(vec)

pix_size = ras.GetGeoTransform()[1]

colstart = int(( vecE['Xmin'] - rasE['Xmin']) / pix_size)
colend   = rasti.shape[1] - (int((rasE['Xmax'] - vecE['Xmax']) / pix_size))
rowend   = rasti.shape[0] - (int((vecE['Ymin'] - rasE['Ymin']) / pix_size))
rowstart = int((rasE['Ymax'] - vecE['Ymax']) / pix_size)


sub = rasti[rowstart:rowend, colstart:colend].copy()
sub[sub == rast.GetNoDataValue()] = 8
rasti[rowstart:rowend, colstart:colend] = sub
#
# sub = rasti[1:100,1:100].copy()
# subb = sub[5:10,5:10].copy()
# subb[subb == rast.GetNoDataValue()] = 5
# sub[5:10,5:10] = subb
# nodata = rast.GetNoDataValue()

gtiff_driver = gdal.GetDriverByName('HFA')
out_ds = gtiff_driver.Create('Z:/_students_data_exchange/BB_FP/nodata_cor/caucasus_lc_30m_MOD2.img', ras.RasterXSize, ras.RasterYSize,
                             1, rast.DataType)
out_ds.SetGeoTransform(ras.GetGeoTransform())
out_ds.SetProjection(ras.GetProjection())
out_ds.GetRasterBand(1).WriteArray(rasti)
out_ds.GetRasterBand(1).SetNoDataValue(rast.GetNoDataValue())

del out_ds