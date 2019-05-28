from FloppyToolZ.MasterFuncs import *

# load points
points = 'Y:/_students_data_exchange/FP_FP/Seafile/myLibrary/MSc/2nd_round/plot_coords/Combined_cont_gasp1_centerCoord_MODIS.shp'
point  = ogr.Open(points, 0)
poin   = point.GetLayer()
# extract attribute table
poi    = getAttributesALL(poin)
# add xy to table
k = ['X', 'Y', 'dups']
v = [[], [], []]
d = dict(zip(k, v))

for feat in poin:
    d['X'].append(feat.geometry().GetX())
    d['Y'].append(feat.geometry().GetY())
    d['dups'].append('N')
poin.ResetReading()
pod  = {**poi, **d}

pod  = dictOrder(pod, 'X', 'Y')

# populate duplicates column

for i in range(len(pod['X'])-1):
    if(pod['X'][i] == pod['X'][i+1]):
        if(pod['Y'][i] == pod['Y'][i+1]):
            pod['dups'][i+1] = pod['UniqueID'][i]

# clean up dups column

for i in range(1,len(pod['X'])):
    if(pod['dups'][i] is not 'N'):
        if(pod['dups'][i-1] is not 'N'):
            pod['dups'][i] = pod['dups'][i-1]


df = pd.DataFrame(data=pod)
df.to_csv('Y:/_students_data_exchange/FP_FP/Seafile/myLibrary/MSc/2nd_round/plot_coords/test3.csv', sep=',',index=False)