import os
import numpy as np
import matplotlib.pyplot as plt
import pyqtgraph as pg
from pyqtgraph import QtCore, QtGui
import logging
from nosey.analysis.policy import DELTA_ImportPolicy
from nosey.analysis.run import Run
from nosey.analysis.analysis import Analysis
from nosey.analysis.analyzer import Analyzer
from timeit import timeit



files = [
    'run08_19_00135_00001.tif',
    'run08_19_00135_00002.tif',
    'run08_19_00135_00003.tif',
    'run08_19_00135_00004.tif',
    'run08_19_00135_00005.tif',
    'run08_19_00135_00006.tif',
    'run08_19_00136_00001.tif',
    'run08_19_00136_00002.tif',
    'run08_19_00136_00003.tif',
    'run08_19_00136_00004.tif',
    'run08_19_00136_00005.tif',
    'run08_19_00136_00006.tif',
    'run08_19_00137_00001.tif',
    'run08_19_00137_00002.tif',
    'run08_19_00137_00003.tif',
    'run08_19_00137_00004.tif',
    'run08_19_00137_00005.tif',
    'run08_19_00137_00006.tif',
    'run08_19_00138_00001.tif',
    'run08_19_00138_00002.tif',
    'run08_19_00138_00003.tif',
    'run08_19_00138_00004.tif',
    'run08_19_00138_00005.tif',
    'run08_19_00138_00006.tif',
    'run08_19_00139_00001.tif',
    'run08_19_00139_00002.tif',
    'run08_19_00139_00003.tif',
    'run08_19_00139_00004.tif',
    'run08_19_00139_00005.tif',
    'run08_19_00139_00006.tif'
    ]

basepath = 'C:/Users/otteflor/Google Drive/Cobalt tautomers - XFEL/XES-BL9 - 05.2019'

fullFiles   = [os.path.join(basepath, f) for f in files]
full_log    = os.path.join(basepath, 'run08_19_00135.FIO')
scans = []

s = Run('Scan')
p = DELTA_ImportPolicy()
s.read(p, files = fullFiles[:6], log_file = full_log)

e = [7630, 7640, 7650, 7660, 7670]
roi = [[5, 8, 487, 21], [0, 34, 487, 58]]
analyzers = []
for r in roi:
    a = Analyzer('')
    a.set_roi(r, r_type = 'signal')
    #a.auto_calibrate(s.images, e, sum_before = True, search_radius = 15, outlier_rejection = True)
    analyzers.append(a)

analysis = Analysis()
analysis.run([s], analyzers)
ei, ii, bi, l = analysis.get_curves(False, True)

for e_s, i_s in zip(ei, ii):
    for e_a, i_a in zip(e_s, i_s):
        plt.plot(e_a, i_a)

plt.show()
