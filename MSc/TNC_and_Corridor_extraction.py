from FloppyToolZ.MasterFuncs import *

# load Chaco dummy biomass
dumBM = gdal.Open('/home/florus/Seafile/myLibrary/MSc/Modelling/GAP_FILLED/Single_VIs/prediction/Mosaic/check/masked/BM_Initial_Mosaic_masked_pred.tif')
# load Chaco dummy Landscape connectivity
dumLC = gdal.Open('/home/florus/Seafile/myLibrary/MSc/Modelling/GAP_FILLED/Single_VIs/prediction/CS/check/Normalized_Input/BM_Initial_Mosaic_masked_pred_fac2_average_norm_reci.tif')
nam = ['BM', 'LscC']

# ### load biomass maps for extraction into numpy stack
bm = getFilelist('/home/florus/Seafile/myLibrary/MSc/Modelling/GAP_FILLED/Single_VIs/prediction/Mosaic/check/masked', '.tif')
bm.sort()
bm = bm[0:4]
bm_nam = [b.split('/')[-1].split('.')[0] for b in bm]
cont = []
for b in bm:
    b1 = gdal.Open(b)
    b2 = b1.GetRasterBand(1)
    b3 = b2.ReadAsArray()
    b3[b3 == -9999] = np.nan
    cont.append(b3)
bm_stack = np.dstack(cont)

# ### get rmse for biomass maps
# initial
ini = pd.read_csv('/home/florus/Seafile/myLibrary/MSc/Modelling/GAP_FILLED/Single_VIs/Modelling/runs_final_check/AllRuns_final_check.csv')
ind = np.where(np.logical_and(ini['ParVers'] == 'NDVI_GrowSeas_and_SeasPos_Mediannot_smooth', ini['ParSet'] == 'SeasPar_NDVI'))
init = float(ini.iloc[ind]['rmse'])
#min,max,median
iter100 = pd.read_csv('/home/florus/Seafile/myLibrary/MSc/Modelling/GAP_FILLED/Single_VIs/Modelling/runs_check100_final/All100Runs_continue.csv')
savs    = getFilelist('/home/florus/Seafile/myLibrary/MSc/Modelling/GAP_FILLED/Single_VIs/Modelling/runs_check100_final/sav_continue', '.sav')
sas     = getMinMaxMedianSAV(iter100, savs)
sa      = [s[2] for s in sas]
rmse    = [init, sa[1], sa[2], sa[0]]

# load landscape connectivity maps for extraction into numpy stack
# ls = getFilelist(path_needed, '.tif')
# ls.sort()
# ls_nam = [l.split('/')[-1].split('.')[0] for l in ls]
# cont2 = []
# for l in ls:
#     l1 = gdal.Open(l)
#     l2 = l1.GetRasterBand(1)
#     l3 = l2.ReadAsArray()
#     l3[l3 == -9999] = np.nan
#     cont2.append(l3)
# ls_stack = np.dstack(cont2)
# ###################################################################################just a test
ls_stack = np.dstack([dumLC.GetRasterBand(1).ReadAsArray()])
ls_nam = ['doof', 'superdoof']
# ###################################################################################test end
# create dictionary for output
keys = ['ID', 'MAP', 'min', 'max', 'mean','stdev', 'var', 'quant_001', 'quant_01', 'quant_1', 'quant_2','quant_25', 'quant_50', 'quant_75', 'quant_98', 'quant_99', 'quant_999', 'quant_9999', 'median', 'sum', 'rmse', 'area_withNA', 'area_withoutNA', 'dens_withNa', 'dens_withoutNA']
vals = [list() for _ in keys]
res  = dict(zip(keys, vals))

# load TNC-file
tnc = ogr.Open('/home/florus/Seafile/myLibrary/MSc/GIS_Data/TNC/TNC_dryverydry_sinusoidal_dissolve.shp', 0)
tnc_lyr = tnc.GetLayer()

sub_list = []
for feat in tnc_lyr:
    sub_list.append(feat.GetField('OBJECTID'))
tnc_lyr.ResetReading()

gtiff_driver = gdal.GetDriverByName('GTiff')
drvMemR = gdal.GetDriverByName('MEM')

# rasterize and extract
for i, dum in enumerate([dumBM, dumLC]):
    print(i)
    conti = np.zeros((dum.RasterYSize, dum.RasterXSize))
    if i == 0:
        stacki = bm_stack
        namsi = bm_nam
        rmses = rmse
    else:
        stacki = ls_stack
        namsi = ls_nam
        rmses = [0,0,0,0]

    for subby in sub_list:
        sub = drvMemR.Create('', dum.RasterXSize, dum.RasterYSize, 1, gdal.GDT_Int16)
        sub.SetGeoTransform(dum.GetGeoTransform())
        sub.SetProjection(dum.GetProjection())
        band = sub.GetRasterBand(1)
        band.SetNoDataValue(0)
        tnc_lyr.SetAttributeFilter("OBJECTID = {}".format(str(subby)))
        gdal.RasterizeLayer(sub, [1], tnc_lyr, burn_values=[subby])
        tnc_lyr.SetAttributeFilter(None)
        sub_arr = sub.ReadAsArray()
        rows, cols = np.where(sub_arr == subby)

        for j in range(stacki.shape[2]):
            res['ID'].append(subby)
            res['MAP'].append(namsi[j])
            vals = stacki[rows, cols,j]
            # convert densities to absolute values
            vals2 = vals * ((dum.GetGeoTransform()[1]**2) / 10000)
            res['min'].append(np.nanmin(vals2))
            res['max'].append(np.nanmax(vals2))
            res['mean'].append(np.nanmean(vals2))
            res['stdev'].append(np.nanstd(vals2))
            res['var'].append(np.nanvar(vals2))
            res['quant_001'].append(np.nanquantile(vals2, 0.0001))
            res['quant_01'].append(np.nanquantile(vals2, 0.001))
            res['quant_1'].append(np.nanquantile(vals2, 0.01))
            res['quant_2'].append(np.nanquantile(vals2, 0.02))
            res['quant_25'].append(np.nanquantile(vals2, 0.25))
            res['quant_50'].append(np.nanquantile(vals2, 0.5))
            res['quant_75'].append(np.nanquantile(vals2, 0.75))
            res['quant_98'].append(np.nanquantile(vals2, 0.98))
            res['quant_99'].append(np.nanquantile(vals2, 0.99))
            res['quant_999'].append(np.nanquantile(vals2, 0.999))
            res['quant_9999'].append(np.nanquantile(vals2, 0.9999))
            res['median'].append(np.nanmedian(vals2))
            res['sum'].append(np.nansum(vals2))
            res['rmse'].append(rmses[j] * (((dum.GetGeoTransform()[1]**2) * np.count_nonzero(~np.isnan(vals))) / 10000))
            res['area_withNA'].append((dum.GetGeoTransform()[1]**2) * len(vals))
            res['area_withoutNA'].append((dum.GetGeoTransform()[1]**2) * np.count_nonzero(~np.isnan(vals)))
            res['dens_withNa'].append(np.nansum(vals2) / (((dum.GetGeoTransform()[1]**2) * len(vals)) / 10000)) # per ha
            res['dens_withoutNA'].append(np.nansum(vals2) / (((dum.GetGeoTransform()[1]**2) * np.count_nonzero(~np.isnan(vals))) / 10000)) # per ha
    #     conti += sub_arr
    #
    # out_ds = gtiff_driver.Create('/home/florus/Seafile/myLibrary/MSc/LinkageMapper/extraction/TNC_' + nam[i] + '.tiff',
    #                              dum.RasterXSize, dum.RasterYSize, 1, gdal.GDT_Int16)
    # out_ds.SetGeoTransform(dum.GetGeoTransform())
    # out_ds.SetProjection(dum.GetProjection())
    # out_ds.GetRasterBand(1).WriteArray(conti)
    # out_ds.GetRasterBand(1).SetNoDataValue(0)
    #
    # del out_ds

df  = pd.DataFrame(data = res)
df.to_csv('/home/florus/Seafile/myLibrary/MSc/LinkageMapper/extraction/extract_TNC.csv', sep=',',index=False)




from FloppyToolZ.MasterFuncs import *

# dummy for rasterizing
dumBM = gdal.Open('/home/florus/Seafile/myLibrary/MSc/Modelling/GAP_FILLED/Single_VIs/prediction/Mosaic/check/masked/BM_Initial_Mosaic_masked_pred.tif')
# tnc areas for cutting buffered lcps
tnc  = ogr.Open('/home/florus/Seafile/myLibrary/MSc/GIS_Data/TNC/TNC_dryverydry_sinusoidal_dissolve.shp', 0)
tnc_lyr = tnc.GetLayer()
# lcps
test = ogr.Open('/home/florus/Seafile/myLibrary/MSc/LinkageMapper/Biomass/Initial_LCPs_BM.shp', 0)
test_lyr = test.GetLayer()

# define buffer sizes
buffer_sizes = [(i+1)*1000 for i in range(20)]

ShapeKiller('/home/florus/Seafile/myLibrary/MSc/LinkageMapper/Biomass/testi.shp')
#  create in memory shapefile
driv = ogr.GetDriverByName('ESRI Shapefile')
shapeStor = driv.CreateDataSource('/home/florus/Seafile/myLibrary/MSc/LinkageMapper/Biomass')
out_lyr = shapeStor.CreateLayer('testi', getSpatRefVec(test), tnc_lyr.GetGeomType())
out_lyr.CreateFields(test_lyr.schema)
out_feat = ogr.Feature(out_lyr.GetLayerDefn())


# loop over every lcp within shapefile
for feat in test_lyr:
    ff = feat.GetField('From_Core')
    tt = feat.GetField('To_Core')
    # loop over every buffer sizer
    #for buffer in buffer_sizes:
    geom = feat.geometry().Clone()
    # buffer it
    buffi = geom.Buffer(10000)
    # clip buffer with to and from core polygon
    tnc_lyr.SetAttributeFilter("FID_Fina_1 = {}".format(str(ff)))
    cutter = tnc_lyr.GetNextFeature()
    buffi_cut = buffi.Difference(cutter.geometry())
    tnc_lyr.SetAttributeFilter(None)
    tnc_lyr.SetAttributeFilter("FID_Fina_1 = {}".format(str(tt)))
    cutter = tnc_lyr.GetNextFeature()
    buffi_cut2 = buffi_cut.Difference(cutter.geometry())
    out_feat.SetGeometry(buffi_cut2)
    for i in range(feat.GetFieldCount()):
        out_feat.SetField(i, feat.GetField(i))
    out_lyr.CreateFeature(out_feat)
test_lyr.ResetReading()
shapeStor.Destroy()
