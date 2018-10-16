from FloppyToolZ.Funci import *
from scipy import optimize

def funci(x, p1, p2, p3, p4, p5, p6):
    return p1 +p2 * ((1 / (1 + np.exp((p3 - x) / p4))) - (1 / (1 + np.exp((p5 - x) / p6))))

def fitter(x, SoS_ndvi, EoS_ndvi, SeasMax_ndvi, SeasMin_ndvi, SeasInt_ndvi, SeasLen_ndvi, SeasAmp_ndvi,
           SoS_evi, EoS_evi, SeasMax_evi, SeasMin_evi, SeasInt_evi, SeasLen_evi, SeasAmp_evi,
           SoS_nbr, EoS_nbr, SeasMax_nbr, SeasMin_nbr, SeasInt_nbr, SeasLen_nbr, SeasAmp_nbr)


def ModTimtoInt(timecodelist):
    leap_years = [str(i) for i in range(1960, 2024, 4)]
    if str(timecodelist[0])[0:4] in leap_years or str(timecodelist[-1])[0:4] in leap_years:
        lp = 366
    else:
        lp = 365

    jdays1 = [int(str(d)[4:7]) for d in timecodelist if str(d)[3] == str(timecodelist[0])[3]]
    jdays2 = [int(str(d)[4:7])+lp for d in timecodelist if str(d)[3] != str(timecodelist[0])[3]]
    jdays  = jdays1 + jdays2
    jdays  = [i-(jdays[0]-1) for i in jdays]
    return jdays

def PixelBreaker(x):
    m = x * powerMask
    m = m / 10000

    # mask nan from m; mask also the values from the time object, which is passed on to optimize.curve_fit
    popt, pcov = optimize.curve_fit(funci,
                                    sub['AccDate'], x, p0=[0.1023, 0.8802, 108.2, 7.596, 311.4, 7.473],
                                    maxfev=100000000)
    pred = funci(dummy, popt[0], popt[1], popt[2], popt[3], popt[4], popt[5])
    dev1 = np.diff(pred)
    SoS = np.argmax(dev1) + 1
    EoS = np.argmin(dev1) + 1
    SeasMax = round(max(pred), 2)
    SeasMin = round(min(pred), 2)
    SeasInt = round(np.trapz(funci(np.arange(SoS, EoS + 1, 1),
                                   popt[0], popt[1], popt[2], popt[3], popt[4], popt[5])), 2)
    SeasLen = EoS - SoS
    SeasAmp = SeasMax - SeasMin
    return [SoS, EoS, SeasMax, SeasMin, SeasInt, SeasLen, SeasAmp]

# working station
# path = '/home/florus/'
path = 'Z:/_students_data_exchange/FP_FP/MODIS/'

# load coefficients!!!!; get .sav for coefficients and loop over 3 -sets (lowest,mean and highest RMSE)


cList =

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
maskL = getFilelist(path + 'rasterized', '.tiff')

# loop over masks (equals looping over tiles

#for mask in maskL:
    mas   = maskL[0] # for testing; will be replaced in the end through courser
    mask  = gdal.Open(mas)
    mask  = mask.GetRasterBand(1).ReadAsArray()
    mask[mask == 0] = np.nan
    # get list for individual container in respective raw-folder
    modHDF = getFilelist(path + 'raw/raw' + mas.split('.')[0][-1], '.hdf')
    # make list time-readable
    modTim = [int(hdf.split('.')[1][1:5] + hdf.split('.')[1][5:8]) for hdf in modHDF]
    # subset filelist to list of needed files
    #for indi in indexer:
        indi = indexer[0]# for testing; will be replaced in the end through courser
        print('subsetting MODIS files for periods ' + str(timeframe[indi[0]][0]) + ' to ' +
              str(timeframe[indi[0]][1]) + ' and ' + str(timeframe[indi[1]][0]) + ' to ' +
              str(timeframe[indi[1]][1]))

        # find scenes from timeframe in modHDF; first, scenes have to be ordered chronological!!
        mdict   = dict(zip(modTim, modHDF))
        modHDFs = [v for k ,v in sorted(mdict.items())]
        modTims = [k for k ,v in sorted(mdict.items())]
        # two seasons due to two points in time for samples (2007,2012 and so on)
        modOrd1  = [[modHDFs[i], modTims[i]] for i in range(len(modTims)) if
                  modTims[i] >= timeframe[indi[0]][0] and modTims[i] <= timeframe[indi[0]][1]]
        modOrd2  = [[modHDFs[i], modTims[i]] for i in range(len(modTims)) if
                  modTims[i] >= timeframe[indi[1]][0] and modTims[i] <= timeframe[indi[1]][1]]

        hdf1 = [i[0] for i in modOrd1]
        hdf2 = [i[0] for i in modOrd2]
        tim1 = [i[1] for i in modOrd1]
        tim2 = [i[1] for i in modOrd2]
        # create a doy-object which can be used for PixelBreaker for this specific sequence

        # build a numpy container for all scenes' VIs'
        nbr_cont = evi_cont = ndvi_cont = []

        #for iter, scene in enumerate(modSub):
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
            # load NDVI, EVI, calc NBR and store them int individual into tile-based lists
            ndvi  = gdal.Open(select[2])
            ndviB = ndvi.GetRasterBand(1)
            ndvi_cont.append(ndviB.ReadAsArray())

            evi   = gdal.Open(select[0])
            eviB  = evi.GetRasterBand[1]
            evi_cont.append(eviB.ReadAsArray())

            mir   = gdal.Open(select[1])
            mirB  = mir.GetRasterBand(1)
            mirA  = mirB.ReasAsArray()
            nir   = gdal.Open(select[3])
            nirB  = nir.GetRasterBand(1)
            nirA  = nirB.ReadAsArray()
            nbr_cont.append((nirA - mirA) / nirA + mirA)

            # do masking, float conversionseasonal parameter derivation via np.alonga_axis (outside of this loop)
    NDVI_arr = np.stack(ndvi_cont, axis=2)
    EVI_arr  = np.stack(evi_cont, axis=2)
    NBR_arr  = np.stack(nbr_cont, axis=2)

    VI_list = [NDVI_arr, EVI_arr, NBR_arr]
    NDVI_Seas, EVI_Seas, NBR_Seas = np.empty(mask.shape[0], mask.shape[1], int(len(cList)/3))
    SP_list = [NDVI_Seas, EVI_Seas, NBR_Seas]
    for count, VI in enumerate(VI_list):
        SP_list[count] = np.apply_along_axis(PixelBreaker, 2, VI)

