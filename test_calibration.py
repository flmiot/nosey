import os
import numpy as np
import matplotlib.pyplot as plt
import pyqtgraph as pg
from pyqtgraph import QtCore, QtGui
import logging
from nosey.analysis.experiment import Experiment
from nosey.analysis.recipes import DELTARecipe
from nosey.analysis.scan import Scan
from nosey.analysis.analyzer import Analyzer
from nosey.roi import ROI
from nosey.analysis.array import DataArray

experiment = Experiment()

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

fullFiles = [os.path.join(basepath, f) for f in files]
scans = []

images = np.zeros((len(files), 195, 487))
for ind, f in enumerate(fullFiles):
    s = Scan(f, f)
    s.read_files(DELTARecipe())
    scans.append(s)
    images[ind] += s.images[0]

e = [7630, 7640, 7650, 7660, 7670]
roi = [[5, 8, 487, 21], [0, 34, 487, 58]]
analyzers = []
for r in roi:
    a = Analyzer('')
    a.set_roi(r, r_type = 'signal')
    a.auto_calibrate(images, e, sum_before = True, search_radius = 15, outlier_rejection = True)
    analyzers.append(a)

# in_e, out_e, intensity, background, fits = scans[0].get_energy_spectrum(analyzers)
# intensity = np.sum(intensity, axis = 1)


experiment.scans = scans
experiment.analyzers = analyzers
result = experiment.get_spectrum()

ei, ii, bi, l = result.get_curves(False, True)

for scanX, scanY in zip(ei, ii):
    for analyzerX, analyzerY in zip(scanX, scanY):
        plt.plot(analyzerX, analyzerY)
plt.show()

# plt.imshow(scans[0].images[0])
# plt.show()

# app = QtGui.QApplication([])
# imageView = pg.ImageView()
# image = scans[4].images
# imageView.setImage(np.sum(image, axis = 0).T)
#
# class Dummy(object):
#     imageView = imageView
#
# d = Dummy()
# r = ROI([50,5], [487, 25], 'ROI {}'.format(1))
# r.addToMonitor(d)
# for i in range(5):
#     r.addEnergyPoint(i* 10, d)
# images = np.zeros((len(scans),) + scans[0].images[0].shape)
# for ind, scan in enumerate(scans):
#     images[ind] = np.sum(scan.images, axis = 0)
# r.setEnergyPointsAuto(images, imageView, True, 15)
#
#
# imageView.show()
# app.exec_()
