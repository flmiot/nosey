import numpy as np
import scipy.interpolate as interp

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
            b           = fb(ce)
            i, factor   = normalize_curve(ce, fi(ce) - b, window)
            b          *= factor
        else:
            b           = fb(ce)
            i           = fi(ce)
        ii += i
        bg += b

    return ce, ii, bg


def calculateCOM(e, i):
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
