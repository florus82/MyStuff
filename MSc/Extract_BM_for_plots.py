from FloppyToolZ.MasterFuncs import *

# get prediction biomass maps
BM_rasL = getFilelist('/home/florus/Seafile/myLibrary/MSc/Modelling/GAP_FILLED/Single_VIs/prediction/Mosaic/check/masked', '.tif')
BM_rasL.sort()
BM_rasL = BM_rasL[0:4]

# get biomass maps for comparison
extraL  = getFilelist('/home/florus/Seafile/myLibrary/MSc/other_maps_biomass_matthias/resample', '.tif')
killer  = ['/home/florus/Seafile/myLibrary/MSc/other_maps_biomass_matthias/resample/baumann-etal_2017_LandCover-Map-CHACO_GlobalChangeBiology_repro_resamp_average_to_MODIS.tif','/home/florus/Seafile/myLibrary/MSc/other_maps_biomass_matthias/resample/20S_060W_biomass_repro_resamp_average_to_MODIS.tif','/home/florus/Seafile/myLibrary/MSc/other_maps_biomass_matthias/resample/20S_070W_biomass_repro_resamp_average_to_MODIS.tif']

for kill in killer:
    extraL.remove(kill)
# create output dictionary
keys = [b.split('/')[-1].split('.')[0] for b in BM_rasL] + [e.split('/')[-1].split('.')[0].split('_repro_resamp_average_to_MODIS')[0] for e in extraL] + ['category']
vals = [list() for _ in range(len(keys))]
res  = dict(zip(keys, vals))
# load median and min bm predictions and other biomass maps/TC+SC for extraction
obm  = []
for map in BM_rasL[1:4] + extraL:
    print(map)
    q = gdal.Open(map)
    w = q.GetRasterBand(1)
    e = q.ReadAsArray()
    obm.append(e)

# use BM_max to draw random samples within biomass strata
aa = gdal.Open(BM_rasL[0])
bb = aa.GetRasterBand(1)
cc = bb.ReadAsArray()
bb_NA = bb.GetNoDataValue()
# define stratas from which samples to be drawn
start_seq = [i for i in range(0,int(np.max(cc)),20)]
end_seq   = [i+20 for i in start_seq]
# get a row/col indices of a random sample per biomass strata step
for i in range(len(start_seq)):
    rows, cols = np.where(np.logical_and(np.logical_and(cc != bb_NA, cc >= start_seq[i]), cc < end_seq[i]))
    if len(rows) > 5000:
        indi = np.random.choice(len(rows), 5000, False)
    else:
        indi = np.random.choice(len(rows), len(rows), False)
    print(len(indi))
    rows, cols = rows[indi], cols[indi]

    # extract the values for row/col indices
    for j in range(len(rows)):
        res['category'].append(str(start_seq[i]) + '_to_'+ str(end_seq[i]))
        res[keys[0]].append(cc[rows[j], cols[j]])
        for k in range(len(obm)):
            res[keys[k+1]].append(obm[k][rows[j], cols[j]])

df  = pd.DataFrame(data = res)
df.replace(-9999, 'NA')
df.to_csv('/home/florus/Seafile/myLibrary/MSc/PLOTS_FINAL/extracts/map_comparison5000_colloq_20.csv', sep=',',index=False)