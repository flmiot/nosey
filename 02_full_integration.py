""" Full integration: Demonstration of multiple analyzer integration in NOSEY.

    Info:
        We'll use real detector data in the '/data' folder

        Since this example is working on real data, you'll need the
        "tifffile"-package.

        Within an Anaconda shell "tifffile" can be installed by typing
        'conda install -c conda-forge tifffile'
"""
import numpy as np
import matplotlib.pyplot as plt

import nosey

# We start by importing detector data (cf. example 01)
run = nosey.Run(name = 'A demo run')
p = nosey.DELTA_ImportPolicy()
detector_files  = ['data/pilatus_0{}.tif'.format(i) for i in range(1,4)]
run.read(p, detector_files, 'data/logfile.FIO')

# We create four analyzer objects (cf. example 01)
signal = [[0, 23, 487, 37]]
upper_bg = [[0, 9, 487, 23]]
lower_bg = [[0, 37, 487, 51]]
analyzers = []
for s, u, l in zip(signal, upper_bg, lower_bg):
    analyzer = nosey.Analyzer()
    analyzer.set_roi(s, 'signal')
    analyzer.set_roi(u, 'upper_bg')
    analyzer.set_roi(l, 'lower_bg')
    analyzers.append(analyzer)

# An analysis object can conveniently handle multiple analyzers and runs.
analyis = nosey.Analysis()
analyis.run(runs = [run], analyzers = analyzers)

# Let's try different analysis scenarios.
ei, ii, bi, l = analyis.get_curves(single_scans = False, single_analyzers = True)
ei, ii, bi, l = analyis.get_curves(single_scans = False, single_analyzers = False)
ei, ii, bi, l = analyis.get_curves(single_scans = False, single_analyzers = False, sum_steps = False)
ei, ii, bi, l = analyis.get_curves(single_scans = False, single_analyzers = False, poly_order = 9)
