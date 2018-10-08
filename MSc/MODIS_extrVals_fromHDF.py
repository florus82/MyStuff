from FloppyToolZ.Funci import *
import time
from joblib import Parallel, delayed


# TIME START
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " + starttime)
print("")

# ##################  load any MODIS tile from study area to get projection info
modfolder = '/home/florus/MSc/RS_Data/MODIS/raw2'
modHDF    = getFilelist(modfolder, '.hdf')
modi  = gdal.Open(modHDF[0])
modis = gdal.Open(list(modi.GetMetadata('SUBDATASETS').values())[0])
modis_spatRef = getSpatRefRas(modis)

# ##################  reproject plot coordinates to MODIS
# reprojShapeSpatRefVec('/home/florus/MSc/GIS_Data/Plots/gasparri/parcelas_uniqID.shp', modis_spatRef)
# reprojShapeSpatRefVec('/home/florus/MSc/GIS_Data/Plots/conti/Conti-etal_BiomassData_withInfo_modID_and_BM_uniqID.shp', modis_spatRef)

# import shapefiles with plot coordinates
parc_XY    = getXYfromShape('/home/florus/MSc/GIS_Data/Plots/conti/Conti-etal_BiomassData_withInfo_modID_and_BM_uniqID_reproj_unnamed.shp')
parc_Attri = getAttributesALL('/home/florus/MSc/GIS_Data/Plots/conti/Conti-etal_BiomassData_withInfo_modID_and_BM_uniqID_reproj_unnamed.shp')

# ##################  transform the coordinates into cell dimensions (all tiles are equal, therefore once is enough)
k = ['col', 'row']
v = [[], []]
cells = dict(zip(k, v))
for i in range(len(parc_XY['X'])):
    cells['col'].append(getRasCellFromXY(parc_XY['X'][i], parc_XY['Y'][i], modis)[0])
    cells['row'].append(getRasCellFromXY(parc_XY['X'][i], parc_XY['Y'][i], modis)[1])

# ################## now comes the master loop --> through all hdf container
# specify which bands are needed and their NA values
bands  = ['NDVI', 'EVI', 'NIR reflectance', 'MIR reflectance', 'pixel reliability', 'VI Quality']
NaList = [-3000, -1000, -3000, -1000, 65535, 255]
VI_oki = [2112, 4160, 6208]

# build result dictionary
k = ['Point', 'NDVI', 'EVI', 'NBR', 'AccDate','CellX', 'CellY','VI_quality']
v = [[], [], [], [], [], [], [], []]
res = dict(zip(k, v))


def MODext(modHDF, bands, cells, res):

    info = gdal.Open(modHDF)
    sdsdict = info.GetMetadata('SUBDATASETS')
    sdslist = [sdsdict[k] for k in sdsdict.keys() if '_NAME' in k]
    select  = [img for img in sdslist for sub in bands if img.endswith(sub)]
    select.sort()

    q2     = gdal.Open(select[4])
    q2band = q2.GetRasterBand(1)
    # ##################  then, loop through the cells
    # ##################  first, check if values at quality layers are okay (if condition)
    # ##################  if not, set NA, otherwise, fill up res dictionary with values

    for i in range(len(cells['col'])):
        hex  = q2band.ReadRaster(cells['col'][i], cells['row'][i], 1, 1)
        qual = struct.unpack(getHexType(q2), hex)[0]
        res['CellX'].append(cells['col'][i])
        res['CellY'].append(cells['row'][i])
        d = dt.datetime(int(select[4].split('.')[1][1:5]), 1, 1) + dt.timedelta(int(select[4].split('.')[1][5:8]) - 1)
        res['AccDate'].append(d.strftime('%Y-%m-%d'))
        res['Point'].append(parc_Attri['UniqueID'][i])
        res['VI_quality'].append(struct.unpack(getHexType(q2), hex)[0])

        if qual in VI_oki:
            #NDVI band
            ndvi     = gdal.Open(select[2])
            ndviband = ndvi.GetRasterBand(1)
            hex      = ndviband.ReadRaster(cells['col'][i], cells['row'][i], 1, 1)
            res['NDVI'].append(struct.unpack(getHexType(ndvi), hex)[0])
            #EVI band
            evi     = gdal.Open(select[0])
            eviband = evi.GetRasterBand(1)
            hex     = eviband.ReadRaster(cells['col'][i], cells['row'][i], 1, 1)
            res['EVI'].append(struct.unpack(getHexType(evi), hex)[0])
            #MIR band
            mir     = gdal.Open(select[1])
            mirband = mir.GetRasterBand(1)
            hex     = mirband.ReadRaster(cells['col'][i], cells['row'][i], 1, 1)
            mirV    = struct.unpack(getHexType(mir), hex)[0]

            #NIR band
            nir     = gdal.Open(select[3])
            nirband = nir.GetRasterBand(1)
            hex     = nirband.ReadRaster(cells['col'][i], cells['row'][i], 1, 1)
            nirV    = struct.unpack(getHexType(nir), hex)[0]

            res['NBR'].append(((nirV - mirV) / (nirV + mirV))  * 10000)
        else:
            res['NDVI'].append('NA')
            res['EVI'].append('NA')
            res['NBR'].append('NA')
        print(i)

    df    = pd.DataFrame(data = res)
    df.to_csv('/home/florus/MSc/ContiExtr/ContiBM' + '_'.join(modHDF.split('.')[1:5]) + '.csv', sep=',',index=False)


# ################### parallel

joblist = [[scene, bands, cells, res] for scene in modHDF]
Parallel(n_jobs=3)(delayed(MODext)(i[0], i[1], i[2], i[3]) for i in joblist)



# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")