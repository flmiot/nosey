import logging
from pyqtgraph.Qt import QtGui
from nosey.mainframe import MainFrame
from nosey.analysis.experiment import Experiment

__version__ = '0.1'

lastComputationTime = 0.1
app = QtGui.QApplication([])

gui = MainFrame()
gui.applySettings()
Log = logging.getLogger(__name__)
logging.basicConfig(level=logging.ERROR)
handler = logging.StreamHandler(stream = gui.statusBar)
Log.addHandler(handler)
