from FloppyToolZ.MasterFuncs import *

SPs = getFilelist('/home/florus/Seafile/myLibrary/MSc/Modelling/GAP_FILLED/Single_VIs/prediction/Mosaic/check/masked', '.tif')
SPs.sort()
SPs = SPs[4:]
#SPs = SPs[::3]

keys = ['SPs', 'SP', 'Perf','min', 'max', 'mean','stdev', 'var', 'quant_001', 'quant_01', 'quant_1', 'quant_2','quant_25', 'quant_50', 'quant_75', 'quant_98', 'quant_99', 'quant_999', 'quant_9999', 'median']
vals = [list() for _ in range(len(keys))]
res  = dict(zip(keys, vals))

for sp in SPs:
    print(sp)
    a = gdal.Open(sp)
    b = a.GetRasterBand(1)
    c = b.ReadAsArray()
    c[c == b.GetNoDataValue()] = np.nan

    res['SPs'].append(sp.split('/')[-1].split('.')[0].split('_Mosaic')[0])
    res['SP'].append(sp.split('/')[-1].split('.')[0].split('_')[0])
    res['Perf'].append(sp.split('/')[-1].split('.')[0].split('_')[1])
    res['min'].append(np.nanmin(c))
    res['max'].append(np.nanmax(c))
    res['mean'].append(np.nanmean(c))
    res['stdev'].append(np.nanstd(c))
    res['var'].append(np.nanvar(c))
    res['quant_001'].append(np.nanquantile(c, 0.0001))
    res['quant_01'].append(np.nanquantile(c, 0.001))
    res['quant_1'].append(np.nanquantile(c, 0.01))
    res['quant_2'].append(np.nanquantile(c, 0.02))
    res['quant_25'].append(np.nanquantile(c, 0.25))
    res['quant_50'].append(np.nanquantile(c, 0.5))
    res['quant_75'].append(np.nanquantile(c, 0.75))
    res['quant_98'].append(np.nanquantile(c, 0.98))
    res['quant_99'].append(np.nanquantile(c, 0.99))
    res['quant_999'].append(np.nanquantile(c, 0.999))
    res['quant_9999'].append(np.nanquantile(c, 0.9999))
    res['median'].append(np.nanmedian(c))

df  = pd.DataFrame(data = res)
df.to_csv('/home/florus/Seafile/myLibrary/MSc/PLOTS_FINAL/extracts/pred_ranges4.csv', sep=',',index=False)










