import numpy as np
import math
import matplotlib.pyplot as plt
import scipy.optimize

x_val = np.arange(1985, 2018+1,1)
y_val = np.array([9513, 9513, 9319, 9304, 8771, 8562, 8526, 8514, 8514, 8077, 6806,
      5840, 2177, 2177, 2177, 2177, 2164, 1596, 1596, 1596, 1596, 1596,
      1596, 1596, 1596, 1596, 1470,  620,  610,  591,  591,  591,  591,
       591])

x = np.arange(0,34)

def fsigmoid(x, k, x0): # x0 is wendepunkt,
    return 1.0 / (1.0 + np.exp(-k*(x-x0)))

popt, pcov = scipy.optimize.curve_fit(fsigmoid, x, y_val/10000)

y = fsigmoid(x, popt[0], popt[1])


fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(x, y_val/10000, 'o')
ax.plot(x, y)
ax.plot(np.array([popt[1], popt[1]]), np.array([0.2, 0.8]), '--')
ax.plot(x[1:len(x)], d)