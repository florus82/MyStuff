from FloppyToolZ.MasterFuncs import *

# load plots and make to MODIS centers
point_path = 'H:/Seafile/Uni_Life/CarbonPaper/GIS_Data/Plots/merge/posicion_parcelas_plus_only_new_ones_84.shp'
refimg     = 'Y:/_students_data_exchange/FP_FP/RS_Data/MODIS/rasterized/Mod1.tiff'
points_to_Center(point_path, refimg)

# load points
points = 'H:/Seafile/Uni_Life/CarbonPaper/2nd_round/plot_coords/posicion_parcelas_plus_only_new_ones_84_centerCoord_MODIS.shp'
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
df.to_csv('H:/Seafile/Uni_Life/CarbonPaper/2nd_round/plot_coords/posicion_parcelas_plus_only_new_ones_84_centerCoord_MODIS_dups.csv', sep=',',index=False)

# create an ordered shapefile

driv = ogr.GetDriverByName('ESRI Shapefile')  # will select the driver foir our shp-file creation.
shapeStor = driv.CreateDataSource('/'.join(points.split('/')[:-1]))
# get first layer (assuming ESRI is standard) & and create empty output layer with
out_lyr = shapeStor.CreateLayer(points.split('/')[-1].split('.')[0] + '_ordered_XY',
                                getSpatRefVec(points), poin.GetGeomType())

# create attribute field
out_lyr.CreateFields(poin.schema)
dups_fld = ogr.FieldDefn('Dups', ogr.OFTString)
dups_fld.SetWidth(8)
out_lyr.CreateField(dups_fld)

# with attributes characteristics
out_feat = ogr.Feature(out_lyr.GetLayerDefn())

for in_feat in poin:

    out_feat.SetGeometry(in_feat.geometry())
    # copy existing attributes
    for i in range(in_feat.GetFieldCount()):
        out_feat.SetField(i, in_feat.GetField(i))
    # input for new attribute
    out_feat.SetField(in_feat.GetFieldCount(), pod['dups'][pod.get('UniqueID').index(in_feat.GetField('UniqueID'))])
    #create feature
    out_lyr.CreateFeature(out_feat)
poin.ResetReading()
shapeStor.Destroy()
del poin

# then apply make_gee_point_file.py !!!!!