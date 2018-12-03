from FloppyToolZ.MasterFuncs import *

# get prediction biomass maps
BM_rasL = getFilelist('/home/florus/Seafile/myLibrary/MSc/Modelling/GAP_FILLED/Single_VIs/prediction/Mosaic', '.tif')
BM_rasL.sort()
BM_rasL = BM_rasL[0:4]

# group values
keys = ['Forest', 'Grassland', 'Savanna', 'Cropland', 'Pasture', 'Non_veg_area', 'Open_woodland','Water', 'Wetland']
vals = [[1], [2,15,16], [3], [4,10,12,14,20,21,22,23], [5,11,13,18,19], [6,9], [17], [7], [8]]
LCc  = dict(zip(keys, vals))
# create output dictionary
keys2 = [b.split('/')[-1].split('.')[0] for b in BM_rasL] + ['LC']
vals2 = [list() for _ in range(len(keys2))]
res   = dict(zip(keys2, vals2))
# load biomass predictions into np arrays
obm  = []
for map in BM_rasL:
    print(map)
    q = gdal.Open(map)
    w = q.GetRasterBand(1)
    e = q.ReadAsArray()
    obm.append(e)

# draw random samples within LC classe
LCras = gdal.Open('/home/florus/Seafile/myLibrary/MSc/other_maps_biomass_matthias/resample/baumann-etal_2017_LandCover-Map-CHACO_GlobalChangeBiology_repro_resamp_average_to_MODIS.tif')
bb = LCras.GetRasterBand(1)
cc = bb.ReadAsArray()
bb_NA = bb.GetNoDataValue()

# get a row/col indices of a random sample per LC class
for k, v in LCc.items():
    print('Find points for ',k)
    rows, cols = np.where(np.isin(cc, v))
    print(len(rows))
    if len(rows) > 10000:
        indi = np.random.choice(len(rows), 10000, False)
    else:
        indi = np.random.choice(len(rows), len(rows), False)
    rows, cols = rows[indi], cols[indi]
    # extract the values for row/col indices
    for i in range(len(rows)):
        res['LC'].append(k)
        for j in range(len(obm)):
            res[keys2[j]].append(obm[j][rows[i], cols[i]])

df  = pd.DataFrame(data = res)
df.replace(-9999, 'NA')
df.to_csv('/home/florus/Seafile/myLibrary/MSc/other_maps_biomass_matthias/LCC_comparison10000_gf_orig.csv', sep=',',index=False)