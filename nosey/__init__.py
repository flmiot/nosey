import logging
from pyqtgraph.Qt import QtGui
from nosey.mainframe import MainFrame
from nosey.analysis.experiment import Experiment
from nosey.logbar import StatusBarHandler
from nosey.analysis.policy import PETRA

__version__ = '0.1'                      #
lastComputationTime = 0.01               #
recipes = [PETRA]   # Import modules

# GUI
app = QtGui.QApplication([])
gui = MainFrame()
gui.applySettings()

# Logging
Log = logging.getLogger(__name__)
handler = StatusBarHandler(stream=gui.statusBar)
Log.addHandler(handler)
Log.setLevel(level=logging.INFO)
