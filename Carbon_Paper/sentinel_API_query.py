from FloppyToolZ.Funci import *
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from datetime import date

api = SentinelAPI('flopoetz', 'SDghkl234ksdvS24', 'https://scihub.copernicus.eu/dhus')

footprint = geojson_to_wkt(read_geojson('E:/Florian/MSc_outside_Seafile/RS_Data/S1/Single_downloads/Chaco_rest/Chaco_simple.geojson'))

products = api.query(footprint,
                     beginposition = ('2018-09-01T00:00:00.000Z', '2019-08-31T23:59:59.999Z'),
                     endposition = ('2018-09-01T00:00:00.000Z', '2019-08-31T23:59:59.999Z'),
                     platformname='Sentinel-1',
                     producttype= 'GRD',
                     polarisationmode= 'VV VH',
                     sensoroperationalmode= 'IW')

#products_df = api.to_dataframe(products)
# products_df.to_csv('E:/Florian/MSc_outside_Seafile/RS_Data/S1/temp/S1_query.csv', sep=',',index=False)
products_df = pd.read_csv('E:/Florian/MSc_outside_Seafile/RS_Data/S1/temp/S1_query.csv')
q_scenes = products_df['title'].tolist()
raw_scenes = getFilelist(r'E:\Florian\MSc_outside_Seafile\RS_Data\S1\after_preprocess\VV', '.tif')
raw_scenes = [raw.split('/')[-1].split('.')[0] for raw in raw_scenes]

diff_scenes = list(set(q_scenes) - set(raw_scenes))

raws = getFilelist(r'E:\Florian\MSc_outside_Seafile\RS_Data\S1\Raw', '.zip')
raw2 = [raw.split('/')[-1].split('.')[0] for raw in raws]

diff_scenes = list(set(diff_scenes) - set(raw2))

# t_start = 20180901
# t_end = 20190831
# conti = []
# for scene in raw_scenes:
#     year = int(scene.split('_')[4][0:4]) * 10000
#     month = int(scene.split('_')[4][4:6]) * 100
#     day = int(scene.split('_')[4][6:8])
#     if (year + month + day) >= t_start and (year + month + day) <= t_end:
#         conti.append(scene)

sub_products = products_df[products_df.title.isin(diff_scenes)]
down_dir = 'E:/Florian/MSc_outside_Seafile/RS_Data/S1/Raw'

for uuid in sub_products.uuid.reset_index(drop=True).tolist():
    api.download(uuid, directory_path=down_dir)
