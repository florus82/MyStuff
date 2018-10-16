from FloppyToolZ.Funci import *
from scipy import optimize
import joblib


def funci(x, p1, p2, p3, p4, p5, p6):
    return p1 +p2 * ((1 / (1 + np.exp((p3 - x) / p4))) - (1 / (1 + np.exp((p5 - x) / p6))))


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
    return [jdays, [i for i in range(1,lp, 1)]]


def getMinMaxMedianSAV(iterCSV, savfileConti):
    it_min = np.where(iterCSV['r2'] == np.min(iterCSV['r2']))[0][0]
    it_max = np.where(iterCSV['r2'] == np.max(iterCSV['r2']))[0][0]
    it_median = np.random.choice(np.asarray(np.where(round(iterCSV['r2'], 2) == round(np.median(iterCSV['r2']), 2)))[0])

    keys = [fil.split('_')[-1].split('.')[0] for fil in savfileConti]
    vals = [fil for fil in savfileConti]
    savi = dict(zip(keys, vals))

    sav_min = joblib.load(savi[str(it_min)])
    sav_max = joblib.load(savi[str(it_max)])
    sav_median = joblib.load(savi[str(it_median)])

    return [sav_min, sav_max, sav_median]

def PixelBreaker_SoS(x):
    # int to float
    m = x / 10000

    # mask nan from m; mask also the values from the time object, which is passed on to optimize.curve_fit
    popt, pcov = optimize.curve_fit(funci,
                                    timeline, m, p0=[0.1023, 0.8802, 108.2, 7.596, 311.4, 7.473],
                                    maxfev=100000000)
    pred = funci(dummy, popt[0], popt[1], popt[2], popt[3], popt[4], popt[5])
    dev1 = np.diff(pred)
    SoS = np.argmax(dev1) + 1

    return SoS


def PixelBreaker_EoS(x):
    # int to float
    m = x / 10000

    # mask nan from m; mask also the values from the time object, which is passed on to optimize.curve_fit
    popt, pcov = optimize.curve_fit(funci,
                                    timeline, m, p0=[0.1023, 0.8802, 108.2, 7.596, 311.4, 7.473],
                                    maxfev=100000000)
    pred = funci(dummy, popt[0], popt[1], popt[2], popt[3], popt[4], popt[5])
    dev1 = np.diff(pred)
    EoS = np.argmin(dev1) + 1

    return EoS


def PixelBreaker_SeasMax(x):
    # int to float
    m = x / 10000

    # mask nan from m; mask also the values from the time object, which is passed on to optimize.curve_fit
    popt, pcov = optimize.curve_fit(funci,
                                    timeline, m, p0=[0.1023, 0.8802, 108.2, 7.596, 311.4, 7.473],
                                    maxfev=100000000)
    pred = funci(dummy, popt[0], popt[1], popt[2], popt[3], popt[4], popt[5])
    SeasMax = round(max(pred), 2)

    return SeasMax


def PixelBreaker_SeasMin(x):
    # int to float
    m = x / 10000

    # mask nan from m; mask also the values from the time object, which is passed on to optimize.curve_fit
    popt, pcov = optimize.curve_fit(funci,
                                    timeline, m, p0=[0.1023, 0.8802, 108.2, 7.596, 311.4, 7.473],
                                    maxfev=100000000)
    pred = funci(dummy, popt[0], popt[1], popt[2], popt[3], popt[4], popt[5])
    SeasMin = round(min(pred), 2)

    return SeasMin


def PixelBreaker_SeasInt(x):
    # int to float
    m = x / 10000

    # mask nan from m; mask also the values from the time object, which is passed on to optimize.curve_fit
    popt, pcov = optimize.curve_fit(funci,
                                    timeline, m, p0=[0.1023, 0.8802, 108.2, 7.596, 311.4, 7.473],
                                    maxfev=100000000)
    dev1 = np.diff(pred)
    SoS = np.argmax(dev1) + 1
    EoS = np.argmin(dev1) + 1
    SeasInt = round(np.trapz(funci(np.arange(SoS, EoS + 1, 1),
                                   popt[0], popt[1], popt[2], popt[3], popt[4], popt[5])), 2)

    return SeasInt


def PixelBreaker_SeasLen(x):
    # int to float
    m = x / 10000

    # mask nan from m; mask also the values from the time object, which is passed on to optimize.curve_fit
    popt, pcov = optimize.curve_fit(funci,
                                    timeline, m, p0=[0.1023, 0.8802, 108.2, 7.596, 311.4, 7.473],
                                    maxfev=100000000)
    pred = funci(dummy, popt[0], popt[1], popt[2], popt[3], popt[4], popt[5])
    dev1 = np.diff(pred)
    SoS = np.argmax(dev1) + 1
    EoS = np.argmin(dev1) + 1
    SeasLen = EoS - SoS

    return SeasLen


def PixelBreaker_SeasAmp(x):
    # int to float
    m = x / 10000

    # mask nan from m; mask also the values from the time object, which is passed on to optimize.curve_fit
    popt, pcov = optimize.curve_fit(funci,
                                    timeline, m, p0=[0.1023, 0.8802, 108.2, 7.596, 311.4, 7.473],
                                    maxfev=100000000)
    pred = funci(dummy, popt[0], popt[1], popt[2], popt[3], popt[4], popt[5])
    SeasMax = round(max(pred), 2)
    SeasMin = round(min(pred), 2)
    SeasAmp = SeasMax - SeasMin
    return SeasAmp


PixelBreaker_Funci = [PixelBreaker_SoS, PixelBreaker_EoS, PixelBreaker_SeasMax,
                      PixelBreaker_SeasMin, PixelBreaker_SeasInt,
                      PixelBreaker_SeasLen, PixelBreaker_SeasAmp]

# ######################################################################################### start

# working station
path1 = '/home/florus/MSc/'
# path1 = 'Z:/_students_data_exchange/FP_FP/'
path2 = '/home/florus/Seafile/myLibrary/MSc/'
# path2 = 'Z:/_students_data_exchange/FP_FP/Seafile/myLibrary/'

no_seaspar = 7

# load models for lowest,median and highest RMSE)
iter100 = pd.read_csv(path2 + 'Modelling/runs100/AllRuns.csv')
savs    = getFilelist(path2 + 'Modelling/runs100/sav', '.sav')
sav     = getMinMaxMedianSAV(iter100, savs)


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
syears = [2013, 2014, 2015] # 3 pairs as some plots only in 2010-2012
sequen = [[15, m, sy, 14, m, sy+1] for m in months for sy in syears]

timeframe = [time_seq(seq[0], seq[1], seq[2], seq[3], seq[4], seq[5]) for seq in sequen]


# ######################predictions are MODIS-tile based
# get a list for all masks
maskL = getFilelist(path1 + 'RS_Data/MODIS/rasterized', '.tiff')

# loop over masks (equals looping over tiles

#for mask in maskL:
mas   = maskL[0] # for testing; will be replaced in the end through courser
mask  = gdal.Open(mas)
mask  = mask.GetRasterBand(1).ReadAsArray()
mask[mask == 0] = np.nan
# get list for individual container in respective raw-folder
modHDF = getFilelist(path1 + 'RS_Data/MODIS/raw/raw' + mas.split('.')[0][-1], '.hdf')
# make list time-readable
modTim = [int(hdf.split('.')[1][1:5] + hdf.split('.')[1][5:8]) for hdf in modHDF]

# iterate over growings season combination --> median needs to be taken from this result
#for time in timeframe:
time = timeframe[0]# for testing; will be replaced in the end through courser
print('subsetting MODIS files for periods ' + str(time[0]) + ' to ' +
      str(time[1]))

# find scenes from timeframe in modHDF; first, scenes have to be ordered chronological!!
mdict   = dict(zip(modTim, modHDF))
modHDFs = [v for k ,v in sorted(mdict.items())]
modTims = [k for k ,v in sorted(mdict.items())]
modOrd = [[modHDFs[i], modTims[i]] for i in range(len(modTims)) if
          modTims[i] >= time[0] and modTims[i] <= time[1]]

hdf = [i[0] for i in modOrd]
tim = [i[1] for i in modOrd]

# create a doy-object which can be used for PixelBreaker for this specific sequence
timline, dummy = ModTimtoInt(tim)
# build numpy container for all scenes' VIs' per growing season
ndvi_cont = []
evi_cont  = []
nbr_cont  = []
# iterate over each scene of the growing season combination
for iter, scene in enumerate(hdf):
    # scene = hdf[0]# for testing; will be replaced in the end through courser
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
    ndvi_cont.append(ndviB.ReadAsArray() * powerMask)

    evi   = gdal.Open(select[0])
    eviB  = evi.GetRasterBand(1)
    evi_cont.append(eviB.ReadAsArray() * powerMask)

    mir   = gdal.Open(select[1])
    mirB  = mir.GetRasterBand(1)
    mirA  = mirB.ReadAsArray() * powerMask
    nir   = gdal.Open(select[3])
    nirB  = nir.GetRasterBand(1)
    nirA  = nirB.ReadAsArray() * powerMask
    nbr_cont.append((nirA - mirA) / (nirA + mirA))

    # do masking, float conversionseasonal parameter derivation via np.alonga_axis (outside of this loop)
NDVI_arr = np.stack(ndvi_cont, axis=2)
EVI_arr  = np.stack(evi_cont, axis=2)
NBR_arr  = np.stack(nbr_cont, axis=2)

del ndvi_cont, evi_cont, nbr_cont

VI_list = [NDVI_arr, EVI_arr, NBR_arr]

del NDVI_arr, EVI_arr, NBR_arr

NDVI_Seas = np.empty((mask.shape[0], mask.shape[1], no_seaspar))
EVI_Seas  = np.empty((mask.shape[0], mask.shape[1], no_seaspar))
NBR_Seas  = np.empty((mask.shape[0], mask.shape[1], no_seaspar))

VI_SP     = [NDVI_Seas, EVI_Seas, NBR_Seas]
del NDVI_Seas, EVI_Seas, NBR_Seas
VIname    = ['NDVI', 'EVI', 'NBR']
for iter1, VI in enumerate(VI_list):
    for iter2 in range(no_seaspar):
        VI_SP[iter1][:,:,iter2] = np.apply_along_axis(PixelBreaker_Funci[iter2], 2, VI)

    joblib.dump(VI_SP[iter1], path2 + 'MSc/Modelling/prediction/megadump/SeasPar_' +
                VIname[iter1] + '_' + str(time[0]) +  '_' + str(time[1]) + '.sav')
del VI_SP