from FloppyToolZ.MasterFuncs import *

# load files
imgs = getFilelist('Z:/_LANDSAT/annual_Metrics', '.vrt')

bin = getFilelist('Y:/ASP_FP/reclassified_maps','.tif')

buf = ogr.Open('Y:/ASP_FP/buffers_birds_mammals.shp')

# ### create a binary raster mask for the buffered plot extents
# open dummy raster
# dum  = gdal.Open(bin[0])
# buf_lyr = buf.GetLayer()
#
# gtiff_driver = gdal.GetDriverByName('GTiff')
# out_ds = gtiff_driver.Create('Y:/ASP_FP/Validation/processing/buffer_mask.tif',
#                              dum.RasterXSize, dum.RasterYSize, 1, gdal.GDT_Byte)
# out_ds.SetGeoTransform(dum.GetGeoTransform())
# out_ds.SetProjection(dum.GetProjection())
# #Band = dum.GetRasterBand(1)
# #Band.SetNoDataValue(0)
# gdal.RasterizeLayer(out_ds, [1], buf_lyr, burn_values=[5])
# del out_ds

mask  = gdal.Open('Y:/ASP_FP/Validation/processing/buffer_mask.tif')
mas   = mask.GetRasterBand(1)
maski = mas.ReadAsArray()

# dictionary for F-NF areas per year within buffer
k = ['Year', 'Class', 'Area_in_ha']
v = [[] for _ in k]
res = dict(zip(k, v))

# random sample per year
for b in bin:
    year  = b.split('_')[-1].split('.')[0]
    ras   = gdal.Open(b)
    gt    = ras.GetGeoTransform()
    rast  = ras.GetRasterBand(1)
    rasti = rast.ReadAsArray()
    # Forest samples
    F_row, F_col = np.where(np.logical_and(maski[:, :] == 5, rasti[:, :] == 1))
    res['Year'].append(year)
    res['Class'].append('F')
    res['Area_in_ha'].append(len(F_row)*900/10000)
    # F_rs  = np.random.choice(range(len(F_row)), 50, replace=False)
    # Fx_rs  = (gt[0] + gt[1]/2) + gt[1] * F_col[F_rs]
    # Fy_rs  = (gt[3] + gt[5]/2) + gt[5] * F_row[F_rs]
    # NF samples
    NF_row, NF_col = np.where(np.logical_and(maski[:, :] == 5, rasti[:, :] == 0))
    res['Year'].append(year)
    res['Class'].append('NF')
    res['Area_in_ha'].append(len(NF_row)*900/10000)
    # NF_rs = np.random.choice(range(len(NF_row)), 50, replace=False)
    # NFx_rs = (gt[0] + gt[1] / 2) + gt[1] * NF_col[NF_rs]
    # NFy_rs = (gt[3] + gt[5] / 2) + gt[5] * NF_row[NF_rs]
    # export as shape
    # xy = {'X': np.concatenate((Fx_rs, NFx_rs)), 'Y': np.concatenate((Fy_rs, NFy_rs))}
    # ids = {'ID': [i+1 for i in range(len(xy['X']))], 'LC': ['F' for _ in range(50)]+['NF' for _ in range(50)]}

    # XYtoShape(xy, ids, getSpatRefRas(ras), 'Y:/ASP_FP/Validation/processing', year + 'random_samples', 'point')
    print(year)
df = pd.DataFrame(data=res)
df.to_csv('K:/Seafile/Uni_Life/Contribution/Asun/buffer_class_areas.csv',
        sep=',', index=False)
