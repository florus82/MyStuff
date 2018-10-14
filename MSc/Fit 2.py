import numpy as np
import pandas as pd

def funci(x, p1, p2, p3, p4, p5, p6):
    return p1 +p2 * ((1 / (1 + np.exp((p3 - x) / p4))) - (1 / (1 + np.exp((p5 - x) / p6))))


dat   = pd.read_csv('/home/florus/Seafile/myLibrary/MSc/Modelling/test.csv')
dummy = np.array([i for i in range(1, 366, 1)])

# make a seasparm container
keys = ['GrowSeas', 'GrowFit', 'Cell', 'Index', 'SoS', 'EoS', 'SeasMax',
       'SeasMin', 'SeasInt', 'SeasLen', 'SeasAmp', 'BM']
vals = [list() for i in range(len(keys))]
pars = dict(zip(keys, vals))

# make parameter & rmse container
keys = ['rmse', 'p1', 'p2', 'p3', 'p4', 'p5', 'p6']
vals = [list() for i in range(len(keys))]
res  = dict(zip(keys, vals))



for index, row in dat.iterrows():

    pars['GrowSeas'].append(row['GrowSeas'])
    pars['GrowFit'].append(row['GrowFit'])
    pars['Cell'].append(row['Cell'])
    pars['Index'].append(row['Index'])
    pars['BM'].append(row['BM'])

    p1 = np.random.sample() * (row['p1u'] - row['p1l']) + row['p1l']
    p2 = np.random.sample() * (row['p2u'] - row['p2l']) + row['p2l']
    p3 = np.random.sample() * (row['p3u'] - row['p3l']) + row['p3l']
    p4 = np.random.sample() * (row['p4u'] - row['p4l']) + row['p4l']
    p5 = np.random.sample() * (row['p5u'] - row['p5l']) + row['p5l']
    p6 = np.random.sample() * (row['p6u'] - row['p6l']) + row['p6l']

    pred = funci(dummy, p1, p2, p3, p4, p5, p6)

    dev1 = np.diff(pred)
    SoS = np.argmax(dev1) + 1
    EoS = np.argmin(dev1) + 1
    SeasMax = round(max(pred), 2)
    SeasMin = round(min(pred), 2)
    SeasInt = round(np.trapz(funci(np.arange(SoS, EoS + 1, 1),
                                p1, p2, p3, p4, p5, p6)), 2)
    SeasLen = EoS - SoS
    SeasAmp = SeasMax - SeasMin

    pars['SoS'].append(SoS)
    pars['EoS'].append(EoS)
    pars['SeasMax'].append(SeasMax)
    pars['SeasMin'].append(SeasMin)
    pars['SeasInt'].append(SeasInt)
    pars['SeasLen'].append(SeasLen)
    pars['SeasAmp'].append(SeasAmp)

dati = pd.DataFrame(data=pars)
dati.to_csv('/home/florus/Seafile/myLibrary/MSc/Modelling/iteration' +  + '.csv', sep=',', index = False)

# first, join growseas --> 2007+2012, 2006+2011, 2005+2010; probably not necessary as cells are unique already!!!!!!!!!!!!!!!!!
# then, group by cell & index and then drop growseas and growfit