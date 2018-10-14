from FloppyToolZ.Funci import *
import uncertainties as unc
from scipy import optimize

# Define the pheno function, the coefficient confidence function and set seed
def funci(x, p1, p2, p3, p4, p5, p6):
    return p1 +p2 * ((1 / (1 + np.exp((p3 - x) / p4))) - (1 / (1 + np.exp((p5 - x) / p6))))

def getCoefConf(para, paracov):
    keys = ['p1l', 'p1','p1u', 'p2l', 'p2', 'p2u', 'p3l', 'p3', 'p3u', 'p4l', 'p4', 'p4u',
            'p5l', 'p5', 'p5u', 'p6l', 'p6', 'p6u']
    vals = [list() for i in range(len(keys))]
    res  = dict(zip(keys, vals))
    if np.isinf(pcov)[0].any():
        pL = [popt[0], popt[0], popt[0], popt[1], popt[1], popt[1], popt[2], popt[2], popt[2], popt[3], popt[3], popt[3],
              popt[4], popt[4], popt[4], popt[5], popt[5], popt[5]]
        for i in range(0, 17, 3):
            res[keys[i]].append(pL[i+1])
            res[keys[i+1]].append(pL[i+1])
            res[keys[i+2]].append(pL[i+1])
        return res
    else:
        p1, p2, p3, p4, p5, p6 = unc.correlated_values(para, paracov)
        pL = [p1, p1, p1, p2, p2, p2, p3, p3, p3, p4, p4, p4, p5, p5, p5, p6, p6, p6]

        for i in range(0, 17, 3):
            res[keys[i]].append(pL[i].nominal_value - pL[i].std_dev * 1.96)
            res[keys[i+1]].append(pL[i+1].nominal_value)
            res[keys[i+2]].append(pL[i+2].nominal_value + pL[i+2].std_dev * 1.96)
        return res

keys = ['GrowSeas', 'GrowFit','Cell', 'Index', 'SoS', 'EoS', 'SeasMax', 'SeasMin', 'SeasInt', 'SeasLen', 'SeasAmp', 'BM',
        'p1l', 'p1', 'p1u', 'p2l', 'p2', 'p2u', 'p3l', 'p3', 'p3u', 'p4l', 'p4', 'p4u',
        'p5l', 'p5', 'p5u', 'p6l', 'p6', 'p6u'
        ]
vals = [list() for i in range(len(keys))]
res  = dict(zip(keys, vals))

np.random.seed(42)

dummy = np.arange(1,366,1)

smooth  = getFilelist('/home/florus/MSc/Modelling/for_python/smooth', '.csv')
# smooth5 = getFilelist('/home/florus/MSc/Modelling/for_python/smooth5', '.csv')
# no_smot = getFilelist('/home/florus/MSc/Modelling/for_python/not_smooth', '.csv')

indi  = ['NDVI', 'EVI', 'NBR']

for file in smooth:
        blo   = pd.read_csv(file)
        cells = blo['Cell'].unique()

        for i, cell in enumerate(cells):
            for ind in indi:

                sub = blo.iloc[np.where(blo['Cell'] == cell)[0]]

                res['GrowSeas'].append(file.split('/')[-1][3:7])
                res['GrowFit'].append(file.split('_')[2])

                # fit the function
                popt, pcov = optimize.curve_fit(funci,
                                                sub['AccDate'], sub[ind], p0=[0.1023, 0.8802, 108.2, 7.596, 311.4, 7.473],
                                                maxfev=100000000)
                parm = getCoefConf(popt, pcov)
                # apply the function
                pred = funci(dummy,parm['p1'], parm['p2'], parm['p3'], parm['p4'], parm['p5'], parm['p6'])

                # calc season parameter
                dev1 = np.diff(pred)
                SoS  = np.argmax(dev1) + 1
                EoS  = np.argmin(dev1) + 1
                SeasMax = round(max(pred),2)
                SeasMin = round(min(pred),2)
                SeasInt = round(np.trapz(funci(np.arange(SoS, EoS+1, 1),
                           parm['p1'], parm['p2'], parm['p3'], parm['p4'], parm['p5'], parm['p6'])), 2)
                SeasLen = EoS - SoS
                SeasAmp = SeasMax - SeasMin

                # fill up res
                res['Cell'].append(cell)
                res['Index'].append(ind)
                res['SoS'].append(SoS)
                res['EoS'].append(EoS)
                res['SeasMax'].append(SeasMax)
                res['SeasMin'].append(SeasMin)
                res['SeasInt'].append(SeasInt)
                res['SeasLen'].append(SeasLen)
                res['SeasAmp'].append(SeasAmp)
                res['BM'].append(np.unique(sub['Mean_AGB'])[0])
                res['p1l'].append(parm['p1l'][0])
                res['p1'].append(parm['p1'][0])
                res['p1u'].append(parm['p1u'][0])
                res['p2l'].append(parm['p2l'][0])
                res['p2'].append(parm['p2'][0])
                res['p2u'].append(parm['p2u'][0])
                res['p3l'].append(parm['p3l'][0])
                res['p3'].append(parm['p3'][0])
                res['p3u'].append(parm['p3u'][0])
                res['p4l'].append(parm['p4l'][0])
                res['p4'].append(parm['p4'][0])
                res['p4u'].append(parm['p4u'][0])
                res['p5l'].append(parm['p5l'][0])
                res['p5'].append(parm['p5'][0])
                res['p5u'].append(parm['p5u'][0])
                res['p6l'].append(parm['p6l'][0])
                res['p6'].append(parm['p6'][0])
                res['p6u'].append(parm['p6u'][0])

                print(i)

        df = pd.DataFrame(data=res)
        df.to_csv('/home/florus/Seafile/myLibrary/MSc/Modelling/test.csv', sep=',', index=False)



        #
        #
        # plt.plot(dummy,
        #          funci(dummy,parm['p1'], parm['p2'], parm['p3'], parm['p4'], parm['p5'], parm['p6']))
        #
        #
        #
        #
        #
        # def Fit(x, y ):
        #     DOY = x
        #     NDVI = y
        #     init = np.array([0.1023, 0.8802, 108.2, 7.596, 311.4, 7.473])
        #     # Jetzt die FitFunktion --> musst du an deine Funktion anpassen!
        #     fitfunc = lambda p, DOY: p[0] +p[1] * ((1 / (1 + np.exp((p[2] - x) / p[3]))) - (1 / (1 + np.exp((p[4] - x) / p[5]))))
        #     errfunc = lambda p, DOY, NDVI: fitfunc(p, DOY) - NDVI
        #     p1, success = optimize.leastsq(errfunc, init, args=(DOY, NDVI),maxfev=100000000)
        #     return p1
        #
        # Fit(xdata,ydata)