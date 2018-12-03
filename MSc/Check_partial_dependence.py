from FloppyToolZ.MasterFuncs import *
#from  __future__ import print_function
import matplotlib.pyplot as plt

from mpl_toolkits.mplot3d import Axes3D

from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.ensemble.partial_dependence import plot_partial_dependence
from sklearn.ensemble.partial_dependence import partial_dependence

dat = pd.read_csv('/home/florus/Seafile/myLibrary/MSc/Modelling/GAP_FILLED/SINGLE_VIs/data_junks_from_R/not_smooth/subsets/NDVI_GrowSeas_and_SeasPos_Mediannot_smooth.csv')

p2 = '/home/florus//Seafile/myLibrary/MSc/Modelling/All_VIs/'
c_fil  = getFilelist(p2 + 'colnames', '.csv')
c_fil.sort()
c_seasPar  = pd.read_csv(c_fil[1])
c_seasPar_NDVI = c_seasPar[0:9]
c_seasPar_NDVI  = c_seasPar_NDVI[c_seasPar_NDVI.columns.values[0]].values.tolist()
killNDVI = ['NDVI_GreenUp', 'NDVI_Maturity']

for ki in killNDVI:
    c_seasPar_NDVI.remove(ki)

par_sets  = c_seasPar_NDVI
block = dat[par_sets].dropna()

mo1 = ['run_35', 'run_1', 'run_86']
mo2 = ['run_28', 'run_67', 'run_5']
mo = mo1 + mo2
pa1 = '/home/florus/Seafile/myLibrary/MSc/Modelling/Single_VIs/Modelling/runs100/sav/'
pa2 = '/home/florus/Seafile/myLibrary/MSc/Modelling/Single_VIs/Modelling/runs100/sav_continue/'
pa = [pa1,pa1,pa1,pa2,pa2,pa2]

mo_names = ['min', 'max', 'median', 'min', 'max', 'median', 'orig']
mo_cat   = ['bad', 'bad', 'bad', 'continue', 'continue', 'continue', 'orig']
paths = [j + mo[i] + '.sav' for i, j in enumerate(pa)] + ['/home/florus/Seafile/myLibrary/MSc/Modelling/GAP_FILLED/SINGLE_VIs/Modelling/runs/NDVI_GrowSeas_and_SeasPos_Mediannot_smoothSeasPar_NDVI.sav']

keys = ['Mod', 'Cat', 'y', 'x', 'Para']
vals = [list() for _ in range(len(keys))]
res  = dict(zip(keys, vals))

kwargs = dict(X=block, percentiles=(0, 1), grid_resolution=100)

for z, p in enumerate(paths):
    modi = joblib.load(p)
    for j in range(7):
        tt = partial_dependence(modi.best_estimator_, [j], **kwargs)
        print(tt[0][0].shape)
        for k in range(tt[0][0].shape[0]):
            res['Mod'].append(mo_names[z])
            res['Cat'].append(mo_cat[z])
            res['y'].append(tt[0][0][k])
            res['x'].append(tt[1][0][k])
            res['Para'].append(par_sets[j])

df  = pd.DataFrame(data = res)
df.to_csv('/home/florus/Seafile/myLibrary/MSc/Modelling/Single_VIs/Modelling/runs100/part_depend_gf_dat.csv', sep=',',index=False)

#
# features = [0,1,2,3,4,5,6]
# fig, axs = plot_partial_dependence(modi.best_estimator_, block, features,
#                                    feature_names=par_sets,
#                                    n_jobs=10, grid_resolution=100)




