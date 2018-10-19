from FloppyToolZ.MasterFuncs import *
import time

# set working station
# path1 = '/home/florus/MSc/'
path1 = 'Z:/_students_data_exchange/FP_FP/'
# path2 = '/home/florus/Seafile/myLibrary/MSc/'
path2 = 'Z:/_students_data_exchange/FP_FP/Seafile/myLibrary/MSc/'

# load models for lowest,median and highest RMSE) - should all be part of apply_along_axis
iter100 = pd.read_csv(path2 + 'Modelling/runs100/AllRuns.csv')
savs    = getFilelist(path2 + 'Modelling/runs100/sav', '.sav')
sav     = getMinMaxMedianSAV(iter100, savs)

# VIs
VIS = ['NDVI', 'EVI', 'NBR']
# how many seasonal parameter per VI
no_seaspar = 7

# set time-frame for prediction
months = ['Jul', 'Aug', 'Sep']
syears = [2013, 2014, 2015] # 3 pairs as some plots only in 2010-2012
sequen = [[15, m, sy, 14, m, sy+1] for m in months for sy in syears]
timeframe = [time_seq(seq[0], seq[1], seq[2], seq[3], seq[4], seq[5]) for seq in sequen]

# set needed bands to extract, their corresponding NA values and accepted Quality flags
bands  = ['NDVI', 'EVI', 'NIR reflectance', 'MIR reflectance', 'pixel reliability', 'VI Quality']
NaList = [-3000, -1000, -3000, -1000, 65535, 255]
QA_oki = [2112, 4160, 6208]

# get a list for all masks/tiles --> this is highest hierarchical order: set manually to not blow geoserv2
maskL = getFilelist(path1 + 'RS_Data/MODIS/rasterized', '.tiff')

ma   = maskL[0] ################# manual set!!!!!!!!!!!!!!!!
mas  = gdal.Open(ma)
mask  = mas.GetRasterBand(1).ReadAsArray()
mask[mask == 0] = np.nan
# subset study area to smallest bbox possible due to np.nan frame removal
reader = shrinkNAframe(mask)
mask  = mas.GetRasterBand(1).ReadAsArray(reader[0], reader[1], reader[2], reader[3])
mask[mask == 0] = np.nan
# ################################ create 48 sub-tiles of this subset --> number of sub-tiles == number of jobs

no_tiles = 5**2

keys = ['x_off', 'y_off', 'x_count', 'y_count']

y_off_L   = [i for i in range(0, mask.shape[0], math.floor(mask.shape[0] / int(no_tiles**0.5)))]
ydum      = y_off_L + [mask.shape[0]]
y_count_L = [ydum[i+1] - y_off_L[i] for i in range(len(y_off_L))]

x_off_L   = [i for i in range(0, mask.shape[1], math.ceil(mask.shape[1] / int(no_tiles**0.5)))]
xdum      = x_off_L + [mask.shape[1]]
x_count_L = [xdum[i+1] - x_off_L[i] for i in range(len(x_off_L))]

vals = [x_off_L * int(no_tiles**0.5), [i for i in y_off_L for _ in range(int(no_tiles**0.5))],
        x_count_L * int(no_tiles**0.5), [i for i in y_count_L for _ in range(int(no_tiles**0.5))]]
subtil = dict(zip(keys, vals))

# #################################### bring MODIS scenes in timely order
# get list for individual container in respective raw-folder
modHDF = getFilelist(path1 + 'RS_Data/MODIS/raw/raw' + ma.split('.')[0][-1], '.hdf')
# make list time-readable
modTim = [int(hdf.split('.')[1][1:5] + hdf.split('.')[1][5:8]) for hdf in modHDF]
# scenes have to be ordered chronological!!
mdict   = dict(zip(modTim, modHDF))
modHDFs = [v for k ,v in sorted(mdict.items())]
modTims = [k for k ,v in sorted(mdict.items())]

# ########################################################################### build lists for joblist

Tile_job      = []
Tile_Timeline = []
Tile_dummy    = []
Tile_outPath  = []

# tileblock-list
for tile_iter in range(no_tiles):
    tile_iter = 0
    tile_NDVI_conti = []
    tile_EVI_conti  = []
    tile_NBR_conti  = []
    tile_timeline   = []
    tile_dummy      = []
    print(tile_iter)
    for tims in timeframe:
        tims = timeframe[0]
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
            # scene = hdf[0]
            print(iter3)
            info = gdal.Open(scene)
            sdsdict = info.GetMetadata('SUBDATASETS')
            sdslist = [sdsdict[k] for k in sdsdict.keys() if '_NAME' in k]
            select = [img for img in sdslist for sub in bands if img.endswith(sub)]
            select.sort()

            qual = gdal.Open(select[4])
            qual_arr = qual.GetRasterBand(1).ReadAsArray(subtil['x_off'][tile_iter], subtil['y_off'][tile_iter],
                                                         subtil['x_count'][tile_iter], subtil['y_count'][tile_iter])
            qualMask = np.where(np.isin(qual_arr, QA_oki), 1, np.nan)

            powerMask = qualMask * mask[subtil['y_off'][tile_iter]:(subtil['y_count'][tile_iter] + subtil['y_off'][tile_iter]),
                                   subtil['x_off'][tile_iter]:(subtil['x_count'][tile_iter] + subtil['x_off'][tile_iter])]

            # load NDVI, EVI, calc NBR and store them int individual into tile-based lists
            ndvi = gdal.Open(select[2])
            ndviB = ndvi.GetRasterBand(1)
            tile_NDVI_conti.append((ndviB.ReadAsArray(subtil['x_off'][tile_iter], subtil['y_off'][tile_iter],
                    subtil['x_count'][tile_iter], subtil['y_count'][tile_iter]) * powerMask)/10000)

            evi = gdal.Open(select[0])
            eviB = evi.GetRasterBand(1)
            tile_EVI_conti.append((eviB.ReadAsArray(subtil['x_off'][tile_iter], subtil['y_off'][tile_iter],
                    subtil['x_count'][tile_iter], subtil['y_count'][tile_iter]) * powerMask)/10000)

            mir = gdal.Open(select[1])
            mirB = mir.GetRasterBand(1)
            mirA = mirB.ReadAsArray(subtil['x_off'][tile_iter], subtil['y_off'][tile_iter],
                                subtil['x_count'][tile_iter], subtil['y_count'][tile_iter]) * powerMask
            nir = gdal.Open(select[3])
            nirB = nir.GetRasterBand(1)
            nirA = nirB.ReadAsArray(subtil['x_off'][tile_iter], subtil['y_off'][tile_iter],
                                subtil['x_count'][tile_iter], subtil['y_count'][tile_iter]) * powerMask
            tile_NBR_conti.append((nirA - mirA) / (nirA + mirA))

    # dump all VI-timeseries dfs tile-wise in the list
    VI_conti = tile_NDVI_conti + tile_EVI_conti + tile_NBR_conti
    Tile_job.append(np.stack(VI_conti, axis = 2))
    del tile_NDVI_conti, tile_EVI_conti, tile_NBR_conti

    # dump the dummy (for prediction) and timeline (for training and length of images per timeframe) lists in the tile-list
    Tile_dummy.append(tile_dummy)
    Tile_Timeline.append(tile_timeline)

    # set storage path for the result of this tile (after PixelSmasher is done with it ;-) )
    Tile_outPath.append(path2 + 'MSc/Modelling/prediction/megadump/tile_SP_' + 'X_' +str(subtil['x_off'][tile_iter]) + '_' +\
                        str(subtil['x_off'][tile_iter] + subtil['x_count'][tile_iter]) +\
                        '__Y_' +str(subtil['y_off'][tile_iter]) + '_' + str(subtil['y_off'][tile_iter] + subtil['y_count'][tile_iter]) +'.sav')




# ############################ create joblist
jobs = [[Tile_job[divi], PixelBreaker_BoneStorm, Tile_Timeline[divi], Tile_dummy[divi],\
         Tile_outPath[divi]] for divi in range(no_tiles)]

if __name__ == '__main__':
# ####################################### SET TIME COUNT ###################################################### #
    starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print("--------------------------------------------------------")
    print("Starting process, time:" +  starttime)
    print("")


    Parallel(n_jobs=25)(delayed(PixelSmasher())(i[0], i[1], i[2], i[3], i[4]) for i in jobs)

    print("")
    endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print("--------------------------------------------------------")
    print("--------------------------------------------------------")
    print("start: " + starttime)
    print("end: " + endtime)
    print("")