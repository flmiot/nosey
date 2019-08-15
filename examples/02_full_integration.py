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
p = nosey.DELTA_ImportPolicy()

run1 = nosey.Run(name = 'Run 1')
detector_files  = ['data/pilatus_run_01_0{}.tif'.format(i) for i in range(1,4)]
run1.read(p, detector_files, 'data/run_01.FIO')

run2 = nosey.Run(name = 'Run 2')
detector_files  = ['data/pilatus_run_02_0{}.tif'.format(i) for i in range(1,4)]
run2.read(p, detector_files, 'data/run_02.FIO')

runs = [run1, run2]

# We create four analyzer objects (cf. example 01)
signal = [[0, 23, 487, 37], [0, 40, 487, 45]]
upper_bg = [[0, 9, 487, 23], [0, 9, 487, 23]]
lower_bg = [[0, 37, 487, 51], [0, 37, 487, 51]]
analyzers = []
for ind, s, u, l in zip(range(len(signal)), signal, upper_bg, lower_bg):
    analyzer = nosey.Analyzer('Roi {}'.format(ind))
    analyzer.set_roi(s, 'signal')
    analyzer.set_roi(u, 'upper_bg')
    analyzer.set_roi(l, 'lower_bg')
    analyzers.append(analyzer)

# An analysis object can conveniently handle multiple analyzers and runs.
analysis = nosey.Analysis()
analysis.run(runs = runs, analyzers = analyzers)

# Helper
def plot(result, pos, title = ""):
    ax=plt.subplot(2, 2, pos)
    for scan in zip(*result):
        for a_e, a_i, a_b, a_l in zip(*scan):
            ax.plot(a_e, a_i - a_b, label = a_l)
        ax.title.set_text(title)
        ax.legend()

# Let's try different analysis scenarios.
r = analysis.get_curves(single_scans = False, single_analyzers = False)
plot(r, 1, 'Integrated runs, integrated analyzers')

r = analysis.get_curves(single_scans = False, single_analyzers = True)
plot(r, 2, 'Integrated runs, single analyzers')

r = analysis.get_curves(single_scans = True, single_analyzers = False)
plot(r, 3, 'Single runs, integrated analyzers')

r = analysis.get_curves(single_scans = True, single_analyzers = True)
plot(r, 4, 'Single runs, single analyzers')

plt.show()
