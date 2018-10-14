from FloppyToolZ.Funci import *

bands  = ['NDVI', 'EVI', 'NIR reflectance', 'MIR reflectance', 'pixel reliability', 'VI Quality']
NaList = [-3000, -1000, -3000, -1000, 65535, 255]
VI_oki = [2112, 4160, 6208]

mask1  = gdal.Open('/home/florus/MSc/RS_Data/MODIS/rasterized/Mod1.tiff')
mask1  = mask1.GetRasterBand(1).ReadAsArray()
mask1[mask1 == 0] = np.nan

mask1  = gdal.Open('/home/florus/MSc/RS_Data/MODIS/rasterized/Mod2.tiff')
mask2  = mask2.GetRasterBand(1).ReadAsArray()
mask2[mask2 == 0] = np.nan

modfolder1 = '/home/florus/MSc/RS_Data/MODIS/raw'
modfolder2 = '/home/florus/MSc/RS_Data/MODIS/raw2'

modHDF    = getFilelist(modfolder2, '.hdf')
# subset filelist to list of needed files
modi = modHDF[0]

info = gdal.Open(modi)
sdsdict = info.GetMetadata('SUBDATASETS')
sdslist = [sdsdict[k] for k in sdsdict.keys() if '_NAME' in k]
select = [img for img in sdslist for sub in bands if img.endswith(sub)]
select.sort()

q2 = gdal.Open(select[4])
q2band = q2.GetRasterBand(1)
q2_arr = q2band.ReadAsArray()