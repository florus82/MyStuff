from FloppyToolZ.Funci import *
import pandas as pd
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.externals import joblib
from sklearn import metrics

# #### create master file list for pred/resp sets
p1 = '/home/florus/'
# p2 = 'Z:/_students_data_exchange/FP_FP/Seafile/myLibrary/' # Geoserv2

path_ns  = p1 + 'MSc/Modelling/not_smooth/subsets'
path_sm  = p1 + 'MSc/Modelling/smooth/subsets'
path_sm5 = p1 + 'MSc/Modelling/smooth5/subsets'

paths = [path_ns, path_sm, path_sm5]

fil   = [getFilelist(path, '.csv') for path in paths]
filp  = [f for fi in fil for f in fi]

# #### read in column names for different pred-sets (seasPAr, seasFit, seasStat)
c_fil  = getFilelist('/home/florus/MSc/Modelling/colnames', '.csv')
c_seasPar  = pd.read_csv(c_fil[2])
c_seasFit  = pd.read_csv(c_fil[1])
c_seasStat = pd.read_csv(c_fil[0])

c_seasPar  = c_seasPar[c_seasPar.columns.values[0]].values.tolist()
c_seasFit  = c_seasFit[c_seasFit.columns.values[0]].values.tolist()
c_seasStat = c_seasStat[c_seasStat.columns.values[0]].values.tolist()

# #### read in the data-blocks and seperate into train & test

dat        = pd.read_csv(filp[0])

# response
y_dat      = dat['Mean_AGB']

# pred-sets
x_seasPar  = dat[c_seasPar]
x_seasFit  = dat[c_seasFit]
x_seasStat = dat[c_seasStat]

x_seasPar_Train, x_seasPar_Test, y_seasPar_Train, y_seasPar_Test     = train_test_split(x_seasPar, y_dat, random_state= 42, test_size = 0.3)
x_seasFit_Train, x_seasFit_Test, y_seasFit_Train, y_seasFit_Test     = train_test_split(x_seasFit, y_dat, random_state= 42, test_size = 0.3)
x_seasStat_Train, x_seasStat_Test, y_seasStat_Train, y_seasStat_Test = train_test_split(x_seasStat, y_dat, random_state= 42, test_size = 0.3)


# #### funcitons needed
# grid search
def Model(yValues, predictors, CVout, nCores):
    param_grid = {'learning_rate': [0.1, 0.05, 0.02, 0.01, 0.005, 0.002, 0.001],
                  'max_depth': [4, 6],
                  'min_samples_leaf': [3, 5, 9, 17],
                  'max_features': [1.0, 0.5, 0.3, 0.1]}
    est = GradientBoostingRegressor(n_estimators=7500)
    gs_cv = GridSearchCV(est, param_grid, cv=5, refit=True, n_jobs=nCores) \
        .fit(predictors, yValues)
    # Write outputs to disk and return elements from function
    joblib.dump(gs_cv, CVout)
    return (gs_cv)

# model performance
 def ModPerfor(cv_results, yData, xData): # cv_results is the output from Model
        # Produce pandas-table entailing all model-parameterizations
        cv_scoreTable = cv_results.cv_results_
        cv_scoreTable_pd = pd.DataFrame(cv_scoreTable)
        # Get parameters from the best estimator
        md = cv_results.best_params_['max_depth']
        lr = cv_results.best_params_['learning_rate']
        msl = cv_results.best_params_['min_samples_leaf']
        mf = cv_results.best_params_['max_features']
        # Calculate Predictions of the true values
        y_true, y_pred = yData, cv_results.predict(xData)
        # plt.scatter(y_true, y_pred, color='black')
        # plt.show()
        # Extract R2 and MSE
        R2 = metrics.r2_score(y_true, y_pred)
        mse = metrics.mean_squared_error(y_true, y_pred)
        # print(R2, mse)
        # merge y_true, y_pred into pandas table
        corr_table = pd.DataFrame({'y_True': y_true, 'y_pred': y_pred})
        # print(corr_table[1:5])
        return [R2, mse, md, lr, msl, mf, corr_table]



# ##### run gbr once
# if __name__ == '__main__': # only needed for stupid windows
a = Model(y_seasFit_Train, x_seasFit_Train, ('/home/florus/MSc/Modelling/', 2)
# make overview table
### run gbr 1000 times


# make overview table












































cc = list(test.columns.values)
k1 = ['seasPar']
k2 = ['seasFit']
k3 = ['seasStat']
v1 = [cc[3:30]]
v2 = [cc[30:1125]]
v3 = [cc[1127:1172]]

d1 = dict(zip(k1, v1))
d2 = dict(zip(k2, v2))
d3 = dict(zip(k3, v3))

df1 = pd.DataFrame(data=d1)
df2 = pd.DataFrame(data=d2)
df3 = pd.DataFrame(data=d3)

df1.to_csv('/home/florus/MSc/Modelling/colnames/seasPar.csv', sep=',',index=False)
df2.to_csv('/home/florus/MSc/Modelling/colnames/seasFit.csv', sep=',',index=False)
df3.to_csv('/home/florus/MSc/Modelling/colnames/seasStat.csv', sep=',',index=False)
