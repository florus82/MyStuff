from FloppyToolZ.MasterFuncs import *
from joblib import Parallel, delayed
import time

# set the tiling system layer
tile_path = r'Y:\FP_MB\CHACO_extent_tiles_9.shp'

# set time start and time end
t_start = 20180901
t_end = 20190831

# set the path for the polygonized S1 scenes
poly_path = r'E:\Florian\MSc_outside_Seafile\RS_Data\S1\after_preprocess\scene_polys\VV_Polygons.shp'

# paths for VV and VH folders
VVfold = r'E:\Florian\MSc_outside_Seafile\RS_Data\S1\after_preprocess\VV\2nd'
VHfold = r'E:\Florian\MSc_outside_Seafile\RS_Data\S1\after_preprocess\VH'

# set OutputFolder
outFo = r'E:\Florian\MSc_outside_Seafile\RS_Data\S1\after_preprocess\scenes_per_tile'

# get a list of valid (CHACO_YN ==1) Id_long
tiling = ogr.Open(tile_path)
tiles = tiling.GetLayer()
tiles.SetAttributeFilter('CHACO_YN = 1')
idList = [til.GetField('Id_long') for til in tiles]
tiles.ResetReading()
#
# tilefile = tile_path
# tileID = idList[0]
# time_start = t_start
# time_end = t_end
# polygonfile_path = poly_path
# outFolder = outFo

def S1_scenes_per_Tile(tilefile, tileID, time_start, time_end, polygonfile_path, outFolder):

    tiles_open = ogr.Open(tilefile)
    tiles_lyr  = tiles_open.GetLayer()
    query = '{} = {}'.format('Id_long', tileID)
    tiles_lyr.SetAttributeFilter(query)
    tili = tiles_lyr.GetNextFeature()
    geom = tili.geometry() # load geometry

    # intersect
    pol = ogr.Open(polygonfile_path)
    pol_lyr = pol.GetLayer()
    sceneCont = []
    pol_lyr.SetSpatialFilter(geom)
    for p in pol_lyr:
        sceneCont.append(p.GetField('Scene'))
        #print(p.GetField('Scene'))
    pol_lyr.SetSpatialFilter(None)
    pol_lyr.ResetReading()

    k = ['Id_long', 'Scenes']
    v = [[], []]
    res = dict(zip(k, v))

    for scene in sceneCont:
        year = int(scene.split('_')[4][0:4])*10000
        month = int(scene.split('_')[4][4:6])*100
        day = int(scene.split('_')[4][6:8])
        if (year + month + day) >= time_start and (year + month + day) <= time_end:
            # print(scene)
            res['Id_long'].append(tileID)
            res['Scenes'].append(scene)
        else:
            continue
    df = pd.DataFrame(data=res)
    df.to_csv(outFolder + '/' + str(int(tili.GetField('Id_long'))) + '.csv', sep=',', index=False)
    return ('scenes found :)')

# create the joblist
joblist = []
for id in idList:
    joblist.append([tile_path, id, t_start, t_end, poly_path, outFo])

if __name__ == '__main__':
# ####################################### SET TIME COUNT ###################################################### #
    starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print("--------------------------------------------------------")
    print("Starting process, time:" +  starttime)
    print("")


    Parallel(n_jobs=58)(delayed(S1_scenes_per_Tile)(job[0], job[1], job[2], job[3], job[4], job[5]) for job in joblist)

    print("")
    endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print("--------------------------------------------------------")
    print("--------------------------------------------------------")
    print("start: " + starttime)
    print("end: " + endtime)
    print("")

# conti = []
# files = getFilelist(VVfold, '.tif')
# for file in files:
#     year = int(file.split('/')[-1].split('_')[4][0:4]) * 10000
#     month = int(file.split('/')[-1].split('_')[4][4:6]) * 100
#     day = int(file.split('/')[-1].split('_')[4][6:8])
#     if (year + month + day) >= t_start and (year + month + day) <= t_end:
#         conti.append(file)