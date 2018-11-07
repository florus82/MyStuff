from FloppyToolZ.Funci import *
import time
import pandas as pd
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.externals import joblib
from sklearn import preprocessing
from sklearn import metrics

# #### funcitons needed
# grid search
def Model(yValues, predictors, CVout, nCores):
    param_grid = {'learning_rate': [0.1, 0.05, 0.02, 0.01, 0.005, 0.002, 0.001],
                  'max_depth': [4, 6],
                  'min_samples_leaf': [3, 5, 9, 17],
                  'max_features': [1.0, 0.5, 0.3, 0.1]}
    est = GradientBoostingRegressor(n_estimators=7500)
    gs_cv = GridSearchCV(est, param_grid, cv=5, refit=True, n_jobs=nCores).fit(predictors, yValues)
    # Write outputs to disk and return elements from function
    joblib.dump(gs_cv, CVout)
    return (gs_cv)

# model performance
def ModPerfor(cv_results, yData, xData):
    # Calculate Predictions of the true values
    y_true, y_pred = yData, cv_results.predict(xData)

    res['r2'].append(metrics.r2_score(y_true, y_pred))
    res['mse'].append(metrics.mean_squared_error(y_true, y_pred))
    res['rmse'].append((metrics.mean_squared_error(y_true, y_pred))**0.5)
    res['y_true'].append(list(y_true))
    res['y_pred'].append(list(y_pred))

    # Get parameters from the best estimator
    res['max_depth'].append(cv_results.best_params_['max_depth'])
    res['learning_rate'].append(cv_results.best_params_['learning_rate'])
    res['min_samples_leaf'].append(cv_results.best_params_['min_samples_leaf'])
    res['max_features'].append(cv_results.best_params_['max_features'])
    #return res




# #### create master file list for pred/resp sets
# p1 = '/home/florus/'
p1 = 'Y:/_students_data_exchange/FP_FP/Seafile/myLibrary/MSc/Modelling/GAP_FILLED/ALL_VIs/data_junks_from_R/' # Geoserv2

path_ns  = p1 + 'not_smooth/subsets'
path_sm  = p1 + 'smooth/subsets'
path_sm5 = p1 + 'smooth5/subsets'

paths = [path_ns, path_sm, path_sm5]

fil   = [getFilelist(path, '.csv') for path in paths]
filp  = [f for fi in fil for f in fi]

# #### read in column names for different pred-sets (seasPAr, seasFit, seasStat)
c_fil  = getFilelist('Y:/_students_data_exchange/FP_FP/Seafile/myLibrary/MSc\Modelling/All_VIs/colnames', '.csv')
c_fil.sort()
c_seasPar  = pd.read_csv(c_fil[1])
c_seasFit  = pd.read_csv(c_fil[0])
c_seasStat = pd.read_csv(c_fil[2])

c_seasPar  = c_seasPar[c_seasPar.columns.values[0]].values.tolist()
c_seasFit  = c_seasFit[c_seasFit.columns.values[0]].values.tolist()
c_seasStat = c_seasStat[c_seasStat.columns.values[0]].values.tolist()
c_seasParStat = c_seasPar + c_seasStat

c_seasPar.append('Mean_AGB')
c_seasFit.append('Mean_AGB')
c_seasStat.append('Mean_AGB')
c_seasParStat.append('Mean_AGB')

# exlcude GreenUP & Maturity due to too many NaNs
# kill = ['NDVI_GreenUp', 'EVI_GreenUp','NBR_GreenUp',
#         'NDVI_Maturity', 'EVI_Maturity', 'NBR_Maturity']
#
# for ki in kill:
#     c_seasPar.remove(ki)
#     c_seasParStat.remove(ki)
# #### read in the data-blocks and seperate into train & test

# build result container
keys = ['ParVers', 'ParSet', 'r2', 'mse', 'rmse', 'y_true', 'y_pred', 'max_depth', 'learning_rate', 'min_samples_leaf', 'max_features']
vals = [list() for i in range(len(keys))]
res  = dict(zip(keys, vals))

# par_sets  = [c_seasPar, c_seasFit, c_seasStat, c_seasParStat]
# par_names = ['SeasPar', 'SeasFIT', 'SeasStats', 'SeasParStats']
par_sets  = [c_seasPar, c_seasStat, c_seasParStat]
par_names = ['SeasPar', 'SeasStats', 'SeasParStats']

# dummy model for save parallel
def ModelRun():
    # iterate over different parameter versions
    for n, pV in enumerate(filp):
        dat = pd.read_csv(pV)
        # iterate over different parameter-sets
        for i, par in enumerate(par_sets):
            # subset data per predictor set
            block = dat[par].dropna()
            # split into train & test
            x_Train, x_Test, y_Train, y_Test = train_test_split(block.iloc[:, np.where((block.columns.values=='Mean_AGB') == False)[0]],
                             block['Mean_AGB'], random_state= 42, test_size = 0.3)

            # scale training and test predictors
            # scaler = preprocessing.StandardScaler().fit(x_Train)
            # x_Train = scaler.transform(x_Train)
            # x_Test  = scaler.transform(x_Test)
            # insert Modelversion into results-container
            res['ParVers'].append(pV.split('/')[-1].split('.')[0])
            res['ParSet'].append(par_names[i])

            stor = 'Y:/_students_data_exchange/FP_FP/Seafile/myLibrary/MSc/Modelling/GAP_FILLED/ALL_VIs/runs_greenMat/' + pV.split('/')[-1].split('.')[0] + par_names[i] + '.sav'
            ModPerfor(Model(y_Train, x_Train, stor, 40),
                      y_Test, x_Test)

            print(n)



        # ##### run gbr once
if __name__ == '__main__':
    starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print("--------------------------------------------------------")
    print("Starting process, time: " + starttime)
    print("")
    # run model and store performances in results-container
    ModelRun()

    print("")
    endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print("--------------------------------------------------------")
    print("--------------------------------------------------------")
    print("start: " + starttime)
    print("end: " + endtime)
    print("")

df = pd.DataFrame(data = res)
df.to_csv('Y:/_students_data_exchange/FP_FP/Seafile/myLibrary/MSc/Modelling/GAP_FILLED/ALL_VIs/runs_greenMat/AllRuns.csv', sep=',', index=False)