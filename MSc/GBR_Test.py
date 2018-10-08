from FloppyToolZ.Funci import *
import pandas as pd
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.externals import joblib
from sklearn import metrics

### read in the data-blocks

path_ns  = 'Z:/_students_data_exchange/FP_FP/Seafile/myLibrary/MSc/Modelling/not_smooth/subsets'
path_sm  = 'Z:/_students_data_exchange/FP_FP/Seafile/myLibrary/MSc/Modelling/smooth/subsets'
path_sm5 = 'Z:/_students_data_exchange/FP_FP/Seafile/myLibrary/MSc/Modelling/smooth5/subsets'

paths = [path_ns, path_sm, path_sm5]

fil   = [getFilelist(path, '.csv') for path in paths]
filp  = [f for fi in fil for f in fi]

test = pd.read_csv(filp[0])
x = test.drop(['Mean_AGB' ,'mean_AGB'], axis=1)
y = test['Mean_AGB']