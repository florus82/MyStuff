from FloppyToolZ.MasterFuncs import *

# set working station
# path1 = '/home/florus/MSc/'
path1 = 'Y:/_students_data_exchange/FP_FP/'
# path2 = '/home/florus/Seafile/myLibrary/MSc/'
path2 = 'Y:/_students_data_exchange/FP_FP/Seafile/myLibrary/MSc/'

# ########################################################################## load monster-cube
# get a list for all masks/tiles --> this is highest hierarchical order: set manually to not blow geoserv2
maskL = getFilelist(path1 + 'RS_Data/MODIS/rasterized', '.tiff')

tile = 'Mod3'
ma   = maskL[2] ################# manual set!!!!!!!!!!!!!!!!
mas  = gdal.Open(ma)
mask  = mas.GetRasterBand(1).ReadAsArray()
mask[mask == 0] = np.nan
# subset study area to smallest bbox possible due to np.nan frame removal
reader = shrinkNAframe(mask)
mask  = mas.GetRasterBand(1).ReadAsArray(reader[0], reader[1], reader[2], reader[3])
mask[mask == 0] = np.nan

# set time-frame for prediction
months = ['Jul', 'Aug', 'Sep']
syears = [2013, 2014, 2015] # 3 pairs as some plots only in 2010-2012
sequen = [[15, m, sy, 14, m, sy+1] for m in months for sy in syears]
timeframe = [time_seq(seq[0], seq[1], seq[2], seq[3], seq[4], seq[5]) for seq in sequen]


# set needed bands to extract, their corresponding NA values and accepted Quality flags
bands  = ['NDVI', 'EVI', 'NIR reflectance', 'MIR reflectance', 'pixel reliability', 'VI Quality']
NaList = [-3000, -1000, -3000, -1000, 65535, 255]
QA_oki = [2112, 4160, 6208]


# #################################### bring MODIS scenes in timely order
# get list for individual container in respective raw-folder
modHDF = getFilelist(path1 + 'RS_Data/MODIS/raw/raw' + ma.split('.')[0][-1], '.hdf')
# make list time-readable
modTim = [int(hdf.split('.')[1][1:5] + hdf.split('.')[1][5:8]) for hdf in modHDF]
# scenes have to be ordered chronological!!
mdict   = dict(zip(modTim, modHDF))
modHDFs = [v for k ,v in sorted(mdict.items())]
modTims = [k for k ,v in sorted(mdict.items())]

# load monster block
tile_NDVI_conti = []
# tile_EVI_conti  = []
# tile_NBR_conti  = []
tile_timeline   = []
tile_dummy      = []

for tims in timeframe:
    # tims = timeframe[0]
    print('subsetting MODIS files for periods ' + str(tims[0]) + ' to ' + str(tims[1]))
    # find scenes from timeframe in modHDF and time
    modOrd = [[modHDFs[i], modTims[i]] for i in range(len(modTims)) if modTims[i] >= tims[0] and modTims[i] <= tims[1]]
    hdf = [i[0] for i in modOrd]
    tim = [i[1] for i in modOrd]
    # create a doy-object which can be used for PixelBreaker for this specific sequence
    timeline, dummy = ModTimtoInt(tim)
    tile_timeline.append(timeline)
    tile_dummy.append(dummy)

    for iter3, scene in enumerate(hdf):
        # print(iter3)
        # scene = hdf[0]
        info = gdal.Open(scene)
        sdsdict = info.GetMetadata('SUBDATASETS')
        sdslist = [sdsdict[k] for k in sdsdict.keys() if '_NAME' in k]
        select = [img for img in sdslist for sub in bands if img.endswith(sub)]
        select.sort()

        qual = gdal.Open(select[4])
        qual_arr = qual.GetRasterBand(1).ReadAsArray(reader[0], reader[1], reader[2], reader[3])
        qualMask = np.where(np.isin(qual_arr, QA_oki), 1, np.nan)
        powerMask = qualMask * mask

        # load NDVI, EVI, calc NBR and store them int individual into tile-based lists
        ndvi = gdal.Open(select[2])
        ndviB = ndvi.GetRasterBand(1)
        tile_NDVI_conti.append((ndviB.ReadAsArray(reader[0], reader[1], reader[2], reader[3]) * powerMask )/10000)

        # evi = gdal.Open(select[0])
        # eviB = evi.GetRasterBand(1)
        # tile_EVI_conti.append((eviB.ReadAsArray(reader[0], reader[1], reader[2], reader[3]) * powerMask)/10000)
        #
        # mir = gdal.Open(select[1])
        # mirB = mir.GetRasterBand(1)
        # mirA = mirB.ReadAsArray(reader[0], reader[1], reader[2], reader[3]) * powerMask
        # nir = gdal.Open(select[3])
        # nirB = nir.GetRasterBand(1)
        # nirA = nirB.ReadAsArray(reader[0], reader[1], reader[2], reader[3]) * powerMask
        # tile_NBR_conti.append((nirA - mirA) / (nirA + mirA))

# dump all VI-timeseries dfs tile-wise in the list
print('putting lists together')
VI_conti = tile_NDVI_conti # + tile_EVI_conti + tile_NBR_conti
print('deleting lists')
del tile_NDVI_conti #, tile_EVI_conti, tile_NBR_conti
print('stacking list')
monster_block = np.stack(VI_conti, axis = 2)
print('deleting list')
del VI_conti

# dump timeline and dummy list
joblib.dump(tile_timeline,path1 + 'MSc_outside_Seafile/' + tile + '/time/timeline.sav')
joblib.dump(tile_dummy,path1 + 'MSc_outside_Seafile/' + tile + '/time/dummy.sav')

# set number of tiles and create cutter
no_tiles = 36**2

keys = ['x_off', 'y_off', 'x_count', 'y_count']

y_off_L   = [i for i in range(0, mask.shape[0], math.ceil(mask.shape[0] / int(no_tiles**0.5)))]
ydum      = y_off_L + [mask.shape[0]]
y_count_L = [ydum[i+1] - y_off_L[i] for i in range(len(y_off_L))]

x_off_L   = [i for i in range(0, mask.shape[1], math.ceil(mask.shape[1] / int(no_tiles**0.5)))]
xdum      = x_off_L + [mask.shape[1]]
x_count_L = [xdum[i+1] - x_off_L[i] for i in range(len(x_off_L))]

vals = [x_off_L * int(no_tiles**0.5), [i for i in y_off_L for _ in range(int(no_tiles**0.5))],
        x_count_L * int(no_tiles**0.5), [i for i in y_count_L for _ in range(int(no_tiles**0.5))]]
subtil = dict(zip(keys, vals))

# slice monsterblock and dump cubes
for i in range(no_tiles):
    print('tiling : ' + str(i))
   #print(str(subtil['y_off'][i])+ ' till ' + str(subtil['y_count'][i] + subtil['y_off'][i]) + ' and ' + str(subtil['x_off'][i]) + ' till ' + str(subtil['x_count'][i] + subtil['x_off'][i]))
    sub = monster_block[subtil['y_off'][i]:(subtil['y_count'][i] + subtil['y_off'][i]),
          subtil['x_off'][i]:(subtil['x_count'][i] + subtil['x_off'][i]),:]

    joblib.dump(sub, path1 + 'MSc_outside_Seafile/' + tile + '/cubes/cube_' + 'X_' +str(subtil['x_off'][i]) + '_' +\
                    str(subtil['x_off'][i] + subtil['x_count'][i]) +\
                    '__Y_' +str(subtil['y_off'][i]) + '_' + str(subtil['y_off'][i] + subtil['y_count'][i]) +'.sav')
