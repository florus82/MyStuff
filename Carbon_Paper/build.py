from FloppyToolZ.Funci import *

# get individiual tif files
VV = getFilelist(r'E:\Florian\MSc_outside_Seafile\RS_Data\S1\after_preprocess\Metrics\VV\2nd', '.tif')
# VV_S1B = [V for V in VV if V.split('/')[-1][0] is 'S']

# VH = getFilelist(r'E:\Florian\MSc_outside_Seafile\RS_Data\S1\after_preprocess\Metrics\VH', '.tif')

poli = ['VV']#, 'VH']
for i, pol in enumerate([VV]):
    img_path = 'E:/Florian/MSc_outside_Seafile/RS_Data/S1/after_preprocess/Metrics' + '/S1_' + poli[i] +'_Chaco_2018_2019_Sep_2nd.tif'
    my_vrt = gdal.BuildVRT(img_path, pol)
    my_vrt = None

    # build pyramids
    Image = gdal.Open(img_path, 0) # 0 = read-only, 1 = read-write.
    gdal.SetConfigOption('COMPRESS_OVERVIEW', 'DEFLATE')
    Image.BuildOverviews("NEAREST", [2,4,8,16,32,64])
    del Image


# bigtiff crap
# md = gdal.GetDriverByName('GTiff').GetMetadata()
# md['DMD_CREATIONOPTIONLIST'].find('BigTIFF')