import sys
from osgeo import ogr
import time
import pandas

# #### SET TIME-COUNT #### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " + starttime)
print("")

#path = '/home/florian/Geodata_with_Python/session5/Assignment04_data/gadm36_dissolve.shp'
#path = '/home/florian/Geodata_with_Python/session5/Assignment04_data/gadm36_shp/gadm36.shp'
path = '/home/florian/Geodata_with_Python/session5/Assignment04_data/WDPA_May2018-shapefile-polygons.shp'
country = ogr.Open(path, 0)

if country is None:
    sys.exit('Could not open {0}.'.format(country))

lyr = country.GetLayer()

header = dict.fromkeys(['Name','Type'])

head = [[lyr.GetLayerDefn().GetFieldDefn(n).GetName(), ogr.GetFieldTypeName(lyr.GetLayerDefn().GetFieldDefn(n).GetType())]
            for n in range(lyr.GetLayerDefn().GetFieldCount())]

header['Name'], header['Type'] = zip(*head)

attrib = dict.fromkeys(header['Name'])
for i, j in enumerate(header['Name']):
     attrib[j] = [lyr.GetFeature(k).GetField(j) for k in range(lyr.GetFeatureCount())]

for k, v in attrib.items():
    attrib[k] = set(attrib[k])
    attrib[k] = list(attrib[k])

w = len(max(attrib.items())[1])

for i, j in attrib.items():
    if len(attrib[i]) == w:
        print("supi")
    else:
        for k in range(w - len(attrib[i])):
            attrib[i].extend('-')
df = pandas.DataFrame(data=attrib)
df.to_csv('/home/florian/Geodata_with_Python/session5/Power.csv', sep=',',index=False)


del country

# #### END TIME-COUNT AND PRINT TIME STATS #### #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")
#