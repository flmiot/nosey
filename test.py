from pyqtgraph.Qt import QtCore, QtGui, uic
from nosey.mdi import MainFrame
from nosey.recipes import DELTARecipe

if __name__ == '__main__':
    app     = QtGui.QApplication([])
    mdi     = MainFrame()
    mdi.show()
    app.exec_()
