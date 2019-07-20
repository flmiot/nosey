from pyqtgraph.Qt import QtCore, QtGui, uic

from nosey.mainframe import MainFrame

if __name__ == '__main__':
    app     = QtGui.QApplication([])
    mdi     = MainFrame()
    mdi.show()
    app.exec_()
