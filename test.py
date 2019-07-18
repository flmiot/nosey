from pyqtgraph.Qt import QtCore, QtGui, uic
from nosey.monitor import Monitor

if __name__ == '__main__':
    app     = QtGui.QApplication([])
    gui     = Monitor()
    gui.show()
    app.exec_()
