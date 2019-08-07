import numpy as np
import scipy.interpolate as interp
import scipy.optimize as optim

import matplotlib.pyplot as plt

def normalize_curve(e, i, window = None):
    """Return normalized curve and factor by which curve was scaled."""
    if window is not None:
        w0 = window[0]
        w1 = window[1]
        ind0 = np.argmin(np.abs(e - w0))
        ind1 = np.argmin(np.abs(e - w1))
    else:
        ind0 = 0
        ind1 = len(i)

    if ind1 - ind0 < 1 or min(ind0, ind1) < 0:
        raise Exception("Invalid normalization window")

    weight = np.sum(i[ind0:ind1])
    factor = np.abs(1 / weight) * 1000.
    return i * factor, factor


def fit_curve(i, order = 3):
    x   = np.arange(len(i))
    p   = np.polyfit(x, i, order)
    poly = np.poly1d(p)
    return poly(x)


def interpolate_and_sum(energy, intensity, background, normalize_before_sum = False, window = None):
    min_energy = np.max(list(np.min(e) for e in energy))
    max_energy = np.min(list(np.max(e) for e in energy))

    points = np.max(list([len(i) for i in intensity]))
    ii = np.zeros(points, dtype = np.float)
    bg = np.zeros(points, dtype = np.float)
    ce = np.linspace(min_energy, max_energy, points)

    for e, i, b in zip(energy, intensity, background):

        fi = interp.interp1d(e, i)
        fb = interp.interp1d(e, b)
        if normalize_before_sum:
            i, factor   = normalize_curve(ce, fi(ce) - fb(ce), window)
            b          *= factor
        else:
            b           = fb(ce)
            i           = fi(ce)
        ii += i
        bg += b

    return ce, ii, bg


def calculateCOM(e, i, window = None):

    if window is not None:
        e0, e1  = window
        i0, i1  = np.argmin(np.abs(e-e0)), np.argmin(np.abs(e-e1))
        i, e    = i[i0:i1], e[i0:i1]

    cumsum = np.cumsum(i)
    f = interp.interp1d(cumsum, e)
    return float(f(0.5*np.max(cumsum)))


def integratedAbsoluteDifference(e0, i0, e1, i1, windowNorm, windowCOM):
    com_shift           = self._calculateCOM(er, ir) - self._calculateCOM(e, i)
    e                  += com_shift
    e, i, b             = interpolate_and_sum([er, e], [-1 * ir, i], windowNorm)
    if windowCOM is None:
        iad                 = np.sum(np.abs(i))
    else:
        ind0                = np.argmin(np.abs(e - windowCOM[0]))
        ind1                = np.argmin(np.abs(e - windowCOM[1]))
        iad                 = np.sum(np.abs(i[ind0:ind1]))
    return iad


def fractionFit(data, ref_a, ref_b):

    # Interpolate
    f_data              = interp.interp1d(data[0], data[1])
    f_ref_a             = interp.interp1d(ref_a[0], ref_a[1])
    f_ref_b             = interp.interp1d(ref_b[0], ref_b[1])
    energy, intensity   = zip(data, ref_a, ref_b)
    min_energy          = np.max(list(np.min(e) for e in energy))
    max_energy          = np.min(list(np.max(e) for e in energy))
    points              = np.max(list([len(i) for i in intensity]))
    ce                  = np.linspace(min_energy, max_energy, points)

    def modelFunction(energy, f):
        return f * f_ref_a(energy) + (1-f)*f_ref_b(energy)


    fit_data    = ce, f_data(ce)
    popt, pcov  = optim.curve_fit(modelFunction, *fit_data, bounds = (0,1))
    f           = lambda e : modelFunction(e, popt[0])

    # Compute sum of squared residuals (SQR)
    sqr = np.sum((f(ce) - f_data(ce))**2)
    print(sqr, pcov)

    return popt[0], ce, lambda e : modelFunction(e, popt[0])


def getOutliers(image, threshold = 0.1):
    image = np.abs(image)
    differences = {}
    differences['east']     = image - np.roll(image, -1, axis = 1)
    differences['south']    = image - np.roll(image, -1, axis = 0)
    differences['west']     = image - np.roll(image, 1, axis = 1)
    differences['north']    = image - np.roll(image, 1, axis = 0)

    outliers = []
    for shift in ['east', 'south', 'west', 'north']:
        tval = np.max(differences[shift]) * threshold
        o = np.where(differences[shift] > tval)
        for y, x in zip(*o):
            if shift is 'east':
                if x == 0:
                    continue

            elif shift is 'south':
                if y == 0:
                    continue

            elif shift is 'west':
                if x == image.shape[1] - 1:
                    continue

            else:
                if y == image.shape[0] - 1:
                    continue

            if not [x,y] in outliers:
                outliers.append([x,y])

    return outliers
