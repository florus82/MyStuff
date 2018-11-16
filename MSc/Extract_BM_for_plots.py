from FloppyToolZ.MasterFuncs import *

# get prediction biomass maps
BM_rasL = getFilelist('Y:/_students_data_exchange/FP_FP/Seafile/myLibrary/MSc/Modelling/Single_VIs/prediction/Mosaic', '.tif')[0:3]
# get biomass maps for comparison
extraL  = getFilelist('Y:/_students_data_exchange/FP_FP/Seafile/myLibrary/MSc/other_maps_biomass_matthias/resample', '.tif').remove('Y:/_students_data_exchange/FP_FP/Seafile/myLibrary/MSc/other_maps_biomass_matthias/resample/baumann-etal_2017_LandCover-Map-CHACO_GlobalChangeBiology_reclassified.tif')

keys = ['BM_MAP'] + extraL + ['category']
vals = [list() for _ in range(len(keys))]
res  = dict(zip(keys, vals))

for extractor in BM_rasL:
    res['BM_MAP'].append(extractor)
    aa = gdal.Open(extractor)
    bb = aa.GetRasterBand(1)
    cc = bb.ReadAsArray()
    bb_NA = bb.GetNoDataValue()

    # define stratas from which samples to be drawn
    start_seq = [i for i in range(0,int(np.max(cc)),20)]
    end_seq   = [i+20 for i in start_seq]

    for i in range(len(start_seq)):
        rows, cols = np.where(np.logical_and(cc != bb_NA, cc >= start_seq[i], cc < end_seq[i]))
        indi = np.random.choice(len(rows),250,False)
        rows, cols = rows[indi], cols[indi]