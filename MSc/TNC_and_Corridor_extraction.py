from FloppyToolZ.MasterFuncs import *

# load Chaco dummy biomass
dumBM = gdal.Open('Y:/_students_data_exchange/FP_FP/Seafile/myLibrary/MSc/Modelling/GAP_FILLED/Single_VIs/prediction/Mosaic/check/masked/BM_Initial_Mosaic_masked_pred.tif')
# load Chaco dummy Landscape connectivity
dumLC = gdal.Open('Y:/_students_data_exchange/FP_FP/Seafile/myLibrary/MSc/Modelling/GAP_FILLED/Single_VIs/prediction/CS/check/Normalized_Input/BM_Initial_Mosaic_masked_pred_fac2_average_norm_reci.tif')
nam = ['BM', 'LscC']

# ### load biomass maps for extraction into numpy stack
bm = getFilelist('Y:/_students_data_exchange/FP_FP/Seafile/myLibrary/MSc/Modelling/GAP_FILLED/Single_VIs/prediction/Mosaic/check/masked', '.tif')
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
ini = pd.read_csv('Y:/_students_data_exchange/FP_FP/Seafile/myLibrary/MSc/Modelling/GAP_FILLED/Single_VIs/Modelling/runs_final_check/AllRuns_final_check.csv')
ind = np.where(np.logical_and(ini['ParVers'] == 'NDVI_GrowSeas_and_SeasPos_Mediannot_smooth', ini['ParSet'] == 'SeasPar_NDVI'))
init = float(ini.iloc[ind]['rmse'])
#min,max,median
iter100 = pd.read_csv('Y:/_students_data_exchange/FP_FP/Seafile/myLibrary/MSc/Modelling/GAP_FILLED/Single_VIs/Modelling/runs_check100_final/All100Runs_continue.csv')
savs    = getFilelist('Y:/_students_data_exchange/FP_FP/Seafile/myLibrary/MSc/Modelling/GAP_FILLED/Single_VIs/Modelling/runs_check100_final/sav_continue', '.sav')
sas     = getMinMaxMedianSAV(iter100, savs)
sa      = [s[2] for s in sas]
rmse    = [init, sa[1], sa[2], sa[0]]
rmse_nam = ['Initial', sas[1][0].split('_')[0], sas[2][0].split('_')[0], sas[0][0].split('_')[0]]

# load landscape connectivity maps for extraction into numpy stack
ls = getFilelist(r'Y:\_students_data_exchange\FP_FP\Seafile\myLibrary\MSc\Modelling\GAP_FILLED\Single_VIs\prediction\CS\checkunscaled\post\mean\scaled', '.tif')
ls.sort()
ls_nam = [l.split('/')[-1].split('.')[0] for l in ls]
cont2 = []
for l in ls:
    l1 = gdal.Open(l)
    l2 = l1.GetRasterBand(1)
    l3 = l2.ReadAsArray()
    l3[l3 == -9999] = np.nan
    cont2.append(l3)
ls_stack = np.dstack(cont2)


# define buffer sizes
buffer_sizes = [int(((i+1)*1000)/2) for i in range(20)]

# load TNC-file
tnc = ogr.Open('Y:/_students_data_exchange/FP_FP/Seafile/myLibrary/MSc/GIS_Data/TNC/TNC_dryverydry_sinusoidal_dissolve.shp', 0)
tnc_lyr = tnc.GetLayer()

sub_list = []
for feat in tnc_lyr:
    sub_list.append(feat.GetField('FID_Fina_1'))
tnc_lyr.ResetReading()

gtiff_driver = gdal.GetDriverByName('GTiff')
drvMemR = gdal.GetDriverByName('MEM')

# rasterize and extract
for i, dum in enumerate([dumBM, dumLC]):
    print(i)
    # create dictionary for tnc  output
    keys = ['FID_Fina_1', 'MAP', 'sum', 'median', 'min', 'max', 'quant_001', 'quant_01', 'quant_1', 'quant_2', 'quant_25', 'quant_50', 'quant_75', 'quant_98', 'quant_99', 'quant_999', 'quant_9999', 'mean', 'stdev', 'rmse', 'rmse_control', 'area_withNA',
            'area_withoutNA', 'dens_withNa', 'dens_withoutNA', 'numberNAs']
    vals = [list() for _ in keys]
    res = dict(zip(keys, vals))
    # create dictionary for LCP output
    keys2 = ['Link_ID', 'MAP', 'shape_control', 'FROM', 'TO', 'width', 'sum', 'median', 'min', 'max', 'quant_001', 'quant_01', 'quant_1', 'quant_2', 'quant_25', 'quant_50', 'quant_75', 'quant_98', 'quant_99', 'quant_999', 'quant_9999', 'mean', 'stdev', 'rmse',
             'rmse_control', 'area_withNA', 'area_withoutNA', 'dens_withNa', 'dens_withoutNA', 'numberNAs']
    vals2 = [list() for _ in keys2]
    res2 = dict(zip(keys2, vals2))

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
        tnc_lyr.SetAttributeFilter("FID_Fina_1 = {}".format(str(subby)))
        gdal.RasterizeLayer(sub, [1], tnc_lyr, burn_values=[subby])
        tnc_lyr.SetAttributeFilter(None)
        sub_arr = sub.ReadAsArray()
        rows, cols = np.where(sub_arr == subby)

        for j in range(stacki.shape[2]):
            res['FID_Fina_1'].append(subby)
            res['MAP'].append(namsi[j])
            vals = stacki[rows, cols,j]
            # convert densities to absolute values
            vals2 = vals * ((dum.GetGeoTransform()[1]**2) / 10000)
            res['sum'].append(np.nansum(vals2)) # absolute biomass
            res['median'].append(np.nanmedian(vals2))
            res['mean'].append(np.nanmean(vals2))
            res['stdev'].append(np.nanstd(vals2))
            res['min'].append(np.nanmin(vals2))
            res['max'].append(np.nanmax(vals2))
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
            res['rmse'].append(rmses[j] * (((dum.GetGeoTransform()[1]**2) * np.count_nonzero(~np.isnan(vals))) / 10000)) # absolut biomass
            res['rmse_control'].append(rmses[j])
            res['area_withNA'].append((dum.GetGeoTransform()[1]**2) * len(vals)) #per sqm
            res['area_withoutNA'].append((dum.GetGeoTransform()[1]**2) * np.count_nonzero(~np.isnan(vals))) #per sqm
            res['dens_withNa'].append(np.nansum(vals2) / (((dum.GetGeoTransform()[1]**2) * len(vals)) / 10000)) # per ha
            res['dens_withoutNA'].append(np.nansum(vals2) / (((dum.GetGeoTransform()[1]**2) * np.count_nonzero(~np.isnan(vals))) / 10000)) # per ha
            res['numberNAs'].append(np.count_nonzero(np.isnan(vals)))


    sub = drvMemR.Create('', dum.RasterXSize, dum.RasterYSize, 1, gdal.GDT_Int16)
    sub.SetGeoTransform(dum.GetGeoTransform())
    sub.SetProjection(dum.GetProjection())
    band = sub.GetRasterBand(1)
    band.SetNoDataValue(0)
    gdal.RasterizeLayer(sub, [1], tnc_lyr, burn_values=[subby])

    sub_arr = sub.ReadAsArray()
    rows, cols = np.where(sub_arr == subby)
    for j in range(stacki.shape[2]):
        res['FID_Fina_1'].append('All')
        res['MAP'].append(namsi[j])
        vals = stacki[rows, cols, j]
        # convert densities to absolute values
        vals2 = vals * ((dum.GetGeoTransform()[1] ** 2) / 10000)
        res['sum'].append(np.nansum(vals2))  # absolute biomass
        res['median'].append(np.nanmedian(vals2))
        res['mean'].append(np.nanmean(vals2))
        res['stdev'].append(np.nanstd(vals2))
        res['min'].append(np.nanmin(vals2))
        res['max'].append(np.nanmax(vals2))
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
        res['rmse'].append(rmses[j] * (
        ((dum.GetGeoTransform()[1] ** 2) * np.count_nonzero(~np.isnan(vals))) / 10000))  # absolut biomass
        res['rmse_control'].append(rmses[j])
        res['area_withNA'].append((dum.GetGeoTransform()[1] ** 2) * len(vals))  # per sqm
        res['area_withoutNA'].append(
            (dum.GetGeoTransform()[1] ** 2) * np.count_nonzero(~np.isnan(vals)))  # per sqm
        res['dens_withNa'].append(
            np.nansum(vals2) / (((dum.GetGeoTransform()[1] ** 2) * len(vals)) / 10000))  # per ha
        res['dens_withoutNA'].append(np.nansum(vals2) / (
        ((dum.GetGeoTransform()[1] ** 2) * np.count_nonzero(~np.isnan(vals))) / 10000))  # per ha
        res['numberNAs'].append(np.count_nonzero(np.isnan(vals)))
    #     conti += sub_arr
    #
    # out_ds = gtiff_driver.Create('Y:/_students_data_exchange/FP_FP/Seafile/myLibrary/MSc/LinkageMapper/extraction/TNC_' + nam[i] + '.tiff',
    #                              dum.RasterXSize, dum.RasterYSize, 1, gdal.GDT_Int16)
    # out_ds.SetGeoTransform(dum.GetGeoTransform())
    # out_ds.SetProjection(dum.GetProjection())
    # out_ds.GetRasterBand(1).WriteArray(conti)
    # out_ds.GetRasterBand(1).SetNoDataValue(0)
    #
    # del out_ds

# ######################################################### corridors
    # load LCPs
    lcps= getFilelist('Y:/_students_data_exchange/FP_FP/Seafile/myLibrary/MSc/LinkageMapper/Biomass', '.shp')
    for j, lcp in enumerate(lcps):
        print('start processing ' + lcp.split('/')[-1])
        lc = ogr.Open(lcp, 0)
        lc_lyr = lc.GetLayer()
        for buff in buffer_sizes:
            print('start with buffer size ' + str(buff))
            #  create in memory shapefile
            driv = ogr.GetDriverByName('MEMORY')
            #driv = ogr.GetDriverByName('ESRI Shapefile')
            source = driv.CreateDataSource('memData')
            #source = driv.CreateDataSource(r'Y:\_students_data_exchange\FP_FP\Seafile\myLibrary\MSc\LinkageMapper\extraction\shapes')
            out_lyr = source.CreateLayer(lcp.split('/')[-1].split('_')[0] + str(buff) + '_' + str(i), getSpatRefVec(lc), tnc_lyr.GetGeomType())
            out_lyr.CreateFields(lc_lyr.schema)
            out_feat = ogr.Feature(out_lyr.GetLayerDefn())
            # loop over every lcp within shapefile
            all_cont1 = []
            all_cont2 = []
            for feat in lc_lyr:
                ff = feat.GetField('From_Core')
                tt = feat.GetField('To_Core')
                res2['FROM'].append(ff)
                res2['TO'].append(tt)
                # loop over every buffer sizer
                #for buffer in buffer_sizes:
                geom = feat.geometry().Clone()
                # buffer it
                buffi = geom.Buffer(buff)
                # clip buffer with to and from core polygon - works at the moment only with multipolygon features, not multiple features per FID
                tnc_lyr.SetAttributeFilter("FID_Fina_1 = {}".format(str(ff)))
                cutter = tnc_lyr.GetNextFeature()
                buffi_cut = buffi.Difference(cutter.geometry())
                tnc_lyr.SetAttributeFilter(None)
                tnc_lyr.SetAttributeFilter("FID_Fina_1 = {}".format(str(tt)))
                cutter = tnc_lyr.GetNextFeature()
                buffi_cut2 = buffi_cut.Difference(cutter.geometry())
                # create layer from buffered lcp
                out_feat.SetGeometry(buffi_cut2)
                for ii in range(feat.GetFieldCount()):
                    out_feat.SetField(ii, feat.GetField(ii))
                out_lyr.CreateFeature(out_feat)
                # rasterize it
                sub = drvMemR.Create('', dum.RasterXSize, dum.RasterYSize, 1, gdal.GDT_Int16)
                sub.SetGeoTransform(dum.GetGeoTransform())
                sub.SetProjection(dum.GetProjection())
                band = sub.GetRasterBand(1)
                band.SetNoDataValue(0)
                gdal.RasterizeLayer(sub, [1], out_lyr, burn_values=[1])
                sub_arr = sub.ReadAsArray()
                rows, cols = np.where(sub_arr == 1)
                # extract
                res2['Link_ID'].append(feat.GetField('Link_ID'))
                res2['MAP'].append(namsi[j])
                res2['shape_control'].append(lcp.split('/')[-1].split('.')[0])
                res2['width'].append(buff*2)
                vals = stacki[rows, cols, j]
                # convert densities to absolute values
                vals2 = vals * ((dum.GetGeoTransform()[1] ** 2) / 10000)
                res2['sum'].append(np.nansum(vals2))
                res2['median'].append(np.nanmedian(vals2))
                res2['mean'].append(np.nanmean(vals2))
                res2['stdev'].append(np.nanstd(vals2))
                res2['min'].append(np.nanmin(vals2))
                res2['max'].append(np.nanmax(vals2))
                res2['quant_001'].append(np.nanquantile(vals2, 0.0001))
                res2['quant_01'].append(np.nanquantile(vals2, 0.001))
                res2['quant_1'].append(np.nanquantile(vals2, 0.01))
                res2['quant_2'].append(np.nanquantile(vals2, 0.02))
                res2['quant_25'].append(np.nanquantile(vals2, 0.25))
                res2['quant_50'].append(np.nanquantile(vals2, 0.5))
                res2['quant_75'].append(np.nanquantile(vals2, 0.75))
                res2['quant_98'].append(np.nanquantile(vals2, 0.98))
                res2['quant_99'].append(np.nanquantile(vals2, 0.99))
                res2['quant_999'].append(np.nanquantile(vals2, 0.999))
                res2['quant_9999'].append(np.nanquantile(vals2, 0.9999))
                res2['rmse'].append(
                    rmses[j] * (((dum.GetGeoTransform()[1] ** 2) * np.count_nonzero(~np.isnan(vals))) / 10000))
                res2['rmse_control'].append(rmses[j])
                res2['area_withNA'].append((dum.GetGeoTransform()[1] ** 2) * len(vals))
                res2['area_withoutNA'].append((dum.GetGeoTransform()[1] ** 2) * np.count_nonzero(~np.isnan(vals)))
                res2['dens_withNa'].append(
                    np.nansum(vals2) / (((dum.GetGeoTransform()[1] ** 2) * len(vals)) / 10000))  # per ha
                res2['dens_withoutNA'].append(np.nansum(vals2) / (
                ((dum.GetGeoTransform()[1] ** 2) * np.count_nonzero(~np.isnan(vals))) / 10000))  # per ha
                res2['numberNAs'].append(np.count_nonzero(np.isnan(vals)))
                all_cont1.append(vals)
                all_cont2.append(vals2)
            conni1 = all_cont1[0]
            for i9 in range(1,len(all_cont1)):
                conni1 = np.concatenate((conni1, all_cont1[i9]), axis = None)
            conni2 = all_cont2[0]
            for i9 in range(1, len(all_cont2)):
                conni2 = np.concatenate((conni2, all_cont2[i9]), axis=None)
            all_cont1 = conni1
            all_cont2 = conni2
            lc_lyr.ResetReading()
            res2['Link_ID'].append('All')
            res2['MAP'].append(namsi[j])
            res2['shape_control'].append(lcp.split('/')[-1].split('.')[0])
            res2['width'].append(buff * 2)
            res2['sum'].append(np.nansum(all_cont2))
            res2['median'].append(np.nanmedian(all_cont2))
            res2['mean'].append(np.nanmean(all_cont2))
            res2['stdev'].append(np.nanstd(all_cont2))
            res2['min'].append(np.nanmin(all_cont2))
            res2['max'].append(np.nanmax(all_cont2))
            res2['quant_001'].append(np.nanquantile(all_cont2, 0.0001))
            res2['quant_01'].append(np.nanquantile(all_cont2, 0.001))
            res2['quant_1'].append(np.nanquantile(all_cont2, 0.01))
            res2['quant_2'].append(np.nanquantile(all_cont2, 0.02))
            res2['quant_25'].append(np.nanquantile(all_cont2, 0.25))
            res2['quant_50'].append(np.nanquantile(all_cont2, 0.5))
            res2['quant_75'].append(np.nanquantile(all_cont2, 0.75))
            res2['quant_98'].append(np.nanquantile(all_cont2, 0.98))
            res2['quant_99'].append(np.nanquantile(all_cont2, 0.99))
            res2['quant_999'].append(np.nanquantile(all_cont2, 0.999))
            res2['quant_9999'].append(np.nanquantile(all_cont2, 0.9999))
            res2['rmse'].append(
                rmses[j] * (((dum.GetGeoTransform()[1] ** 2) * np.count_nonzero(~np.isnan(all_cont1))) / 10000))
            res2['rmse_control'].append(rmses[j])
            res2['area_withNA'].append((dum.GetGeoTransform()[1] ** 2) * np.count_nonzero(all_cont1))
            res2['area_withoutNA'].append((dum.GetGeoTransform()[1] ** 2) * np.count_nonzero(~np.isnan(all_cont1)))
            res2['dens_withNa'].append(
                np.nansum(vals2) / (((dum.GetGeoTransform()[1] ** 2) * np.count_nonzero(all_cont2)) / 10000))  # per ha
            res2['dens_withoutNA'].append(np.nansum(all_cont2) / (
                ((dum.GetGeoTransform()[1] ** 2) * np.count_nonzero(~np.isnan(all_cont1))) / 10000))  # per ha
            res2['numberNAs'].append(np.count_nonzero(np.isnan(all_cont1)))
            source.Destroy()

    df  = pd.DataFrame(data = res)
    df.to_csv('Y:/_students_data_exchange/FP_FP/Seafile/myLibrary/MSc/LinkageMapper/extraction/extract_TNC_all_' + nam[i] + '.csv', sep=',',index=False)

    df2  = pd.DataFrame(data = res2)
    df2.to_csv('Y:/_students_data_exchange/FP_FP/Seafile/myLibrary/MSc/LinkageMapper/extraction/extract_LCP_all_' + nam[i] + '.csv', sep=',',index=False)