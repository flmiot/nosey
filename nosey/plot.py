import os
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, uic

class Plot(QtGui.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        dirname = os.path.dirname(__file__)
        uic.loadUi(os.path.join(dirname, 'ui/plot.ui'), self)
