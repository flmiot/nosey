
from pyqtgraph.Qt import QtGui
from nosey.mainframe import MainFrame
from nosey.logbar import StatusBarHandler
from nosey.analysis.policy import DELTA_ImportPolicy, SOLEIL_ImportPolicy

import logging
__version__ = '0.1'                     #
lastComputationTime = 0.1               #
recipes = [DELTA_ImportPolicy, SOLEIL_ImportPolicy]   # Import modules

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
