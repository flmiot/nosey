import logging
from pyqtgraph.Qt import QtGui
from nosey.mainframe import MainFrame
from nosey.analysis.experiment import Experiment
from nosey.logbar import StatusBarHandler
from nosey.analysis.recipes import DELTARecipe, SOLEILRecipe

__version__ = '0.1'                     #
lastComputationTime = 0.1               #
recipes = [DELTARecipe, SOLEILRecipe]   # Import modules

# GUI
app = QtGui.QApplication([])
gui = MainFrame()
gui.applySettings()

# Logging
Log = logging.getLogger(__name__)
logging.basicConfig(level = logging.DEBUG)
handler = StatusBarHandler(stream = gui.statusBar)
Log.addHandler(handler)
Log.setLevel(level = logging.DEBUG)

# Memory settings
MAX_NUMBER_ANALYZERS = 72
