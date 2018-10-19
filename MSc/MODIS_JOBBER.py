from FloppyToolZ.MasterFuncs import *
import time

# set working station
path1 = '/home/florus/MSc/'
#path1 = 'Z:/_students_data_exchange/FP_FP/'
path2 = '/home/florus/Seafile/myLibrary/MSc/'
#path2 = 'Z:/_students_data_exchange/FP_FP/Seafile/myLibrary/MSc/'

# load models for lowest,median and highest RMSE) - should all be part of apply_along_axis
iter100 = pd.read_csv(path2 + 'Modelling/runs100/AllRuns.csv')
savs    = getFilelist(path2 + 'Modelling/runs100/sav', '.sav')
sav     = getMinMaxMedianSAV(iter100, savs)

# specify Tile; equals the manually set tile for the Tiler
tile = 'Mod1'
# VIs
VIS = ['NDVI', 'EVI', 'NBR']
# how many seasonal parameter per VI
no_seaspar = 7


no_tiles = 24**2

# ########################################## read in dumps

tile_timeline = joblib.load()
tile_dummy    = joblib.load()

tile_time = tile_timeline + tile_timeline + tile_timeline
tile_ dum = tile_dummy + tile_dummy + tile_dummy

cubes = getFilelist(path2 + 'Modelling/prediction/megadump', '.sav')

# ########################################## create joblist
jobs = [[joblib.load(cubes[i]), PixelBreaker_BoneStorm, tile_time, tile_dummy,
         path2 + 'Modelling/prediction/megadump/' + tile + '/' + 'SeasP' + cubes.split] for i in range(no_tiles)]
# jobs = [tile_array, pixelbreakerFunci, timelini, dummi, storpath]


if __name__ == '__main__':
# ####################################### SET TIME COUNT ###################################################### #
    starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print("--------------------------------------------------------")
    print("Starting process, time:" +  starttime)
    print("")


    Parallel(n_jobs=25)(delayed(PixelSmasher)(i[0], i[1], i[2], i[3], i[4]) for i in jobs)

    print("")
    endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print("--------------------------------------------------------")
    print("--------------------------------------------------------")
    print("start: " + starttime)
    print("end: " + endtime)
    print("")