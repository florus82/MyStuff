from FloppyToolZ.MasterFuncs import *
#from  __future__ import print_function
import matplotlib.pyplot as plt

from mpl_toolkits.mplot3d import Axes3D

from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.ensemble.partial_dependence import plot_partial_dependence
from sklearn.ensemble.partial_dependence import partial_dependence

dat = pd.read_csv('/home/florus/Seafile/myLibrary/MSc/Modelling/GAP_FILLED/Single_VIs/data_junks_from_R/not_smooth/subsets/NDVI_GrowSeas_and_SeasPos_Mediannot_smooth.csv')

# dat = pd.read_csv('/home/florus/Seafile/myLibrary/MSc/Modelling/GAP_FILLED/Single_VIs/data_junks_from_R/smooth/subsets/NDVI_GrowSeas_and_SeasPos_Mediansmooth.csv')

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

mo1 = ['run_22', 'run_20', 'run_78']
#mo2 = ['run_28', 'run_67', 'run_5']
mo = mo1 #+ mo2
pa1 = '/home/florus/Seafile/myLibrary/MSc/Modelling/GAP_FILLED/Single_VIs/Modelling/runs_check100_final/sav_continue/'
pa = [pa1,pa1,pa1]

mo_names = ['min', 'max', 'median', 'initial']
paths = [j + mo[i] + '.sav' for i, j in enumerate(pa)] + ['/home/florus/Seafile/myLibrary/MSc/Modelling/GAP_FILLED/Single_VIs/Modelling/runs_final_check/NDVI_GrowSeas_and_SeasPos_Mediannot_smoothSeasPar_NDVI.sav']

keys = ['Mod', 'y', 'x', 'Para']
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
            res['y'].append(tt[0][0][k])
            res['x'].append(tt[1][0][k])
            res['Para'].append(par_sets[j])

df  = pd.DataFrame(data = res)
df.to_csv('/home/florus/Seafile/myLibrary/MSc/PLOTS_FINAL/extracts/part_depend3.csv', sep=',',index=False)
#
# features = [0,1,2,3,4,5,6]
# fig, axs = plot_partial_dependence(modi.best_estimator_, block, features,
#                                    feature_names=par_sets,
#                                    n_jobs=10, grid_resolution=100)




