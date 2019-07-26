import logging
from pyqtgraph.Qt import QtGui
from nosey.mainframe import MainFrame
from nosey.settings import Settings
from nosey.analysis.experiment import Experiment

app = QtGui.QApplication([])

gui = MainFrame()
gui.applySettings()
Log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
handler = logging.StreamHandler(stream = gui.statusBar)
Log.addHandler(handler)
