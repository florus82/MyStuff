from FloppyToolZ.Funci import *
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.externals import joblib
import time
from sklearn import metrics


def funci(x, p1, p2, p3, p4, p5, p6):
    return p1 +p2 * ((1 / (1 + np.exp((p3 - x) / p4))) - (1 / (1 + np.exp((p5 - x) / p6))))

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


# path1 = '/home/florus/Seafile/myLibrary/'
path1 = 'Y:/_students_data_exchange/FP_FP/Seafile/myLibrary/' # Geoserv2

dat   = pd.read_csv(path1 + 'MSc/Modelling/GAP_FILLED/Single_VIs/Modelling/iteration_base/initial_run_final_check.csv')
dummy = np.array([i for i in range(1, 366, 1)])

# make results container
keys = ['Iteration','r2', 'mse', 'rmse', 'y_true', 'y_pred',
        'max_depth', 'learning_rate', 'min_samples_leaf', 'max_features']
vals = [list() for i in range(len(keys))]
res  = dict(zip(keys, vals))

def ModelRunner():
    for counti in range(100):
        res['Iteration'].append(str(counti + 1))
        # make a seasparm container
        keys = ['GrowSeas', 'GrowFit', 'Cell', 'Index', 'SoS', 'EoS', 'SeasMax', 'SeasMin', 'SeasInt', 'SeasLen', 'SeasAmp', 'BM', 'p1', 'p2', 'p3', 'p4', 'p5', 'p6']
        vals = [list() for i in range(len(keys))]
        pars = dict(zip(keys, vals))

        for index, row in dat.iterrows():

            p1 = np.random.random_sample() * (row['p1u'] - row['p1l']) + row['p1l']
            p2 = np.random.random_sample() * (row['p2u'] - row['p2l']) + row['p2l']
            p3 = np.random.random_sample() * (row['p3u'] - row['p3l']) + row['p3l']
            p4 = np.random.random_sample() * (row['p4u'] - row['p4l']) + row['p4l']
            p5 = np.random.random_sample() * (row['p5u'] - row['p5l']) + row['p5l']
            p6 = np.random.random_sample() * (row['p6u'] - row['p6l']) + row['p6l']

            pred = funci(dummy, p1, p2, p3, p4, p5, p6)

            dev1 = np.diff(pred)
            SoS = np.argmax(dev1) + 1
            EoS = np.argmin(dev1) + 1
            SeasMax = round(max(pred), 2)
            SeasMin = round(min(pred), 2)
            #print(index)
            if SeasMax <=0.25 or SeasMax > 0.99 or SeasMin <= 0.25 or SeasMin > 0.8:
                continue
            SeasInt = round(np.trapz(funci(np.arange(SoS, EoS + 1, 1),
                                        p1, p2, p3, p4, p5, p6)), 2)
            SeasLen = EoS - SoS
            SeasAmp = SeasMax - SeasMin

            if SeasLen < 20 or EoS < 200 or SeasInt<50:
                continue

            pars['SoS'].append(SoS)
            pars['EoS'].append(EoS)
            pars['SeasMax'].append(SeasMax)
            pars['SeasMin'].append(SeasMin)
            pars['SeasInt'].append(SeasInt)
            pars['SeasLen'].append(SeasLen)
            pars['SeasAmp'].append(SeasAmp)
            pars['p1'].append(p1)
            pars['p2'].append(p2)
            pars['p3'].append(p3)
            pars['p4'].append(p4)
            pars['p5'].append(p5)
            pars['p6'].append(p6)

            pars['GrowSeas'].append(row['GrowSeas'])
            pars['GrowFit'].append(row['GrowFit'])
            pars['Cell'].append(row['Cell'])
            pars['Index'].append(row['Index'])
            pars['BM'].append(row['BM'])



        dati = pd.DataFrame(data=pars)
        dati.to_csv(path1 + 'MSc/Modelling/GAP_FILLED/Single_VIs/Modelling/runs_check100_final/para_continue/iteration_base' + '_run_' +
                    str(counti + 1) + '.csv',
                    sep=',', index = False)

        # find the median acroos GrowSeas and GrowFit
        aggregrations = {
            'SoS' : lambda x: np.nanmedian(x),
            'EoS' : lambda x: np.nanmedian(x),
            'SeasMax' : lambda x: np.nanmedian(x),
            'SeasMin' : lambda x: np.nanmedian(x),
            'SeasInt' : lambda x: np.nanmedian(x),
            'SeasLen' : lambda x: np.nanmedian(x),
            'SeasAmp' : lambda x: np.nanmedian(x),
            'BM' : lambda x: np.nanmedian(x)
        }

        dati_med = dati.groupby(['Cell', 'Index']).agg(aggregrations)
        dati_med = dati_med.reset_index()

        # split predictors into dfs per Index (
        ndvi = dati_med[dati_med['Index']=='NDVI'].drop(['Index', 'Cell'], axis = 1)
        ndvi.reset_index()
        block = ndvi
        # evi  = dati_med[dati_med['Index']=='EVI'].drop(['Index', 'BM'], axis = 1)
        # nbr  = dati_med[dati_med['Index']=='NBR'].drop(['Index', 'BM'], axis = 1)

        # rename columns
        # ndvi_cols_o = ndvi.columns.values.tolist()
        # ndvi_cols_n = [ndvi_cols_o[0]] + ['NDVI_' + i for i in ndvi_cols_o[1:len(ndvi_cols_o)]]

        # evi_cols_o = evi.columns.values.tolist()
        # evi_cols_n = [evi_cols_o[0]] + ['EVI_' + i for i in evi_cols_o[1:len(evi_cols_o)]]
        #
        # nbr_cols_o = nbr.columns.values.tolist()
        # nbr_cols_n = [nbr_cols_o[0]] + ['NBR_' + i for i in nbr_cols_o[1:len(nbr_cols_o)]]

        # ndvi.rename(columns= dict(zip(ndvi_cols_o, ndvi_cols_n)), inplace= True)
        # evi.rename(columns= dict(zip(evi_cols_o, evi_cols_n)), inplace= True)
        # nbr.rename(columns= dict(zip(nbr_cols_o, nbr_cols_n)), inplace= True)

        # block = pd.merge(ndvi, evi, on='Cell', how='left').\
        #     merge(nbr, on='Cell', how='left').merge(dati_med[['Cell', 'BM']], on='Cell', how='left').\
        #     drop(['Cell'], axis = 1).drop_duplicates()
        # block.reset_index()

        # split into train & test
        x_Train, x_Test, y_Train, y_Test = train_test_split(
            block.iloc[:, np.where((block.columns.values == 'BM') == False)[0]],
            block['BM'], random_state=42, test_size=0.3)

        # set model
        stor = path1 + 'MSc/Modelling/GAP_FILLED/Single_VIs/Modelling/runs_check100_final/sav_continue/'+ 'run_' + str(counti +1) + '.sav'
        ModPerfor(Model(y_Train, x_Train, stor, 58),
                  y_Test, x_Test)

        print(counti)

       # ##### run gbr counti times
if __name__ == '__main__':
    starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print("--------------------------------------------------------")
    print("Starting process, time: " + starttime)
    print("")
    # run model and store performances in results-container
    ModelRunner()

    print("")
    endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print("--------------------------------------------------------")
    print("--------------------------------------------------------")
    print("start: " + starttime)
    print("end: " + endtime)
    print("")

df = pd.DataFrame(data = res)
df.to_csv(path1 + 'MSc/Modelling/GAP_FILLED/Single_VIs/Modelling/runs_check100_final/All100Runs_continue.csv', sep=',', index=False)# then, group by cell & index and then drop growseas and growfit