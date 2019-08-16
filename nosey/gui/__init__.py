from pyqtgraph.Qt import QtGui
from nosey.gui.mainframe import MainFrame
from nosey.gui.logbar import StatusBarHandler
from nosey.policy import DELTA_ImportPolicy, SOLEIL_ImportPolicy


# GUI
app = QtGui.QApplication([])
gui = MainFrame()
gui.applySettings()

# Logging
handler = StatusBarHandler(stream = gui.statusBar)
nosey.Log.addHandler(handler)
nosey.Log.setLevel(level = logging.DEBUG)
