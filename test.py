from pyqtgraph.Qt import QtCore, QtGui, uic
from nosey.monitor import Monitor
from nosey.recipes import DELTARecipe

import os
path = 'C:/Users/hambu/Desktop/run08_19_xes_otte_local'
files = [f for f in sorted(os.listdir(path)) if '_00153_' in f]
files = [os.path.join(path, f) for f in files]

r = DELTARecipe()
image = r.getImages(files)

if __name__ == '__main__':
    app     = QtGui.QApplication([])
    gui     = Monitor(image)
    gui.show()
    app.exec_()
