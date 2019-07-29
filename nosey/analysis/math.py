import numpy as np

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
