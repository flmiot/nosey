import numpy as np
from timeit import timeit

def f1():
    a = np.ones((1,150,20))
    return np.sum(a)

def f2(d):
    d = {'intensity':d['intensity'][0]}
    return np.sum(d['intensity'])

d = {'intensity': np.ones((10,150,20))}

setup = 'import numpy as np; from __main__ import f1, f2, d'
print(timeit('s = f1()', setup, number = 100000))
print(timeit('s = f2(d)', setup, number = 100000))
