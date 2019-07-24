import logging
from pyqtgraph.Qt import QtGui
from nosey.mainframe import MainFrame
from nosey.analysis.experiment import Experiment

Log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

experiment = Experiment()
app = QtGui.QApplication([])
gui = MainFrame()

handler = logging.StreamHandler(stream = gui.statusBar)
Log.addHandler(handler)
