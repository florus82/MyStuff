import ogr, osr
import os
import pandas as pd

os.chdir("P:/Master/Python/Week 10 - Real-world problems III/Data")
parcels = ogr.Open("Parcels.shp")
parcels_lyr = parcels.GetLayer()
parcels_cs = parcels_lyr.GetSpatialRef()

# Get Projection infos
mary = ogr.Open("Marihuana_Grows.shp")
mary_lyr = mary.GetLayer()
mary_cs = mary_lyr.GetSpatialRef()

# Create output dataframe
out_df = pd.DataFrame(
    columns=["Parcel APN", "NR_GH-Plants", "NR_OD-Plants", "Dist_to_grow_m", "Km Priv. Road", "Km Local Road",
             "Mean elevation", "PublicLand_YN", "Prop_in_THP"])

feat = parcels_lyr.GetNextFeature()

while feat:
    apn = feat.GetField('APN')

    geom_par = feat.geometry().Clone()
    geom_par.Transform(osr.CoordinateTransformation(parcels_cs, mary_cs))

    mary_lyr.SetSpatialFilter(geom_par)

    total_gh = total_od = 0

    point_feat = mary_lyr.GetNextFeature()
    while point_feat:
        total_gh += point_feat.GetField('g_plants')
        total_od += point_feat.GetField('o_plants')
        point_feat = mary_lyr.GetNextFeature()
    mary_lyr.ResetReading()

    #out_df.loc[len(out_df) + 1] = [apn, total_gh, total_od...]  # insert further variables from other groups

    feat = parcels_lyr.GetNextFeature()

parcels_lyr.ResetReading()
