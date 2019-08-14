""" Simple integration: Demonstration of Analyzer and Run objects in NOSEY.

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

# Create a new run object. A run (scan, acquisition, ...) holds a set of images
run = nosey.Run(name = 'A demo run')

# We tell NOSEY how to import data with an import policy. Here, we can use a
# built-in policy, but it is easy to create our own. See policy example.
p = nosey.DELTA_ImportPolicy()

# Reading the image files is really easy now:
detector_files  = ['data/pilatus_0{}.tif'.format(i) for i in range(1,4)]
run.read(p, detector_files, 'data/logfile.FIO')

# We create an analyzer. Analyzer objects hold regions-of-interest (ROI)
analyzer = nosey.Analyzer(name = 'Demo analyzer')
analyzer.set_roi([0, 23, 487, 37], 'signal')    # Main signal ROI
analyzer.set_roi([0, 9, 487, 23], 'upper_bg')   # Upper background ROI (opt)
analyzer.set_roi([0, 37, 487, 51], 'lower_bg')  # Lower background ROI (opt)

# We get the integrated spectrum by calling get_energy_spectrum with analyzers
ie, oe, ii, er, bg, er_bg, f = run.get_energy_spectrum( [analyzer] )

# Side by side: Detector images and integrated spectrum
plt.figure(1)
plt.imshow(np.sum(run.images, axis = 0))
plt.title(run)

plt.figure(2)
err = er[0,0] + er_bg[0,0]
y = ii[0,0] - bg[0,0]
plt.plot(oe[0], y)
plt.fill_between(oe[0], y - err, y + err, color='blue', alpha=0.2)
plt.title(analyzer)
plt.show()
