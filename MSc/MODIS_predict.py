from FloppyToolZ.Funci import *

# working station
path = '/home/florus/'
# path =

# set needed bands to extract, their corresponding NA values and accepted Quality flags
bands  = ['NDVI', 'EVI', 'NIR reflectance', 'MIR reflectance', 'pixel reliability', 'VI Quality']
NaList = [-3000, -1000, -3000, -1000, 65535, 255]
QA_oki = [2112, 4160, 6208]

# set time-frame for prediction
# month == first three letters of months, e.g. Jan for January
# need years 2005, 2006, 2007, 2010, 2011, 2012
# seasons jul-jul, aug-aug, sep

def time_seq(start_day, start_month, start_year,
             end_day, end_month, end_year):
     start = int(str(start_year) + str(getJulianDay(start_day, start_month, start_year)))
     end   = int(str(end_year) + str(getJulianDay(end_day, end_month, end_year)))

     return [start, end]

months = ['Jul', 'Aug', 'Sep']
syears = [2005, 2006, 2007, 2010, 2011, 2012] # 3 pairs as some plots only in 2010-2012
sequen = [[15, m, sy, 14, m, sy+1] for m in months for sy in syears]

timeframe = [time_seq(seq[0], seq[1], seq[2], seq[3], seq[4], seq[5]) for seq in sequen]
indexer   = [[m, m + int(len(syears)/2)] for m in [i + j for i in range(len(months))
                                       for j in [i*len(syears)
                                                 for i in range(len(months))]]]


# ######################predictions are MODIS-tile based
# get a list for all masks
maskL = getFilelist(path + 'MSc/RS_Data/MODIS/rasterized', '.tiff')

# loop over masks (equals looping over tiles

#for mask in maskL:
    mas   = maskL[0] # for testing; will be replaced in the end through courser
    mask  = gdal.Open(mas)
    mask  = mask.GetRasterBand(1).ReadAsArray()
    mask[mask == 0] = np.nan
    # get list for individual container in respective raw-folder
    modHDF = getFilelist(path + 'MSc/RS_Data/MODIS/raw/raw' + mas.split('.')[0][-1], '.hdf')
    # make list time-readable
    modTim = [int(hdf.split('.')[1][1:5] + hdf.split('.')[1][5:8]) for hdf in modHDF]
    # subset filelist to list of needed files
    #for indi in indexer:
        indi = indexer[0]# for testing; will be replaced in the end through courser
        print('subsetting MODIS files for periods ' + str(timeframe[indi[0]][0]) + ' to ' +
              str(timeframe[indi[0]][1]) + ' and ' + str(timeframe[indi[1]][0]) + ' to ' +
              str(timeframe[indi[1]][1]))

        # find scenes from timeframe in modHDF; first, scenes have to be ordered chronological!!
        mdict  = dict(zip(modTim, modHDF))
        modOrd = [v for k ,v in sorted(mdict.items())]
        modSub = [modHDF[i] for i in range(len(modTim)) if
                modTim[i] >= timeframe[indi[0]][0] and
                    modTim[i] <= timeframe[indi[0]][1]]

        # build a numpy container for all scenes' VIs'
        aa = np.empty((mask.shape[0], mask.shape[1], len(modSub)))
        aa = np.empty((4800,4800,46))
        #for scene in modSub:
            scene = modSub[0]# for testing; will be replaced in the end through courser
            info = gdal.Open(scene)
            sdsdict = info.GetMetadata('SUBDATASETS')
            sdslist = [sdsdict[k] for k in sdsdict.keys() if '_NAME' in k]
            select = [img for img in sdslist for sub in bands if img.endswith(sub)]
            select.sort()

            qual      = gdal.Open(select[4])
            qualBand  = qual.GetRasterBand(1)
            qual_arr  = qualBand.ReadAsArray()
            qualMask  = np.where(np.isin(qual_arr, QA_oki), 1, np.nan)
            powerMask = qualMask * mask
            # load NDVI, EVI, calc NBR, mask them and load them int individual into stacks
            ndvi  = gdal.Open(select[2])
            ndviB = ndvi.GetRasterBand(1)
            ndviA = ndviB.ReadAsArray()
            ndviM = ndviA * powerMask
            evi   = gdal.Open(select[0])
            mir   = gdal.Open(select[1])
            nir   = gdal.Open(select[3])

            # do seasonal parameter derivation via np.alonga_axis (outside of this loop)

