import os
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, uic

from nosey.plot import Plot
from nosey.analysis import AnalysisSetup
from nosey.monitor import Monitor

class MainFrame(QtGui.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        dirname = os.path.dirname(__file__)
        uic.loadUi(os.path.join(dirname, 'ui/mdi.ui'), self)

        self.setupWindow = AnalysisSetup()
        self.mdiArea.addSubWindow(self.setupWindow)
        self.setupWindow.show()

        self.plot = Plot()
        self.mdiArea.addSubWindow(self.plot)
        self.plot.show()



        image = np.ones((4,128,128))
        monitor = Monitor(image)
        self.mdiArea.addSubWindow(monitor)
        monitor.show()

        self.mdiArea.tileSubWindows()


    @QtCore.pyqtSlot()
    def on_actionExit_triggered(self, *args, **kwargs):
        self.close()
