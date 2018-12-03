from FloppyToolZ.MasterFuncs import *

a = getFilelist('/home/florus/Seafile/myLibrary/MSc/Modelling/Single_VIs/prediction/CS/post_process/norm', '.tif')
killer = []
for i in a:
    if 'fac3' in i:
        killer.append(i)
for kill in killer:
    a.remove(kill)


conti = []
for img in a:
    b = gdal.Open(img)
    c = b.GetRasterBand(1).ReadAsArray()
    c[c < 0] = np.nan
    conti.append(pd.DataFrame(c.flatten()))


aa = pd.concat([conti[0], conti[1]],axis=1, sort=False)
print(aa.corr())